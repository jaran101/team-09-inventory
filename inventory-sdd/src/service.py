import logging
import re
import threading
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .models import Category, Product, StockTransaction, TransactionType, _is_int
from .notifiers import Notifier

logger = logging.getLogger(__name__)

_INT_TEXT = re.compile(r"[+-]?\d+(\.0+)?", re.ASCII)


class InventoryService:
    """บริการจัดการสต็อกสินค้า คำนวณมูลค่า และส่งการแจ้งเตือน

    ปลอดภัยต่อการเรียกจากหลาย thread (NFR-03): การเปลี่ยนสถานะทั้งหมดอยู่ใน lock
    ส่วนการส่งแจ้งเตือนทำหลังปล่อย lock และ notifier ที่ล้มเหลวจะไม่กระทบ
    ธุรกรรมหรือ notifier ตัวอื่น
    """

    def __init__(self, notifiers: Optional[List[Notifier]] = None) -> None:
        """กำหนดค่าเริ่มต้นสำหรับบริการคลังสินค้าพร้อมรองรับ Dependency Injection"""
        self.products: Dict[str, Product] = {}
        self.categories: Dict[str, Category] = {}
        self.transactions: List[StockTransaction] = []
        self.notifiers: List[Notifier] = list(notifiers) if notifiers is not None else []
        self._lock = threading.RLock()

    def add_category(self, category: Category) -> None:
        """เพิ่มหมวดหมู่สินค้าใหม่เข้าสู่ระบบ"""
        with self._lock:
            self.categories[category.id] = category

    def add_product(self, product: Product) -> None:
        """เพิ่มสินค้าใหม่ (ปฏิเสธรหัสซ้ำ และหมวดหมู่ที่ยังไม่ลงทะเบียน)"""
        with self._lock:
            if product.id in self.products:
                raise ValueError("รหัสสินค้านี้มีอยู่ในระบบแล้ว")
            if product.category.id not in self.categories:
                raise ValueError("ไม่พบหมวดหมู่สินค้าในระบบ กรุณาเพิ่มหมวดหมู่ก่อน")
            self.products[product.id] = product

    def list_products(self) -> List[Product]:
        """คืนรายการสินค้าทั้งหมด (สำเนาของ list)"""
        with self._lock:
            return list(self.products.values())

    def _notify_all(self, messages: List[str]) -> None:
        """ส่งข้อความไปยังทุกช่องทาง โดย notifier ที่ล้มเหลวจะถูก log และข้ามไป"""
        for message in messages:
            for notifier in list(self.notifiers):
                try:
                    notifier.send(message)
                except Exception:  # noqa: BLE001 - ไม่ให้ช่องทางเดียวทำให้ทั้งระบบล้ม
                    logger.exception("ส่งการแจ้งเตือนล้มเหลว: %r", notifier)

    @staticmethod
    def _check_quantity(quantity: Any, label: str) -> None:
        """ตรวจว่าจำนวนเป็นจำนวนเต็มที่มากกว่า 0"""
        if not _is_int(quantity):
            raise ValueError(f"จำนวนสินค้าที่{label}ต้องเป็นจำนวนเต็ม")
        if quantity <= 0:
            raise ValueError(f"จำนวนสินค้าที่{label}ต้องมากกว่า 0")

    def _get(self, product_id: str) -> Product:
        """ดึงสินค้า (ต้องเรียกภายใน lock)"""
        product = self.products.get(product_id)
        if product is None:
            raise KeyError("ไม่พบสินค้าในระบบ")
        return product

    def _record(self, product_id: str, kind: TransactionType, quantity: int) -> None:
        """บันทึกประวัติธุรกรรม (ต้องเรียกภายใน lock)"""
        self.transactions.append(
            StockTransaction(
                id=str(uuid.uuid4()),
                product_id=product_id,
                transaction_type=kind,
                quantity=quantity,
            )
        )

    def receive_stock(self, product_id: str, quantity: int) -> Product:
        """บันทึกการรับสินค้าเข้า

        "ต่ำ" หมายถึง quantity < threshold (สอดคล้องกับ issue_stock)
        - หลังรับแล้วยังต่ำ -> แจ้งสต็อกต่ำ
        - เดิมต่ำ แต่หลังรับไม่ต่ำแล้ว -> แจ้งว่าเติมแล้ว
        - เดิมไม่ต่ำและยังไม่ต่ำ -> ไม่แจ้ง
        """
        self._check_quantity(quantity, "รับเข้า")
        messages: List[str] = []
        with self._lock:
            product = self._get(product_id)
            was_low = product.quantity < product.threshold
            product.quantity += quantity
            self._record(product_id, TransactionType.IN, quantity)
            if product.quantity < product.threshold:
                messages.append(
                    f"สินค้าในสต็อกต่ำ {product.name} สต็อกในระบบคงเหลือ {product.quantity}"
                )
            elif was_low:
                messages.append(
                    f"สินค้า {product.name} ถูกเติมแล้ว สต็อกในระบบคงเหลือ {product.quantity}"
                )
        self._notify_all(messages)
        return product

    def issue_stock(self, product_id: str, quantity: int) -> Product:
        """บันทึกการจ่ายสินค้าออก (ตรวจสต็อกก่อนจ่าย และแจ้งเตือนตามเงื่อนไข)"""
        self._check_quantity(quantity, "จ่ายออก")
        messages: List[str] = []
        error: Optional[str] = None
        with self._lock:
            product = self._get(product_id)
            if product.quantity == 0:
                messages.append(f"ไม่มีสินค้า {product.name} ในสต็อก")
                error = "ระบบปฏิเสธการจ่ายสินค้า เนื่องจากไม่มีสินค้าในสต็อก"
            elif product.quantity < quantity:
                messages.append(f"สินค้า {product.name} ในสต็อกไม่พอ")
                error = "ระบบปฏิเสธการจ่ายสินค้า เนื่องจากสินค้าในสต็อกไม่พอ"
            else:
                product.quantity -= quantity
                self._record(product_id, TransactionType.OUT, quantity)
                if product.quantity < product.threshold:
                    messages.append(
                        f"สต็อกสินค้า {product.name} ต่ำกว่า threshold "
                        f"(คงเหลือ {product.quantity}, threshold = {product.threshold})"
                    )
        self._notify_all(messages)
        if error:
            raise ValueError(error)
        return product

    @staticmethod
    def _parse_threshold(value: Any) -> int:
        """แปลงค่า threshold ที่รับเข้ามาเป็น int หรือโยน ValueError ภาษาไทย"""
        if isinstance(value, bool):
            raise ValueError("กรุณากรอกค่าเป็นตัวเลข")
        if isinstance(value, str):
            text = value.strip()
            if not _INT_TEXT.fullmatch(text):
                raise ValueError("กรุณากรอกค่าเป็นตัวเลข")
            return int(float(text))
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        raise ValueError("กรุณากรอกค่าเป็นตัวเลข")

    def update_threshold(self, product_id: str, new_threshold: Any) -> Product:
        """อัปเดต threshold ของสินค้า และแจ้งเตือน (พร้อมแจ้งสต็อกต่ำถ้าเข้าเงื่อนไข)"""
        parsed = self._parse_threshold(new_threshold)
        if parsed <= 0:
            raise ValueError("กรุณากรอกตัวเลขที่มากกว่า 0")
        with self._lock:
            product = self._get(product_id)
            product.threshold = parsed
            if product.quantity < parsed:
                message = (
                    f"มีการเปลี่ยนแปลง threshold ของ {product.name} เป็น {parsed} "
                    f"และสินค้าในสต็อกต่ำ (คงเหลือ {product.quantity})"
                )
            else:
                message = f"มีการเปลี่ยนแปลง threshold ของ {product.name} เป็น {parsed}"
        self._notify_all([message])
        return product

    def get_stock_value_by_category(self) -> Dict[str, Decimal]:
        """รายงานมูลค่ารวมของสต็อกแยกตามชื่อหมวดหมู่"""
        values: Dict[str, Decimal] = {}
        with self._lock:
            for product in self.products.values():
                name = product.category.name
                values[name] = values.get(name, Decimal(0)) + product.quantity * product.price_per_unit
        return values
