import uuid
from typing import Dict, List, Union
from .models import Product, Category, StockTransaction, TransactionType
from .notifiers import Notifier


class InventoryService:
    """บริการจัดการสต็อกสินค้า คํานวณมูลค่า และส่งการแจ้งเตือน"""

    def __init__(self, notifiers: List[Notifier] = None) -> None:
        """กําหนดค่าเริ่มต้นสําหรับบริการคลังสินค้าพร้อมรองรับ Dependency Injection"""
        self.products: Dict[str, Product] = {}
        self.categories: Dict[str, Category] = {}
        self.transactions: List[StockTransaction] = []
        self.notifiers: List[Notifier] = notifiers if notifiers is not None else []

    def add_category(self, category: Category) -> None:
        """เพิ่มหมวดหมู่สินค้าใหม่เข้าสู่ระบบ"""
        self.categories[category.id] = category

    def add_product(self, product: Product) -> None:
        """เพิ่มสินค้าใหม่เข้าสู่ระบบ"""
        self.products[product.id] = product

    def _notify_all(self, message: str) -> None:
        """ส่งข้อความไปยังผู้แจ้งเตือนทุกช่องทางในระบบ"""
        for notifier in self.notifiers:
            notifier.send(message)

    def receive_stock(self, product_id: str, quantity: int) -> Product:
        """บันทึกการรับสินค้าเข้าสต็อก และแจ้งเตือนสถานะเมื่ออัปเดต"""
        if product_id not in self.products:
            raise KeyError("ไม่พบสินค้าในระบบ")
        if quantity <= 0:
            raise ValueError("จำนวนสินค้าที่รับเข้าต้องมากกว่า 0")

        product = self.products[product_id]
        product.quantity += quantity

        transaction = StockTransaction(
            id=str(uuid.uuid4()),
            product_id=product_id,
            transaction_type=TransactionType.IN,
            quantity=quantity
        )
        self.transactions.append(transaction)

        if product.quantity > product.threshold:
            self._notify_all(
                f"สินค้า {product.name} ถูกเติมแล้ว สต็อกในระบบคงเหลือ {product.quantity}"
            )
        else:
            self._notify_all(
                f"สินค้าในสต็อกต่ำ {product.name} สต็อกในระบบคงเหลือ {product.quantity}"
            )

        return product

    def issue_stock(self, product_id: str, quantity: int) -> Product:
        """บันทึกการจ่ายสินค้าออกจากสต็อก และตรวจประเมินเงื่อนไขต่างๆ"""
        if product_id not in self.products:
            raise KeyError("ไม่พบสินค้าในระบบ")
        if quantity <= 0:
            raise ValueError("จำนวนสินค้าที่จ่ายออกต้องมากกว่า 0")

        product = self.products[product_id]

        if product.quantity == 0:
            self._notify_all(f"ไม่มีสินค้า {product.name} ในสต็อก")
            raise ValueError("ระบบปฏิเสธการจ่ายสินค้า เนื่องจากไม่มีสินค้าในสต็อก")

        if product.quantity < quantity:
            self._notify_all(f"สินค้า {product.name} ในสต็อกไม่พอ")
            raise ValueError("ระบบปฏิเสธการจ่ายสินค้า เนื่องจากสินค้าในสต็อกไม่พอ")

        product.quantity -= quantity

        transaction = StockTransaction(
            id=str(uuid.uuid4()),
            product_id=product_id,
            transaction_type=TransactionType.OUT,
            quantity=quantity
        )
        self.transactions.append(transaction)

        if product.quantity < product.threshold:
            self._notify_all(
                f"สต็อกสินค้า {product.name} ต่ำกว่า threshold "
                f"(คงเหลือ {product.quantity}, threshold = {product.threshold})"
            )

        return product

    def update_threshold(self, product_id: str, new_threshold: Union[int, float, str]) -> Product:
        """อัปเดตค่า threshold ของสินค้า และส่งการแจ้งเตือนตามเงื่อนไข"""
        if product_id not in self.products:
            raise KeyError("ไม่พบสินค้าในระบบ")

        if isinstance(new_threshold, str):
            try:
                val = float(new_threshold)
                if not val.is_integer():
                    raise ValueError
                parsed_threshold = int(val)
            except ValueError:
                raise ValueError("กรุณากรอกค่าเป็นตัวเลข")
        elif isinstance(new_threshold, (int, float)):
            if isinstance(new_threshold, float) and not new_threshold.is_integer():
                raise ValueError("กรุณากรอกค่าเป็นตัวเลข")
            parsed_threshold = int(new_threshold)
        else:
            raise ValueError("กรุณากรอกค่าเป็นตัวเลข")

        if parsed_threshold <= 0:
            raise ValueError("กรุณากรอกตัวเลขที่มากกว่า 0")

        product = self.products[product_id]
        product.threshold = parsed_threshold

        if product.quantity < product.threshold:
            self._notify_all(
                f"มีการเปลี่ยนแปลง threshold ของ {product.name} เป็น {parsed_threshold} "
                f"และสินค้าในสต็อกต่ำ (คงเหลือ {product.quantity})"
            )
        else:
            self._notify_all(
                f"มีการเปลี่ยนแปลง threshold ของ {product.name} เป็น {parsed_threshold}"
            )

        return product

    def get_stock_value_by_category(self) -> Dict[str, float]:
        """รายงานคํานวณมูลค่ารวมของสต็อกสินค้าแยกตามหมวดหมู่"""
        category_values: Dict[str, float] = {}
        for product in self.products.values():
            cat_name = product.category.name
            total_val = product.quantity * product.price_per_unit
            category_values[cat_name] = category_values.get(cat_name, 0.0) + total_val
        return category_values