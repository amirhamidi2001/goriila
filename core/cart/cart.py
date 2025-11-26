from decimal import Decimal
from typing import Dict, List, Optional

from django.db import transaction
from django.db.models import F
from shop.models import Product
from cart.models import Cart, CartItem


class CartSession:
    """
    Refactored CartSession:
    - keeps session structure identical: {"items": [{"product_id": "...", "quantity": n}, ...]}
    - reduces DB queries by batching Product queries
    - minimizes session writes (save() called only on real changes)
    - uses Decimal for monetary calculations (assumes Product.price/get_price return Decimal)
    """

    SESSION_KEY = "cart"

    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault(self.SESSION_KEY, {"items": []})
        # internal caches (per-instance; reset each request/new CartSession instance)
        self._modified = False
        self._product_cache: Dict[str, Product] = {}
        self._products_loaded_for_items = False

    # ---------- Helpers ----------
    def _save_marked(self):
        if self._modified:
            self.save()
            self._modified = False

    def save(self):
        """Mark session modified so Django saves it."""
        self.session.modified = True

    def _mark_modified(self):
        self._modified = True

    def _normalize_pid(self, pid) -> str:
        """Ensure product_id is stored as string to be compatible with existing session usage."""
        return str(pid)

    def _ensure_cart_items_list(self) -> List[Dict]:
        if "items" not in self._cart or not isinstance(self._cart["items"], list):
            self._cart["items"] = []
            self._mark_modified()
        return self._cart["items"]

    def _load_products_for_items(self):
        """
        Batch load Product objects for the product_ids present in the session items.
        Caches results in self._product_cache keyed by string id.
        """
        if self._products_loaded_for_items:
            return

        items = self._ensure_cart_items_list()
        if not items:
            self._products_loaded_for_items = True
            return

        product_ids = [int(item["product_id"]) for item in items]
        products = Product.objects.filter(id__in=product_ids, available=True)
        self._product_cache = {str(p.id): p for p in products}
        self._products_loaded_for_items = True

    def _get_product(self, product_id) -> Optional[Product]:
        """
        Return Product instance or None if not available.
        Uses cache if available; single-get fallback if not present in cache.
        """
        pid = self._normalize_pid(product_id)
        if pid in self._product_cache:
            return self._product_cache[pid]

        try:
            p = Product.objects.get(id=pid, available=True)
        except Product.DoesNotExist:
            return None
        self._product_cache[pid] = p
        return p

    def _build_item_index(self) -> Dict[str, Dict]:
        """
        Build a temporary index mapping product_id -> item dict (not persisted).
        This allows O(1) lookups while keeping the session structure (list) unchanged.
        """
        items = self._ensure_cart_items_list()
        return {item["product_id"]: item for item in items}

    # ---------- Mutating operations ----------
    def add_product(self, product_id) -> bool:
        """
        Add product by id (increment if exists).
        Returns True if added/incremented, False on stock unavailable or product not available.
        """
        pid = self._normalize_pid(product_id)
        product = self._get_product(pid)
        if product is None:
            return False

        items = self._ensure_cart_items_list()
        index = self._build_item_index()

        existing = index.get(pid)
        if existing:
            if existing["quantity"] + 1 > product.stock:
                return False
            existing["quantity"] += 1
            self._mark_modified()
        else:
            if product.stock < 1:
                return False
            items.append({"product_id": pid, "quantity": 1})
            self._mark_modified()

        self._save_marked()
        return True

    def update_product_quantity(self, product_id, quantity):
        """
        Set quantity (int). If quantity is same as before, no session write.
        If product doesn't exist in cart, no-op.
        """
        pid = self._normalize_pid(product_id)
        try:
            new_q = int(quantity)
        except (TypeError, ValueError):
            return

        items = self._ensure_cart_items_list()
        for item in items:
            if item["product_id"] == pid:
                if item["quantity"] != new_q:
                    item["quantity"] = new_q
                    self._mark_modified()
                break
        self._save_marked()

    def decrease_product_quantity(self, product_id) -> bool:
        """
        Decrease quantity by 1 if >1. Returns True if decreased, False otherwise.
        """
        pid = self._normalize_pid(product_id)
        items = self._ensure_cart_items_list()
        for item in items:
            if item["product_id"] == pid:
                if item["quantity"] > 1:
                    item["quantity"] -= 1
                    self._mark_modified()
                    self._save_marked()
                    return True
                return False
        return False

    def remove_product(self, product_id):
        """
        Remove item from session cart if present.
        """
        pid = self._normalize_pid(product_id)
        items = self._ensure_cart_items_list()
        for item in list(items):  # iterate over copy to safely remove
            if item["product_id"] == pid:
                items.remove(item)
                self._mark_modified()
                break
        self._save_marked()

    def clear(self):
        """
        Clear cart in session.
        """
        self._cart = self.session[self.SESSION_KEY] = {"items": []}
        self._product_cache = {}
        self._products_loaded_for_items = True
        self._mark_modified()
        self._save_marked()

    # ---------- Read operations (use batch product loads) ----------
    def get_cart_dict(self) -> Dict:
        """
        Return the raw cart dict (same structure as stored in session).
        """
        return self._cart

    def get_cart_items(self) -> List[Dict]:
        """
        Return list of cart items augmented with:
          - "product_obj": Product instance
          - "total_price": quantity * product.get_price()
          - "total_discount": quantity * (price_without_discount - price_with_discount)
        NOTE: This mutates the session items in-memory (adds keys) but preserves product_id/quantity shape
        as stored in session (so existing frontend JSON remains compatible).
        """
        items = self._ensure_cart_items_list()
        self._load_products_for_items()

        # iterate and update; items that have missing product (not available) will be skipped
        for item in items:
            pid = item["product_id"]
            product_obj = self._product_cache.get(pid)
            if not product_obj:
                # Try fetching once more (in case not loaded via batch)
                product_obj = self._get_product(pid)
                if not product_obj:
                    # product not available -> skip populating fields (frontend should handle missing product_obj)
                    item.pop("product_obj", None)
                    item.pop("total_price", None)
                    item.pop("total_discount", None)
                    continue

            # use Decimal arithmetic; assume product.price and product.get_price() are Decimal
            price_without_discount = getattr(product_obj, "price", Decimal("0"))
            price_with_discount = getattr(
                product_obj, "get_price", lambda: price_without_discount
            )()
            # ensure Decimal
            if not isinstance(price_without_discount, Decimal):
                price_without_discount = Decimal(price_without_discount)
            if not isinstance(price_with_discount, Decimal):
                price_with_discount = Decimal(price_with_discount)

            discount_amount_per_unit = price_without_discount - price_with_discount
            quantity = int(item.get("quantity", 0))

            item.update(
                {
                    "product_obj": product_obj,
                    "total_price": price_with_discount * quantity,
                    "total_discount": discount_amount_per_unit * quantity,
                }
            )

        return items

    def get_total_weight(self) -> int:
        """
        Sum of product.weight * quantity. If weight is non-int or missing, treat as 0.
        """
        total_weight = 0
        items = self._ensure_cart_items_list()
        self._load_products_for_items()

        for item in items:
            pid = item["product_id"]
            product = self._product_cache.get(pid) or self._get_product(pid)
            if not product:
                continue
            try:
                weight = int(product.weight)
            except Exception:
                weight = 0
            total_weight += weight * int(item.get("quantity", 0))

        return total_weight

    def get_shipping_cost(self) -> Decimal:
        """
        Example shipping calculation: weight * 100
        Returns Decimal for consistency.
        """
        total_weight = self.get_total_weight()
        return Decimal(total_weight) * Decimal(100)

    def get_total_price(self) -> Decimal:
        """
        Sum total_price from cart items. If get_cart_items() hasn't been called before,
        total_price values may be missing — call get_cart_items() to ensure totals are present.
        """
        # Make sure item totals exist
        items = self.get_cart_items()
        total = Decimal("0")
        for item in items:
            tp = item.get("total_price", Decimal("0"))
            if not isinstance(tp, Decimal):
                tp = Decimal(tp)
            total += tp
        return total

    def get_total_quantity(self) -> int:
        items = self._ensure_cart_items_list()
        return sum(int(item.get("quantity", 0)) for item in items)

    def get_total_discount_amount(self) -> Decimal:
        """
        Ensure cart items are annotated so discount fields exist.
        """
        items = self.get_cart_items()
        total = Decimal("0")
        for item in items:
            td = item.get("total_discount", Decimal("0"))
            if not isinstance(td, Decimal):
                td = Decimal(td)
            total += td
        return total

    def get_total_payment_amount(self) -> Decimal:
        items_total = self.get_total_price()
        shipping = self.get_shipping_cost()
        return items_total + shipping

    # ---------- Sync / Merge with DB (optimized) ----------
    def sync_cart_items_from_db(self, user):
        """
        Load CartItem for user and merge into session cart items:
        - for matching items, update session quantity from DB item
        - for DB items missing in session, append them to session
        Then call merge_session_cart_in_db to ensure DB matches session (preserve original behavior).
        """
        if not user or user.is_anonymous:
            return

        # ensure session list
        items = self._ensure_cart_items_list()
        session_index = self._build_item_index()

        cart, _ = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart).select_related("product")

        for c_item in cart_items:
            pid = self._normalize_pid(c_item.product.id)
            if pid in session_index:
                # update DB -> session (behavior preserved)
                session_index[pid]["quantity"] = c_item.quantity
                self._mark_modified()
            else:
                items.append({"product_id": pid, "quantity": c_item.quantity})
                self._mark_modified()

        # After syncing, ensure DB and session consistent (call merge to remove stale DB items)
        self.merge_session_cart_in_db(user)
        self._save_marked()

    def merge_session_cart_in_db(self, user):
        """
        Merge session cart items into DB cart for the given user.
        Optimized:
          - fetch all products for items (batch)
          - fetch existing CartItem objects for cart (one query)
          - bulk_create new CartItem objects
          - bulk_update changed quantities
          - delete CartItems not in session
        Behavior preserved: final DB state equals session state.
        """
        if not user or user.is_anonymous:
            return

        items = self._ensure_cart_items_list()
        if not items:
            # if session empty -> delete all cart items for user
            cart, _ = Cart.objects.get_or_create(user=user)
            CartItem.objects.filter(cart=cart).delete()
            return

        # Normalize product ids and batch load products
        session_product_ids = [
            int(self._normalize_pid(item["product_id"])) for item in items
        ]
        products = Product.objects.filter(id__in=session_product_ids, available=True)
        product_map = {p.id: p for p in products}
        # Build session map keyed by product_id int
        session_map = {}
        for item in items:
            try:
                pid_int = int(item["product_id"])
            except Exception:
                continue
            session_map[pid_int] = int(item.get("quantity", 0))

        cart, _ = Cart.objects.get_or_create(user=user)
        existing_qs = CartItem.objects.filter(cart=cart).select_related("product")
        existing_map = {ci.product.id: ci for ci in existing_qs}

        to_create = []
        to_update = []
        now_product_ids = set(session_map.keys())

        # Prepare creates and updates
        for pid, qty in session_map.items():
            product_obj = product_map.get(pid)
            if not product_obj:
                # product not available -> skip (preserves behavior of ignoring unavailable)
                continue
            existing_ci = existing_map.get(pid)
            if existing_ci:
                if existing_ci.quantity != qty:
                    existing_ci.quantity = qty
                    to_update.append(existing_ci)
            else:
                to_create.append(CartItem(cart=cart, product=product_obj, quantity=qty))

        # Perform DB writes in transaction
        with transaction.atomic():
            if to_create:
                CartItem.objects.bulk_create(to_create)
            if to_update:
                # bulk_update needs fields list
                CartItem.objects.bulk_update(to_update, ["quantity"])
            # remove cart items not present in session
            if existing_map:
                existing_product_ids = set(existing_map.keys())
                remove_ids = existing_product_ids - now_product_ids
                if remove_ids:
                    CartItem.objects.filter(
                        cart=cart, product__id__in=remove_ids
                    ).delete()

    # End of class
