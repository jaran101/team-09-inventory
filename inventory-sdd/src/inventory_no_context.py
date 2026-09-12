from dataclasses import dataclass
from typing import List, Dict, Protocol
import threading

# -------------------------------------------------------------------
# Design Notes & NFR-02: Pattern สำหรับการแจ้งเตือน (Observer/Notifier)
# -------------------------------------------------------------------
class NotificationService(Protocol):
    def send(self, message: str) -> None:
        ...

class ConsoleNotifier:
    """Print แจ้งเตือนผ่าน Console แทนการส่งจริง (In Scope)"""
    def send(self, message: str) -> None:
        print(f"[Console Alert] {message}")

class EmailNotifier:
    """จำลองการแจ้งเตือนผ่าน Email (US-05)"""
    def send(self, message: str) -> None:
        print(f"[Email Alert] {message}")

# -------------------------------------------------------------------
# Data Model
# -------------------------------------------------------------------
@dataclass
class Product:
    id: str
    name: str
    category: str
    price_per_unit: float
    stock: int = 0
    threshold: int = 0

# -------------------------------------------------------------------
# Core Business Logic (Inventory Manager)
# -------------------------------------------------------------------
class InventoryManager:
    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._notifiers: List[NotificationService] = []
        # NFR-03: Thread Lock สำหรับป้องกัน Data Corruption เมื่อแก้ไขพร้อมกัน
        self._lock = threading.Lock()

    def register_notifier(self, notifier: NotificationService) -> None:
        """เพิ่มช่องทางแจ้งเตือนใหม่โดยไม่ต้องแก้ Business Logic (NFR-02)"""
        self._notifiers.append(notifier)

    def _notify(self, message: str) -> None:
        """กระจายข้อความแจ้งเตือนไปยังทุกช่องทาง"""
        for notifier in self._notifiers:
            notifier.send(message)

    def add_product(self, product: Product) -> None:
        with self._lock:
            self._products[product.id] = product

    # --- US-01 & US-02: บันทึกการรับ/จ่ายสินค้า และแจ้งเตือน ---
    def receive_stock(self, product_id: str, quantity: int) -> None:
        """FR-01: อัปเดตสต็อกทันทีเมื่อรับเข้า"""
        with self._lock:
            product = self._products.get(product_id)
            if not product:
                raise ValueError("ไม่พบสินค้าในระบบ")

            old_stock = product.stock
            product.stock += quantity

            # AC US-02: ตรวจสอบเงื่อนไขแจ้งเตือนเมื่อรับสินค้า
            if old_stock <= product.threshold and product.stock > product.threshold:
                self._notify(f"สินค้า '{product.name}' สต็อกถูกเติมแล้ว จำนวนสต็อกในระบบ: {product.stock}")
            elif product.stock <= product.threshold:
                self._notify(f"สินค้าในสต็อกต่ำ: '{product.name}' จำนวนสต็อกในระบบ: {product.stock}")

    def issue_stock(self, product_id: str, quantity: int) -> None:
        """FR-01, FR-02 & FR-03: ตรวจสอบและจ่ายสินค้า"""
        with self._lock:
            product = self._products.get(product_id)
            if not product:
                raise ValueError("ไม่พบสินค้าในระบบ")

            # AC US-01: กรณีสินค้าไม่มีในสต็อก
            if product.stock == 0:
                self._notify(f"ในสต็อกไม่มีสินค้า '{product.name}'")
                raise ValueError("ไม่มีสินค้าในสต็อก ปฏิเสธการจ่ายสินค้า")

            # AC US-01: กรณีสินค้าไม่พอ
            if product.stock < quantity:
                self._notify(f"สินค้าในสต็อกไม่พอสำหรับ '{product.name}'")
                raise ValueError("สินค้าในสต็อกไม่พอ ปฏิเสธการจ่ายสินค้า")

            # ดำเนินการจ่ายสินค้า
            product.stock -= quantity

            # AC US-02: แจ้งเตือนเมื่อสต็อกหลังจ่ายต่ำกว่า threshold
            if product.stock < product.threshold:
                self._notify(f"สต็อกต่ำกว่า threshold: สินค้า '{product.name}' เหลือ {product.stock} (Threshold: {product.threshold})")

    # --- US-04: กำหนดและแก้ไขค่า Threshold ---
    def update_threshold(self, product_id: str, new_threshold: int) -> None:
        """FR-04: ปรับเปลี่ยนค่า Threshold"""
        # AC US-04: ตรวจสอบชนิดข้อมูลและการป้อนค่า
        if not isinstance(new_threshold, int):
            raise TypeError("กรุณากรอกค่าเป็นตัวเลข")
        if new_threshold <= 0:
            raise ValueError("กรุณากรอกตัวเลขที่มากกว่า 0")

        with self._lock: # NFR-03: รองรับการแก้ไขพร้อมกัน
            product = self._products.get(product_id)
            if not product:
                raise ValueError("ไม่พบสินค้าในระบบ")

            product.threshold = new_threshold
            self._notify(f"สินค้า '{product.name}' มีการเปลี่ยนแปลง threshold เป็น {new_threshold}")

            # AC US-04: กรณีแก้ไข threshold แล้วสต็อกปัจจุบันต่ำกว่า threshold ใหม่
            if product.stock < product.threshold:
                self._notify(f"สินค้าในสต็อกต่ำ: '{product.name}' เหลือ {product.stock} (Threshold: {product.threshold})")

    # --- US-03 & NFR-01: รายงานมูลค่าสต็อกแยกตามหมวดหมู่ ---
    def get_stock_value_by_category(self) -> Dict[str, float]:
        """ประมวลผลมูลค่าสต็อกแยกตามหมวดหมู่"""
        report: Dict[str, float] = {}
        with self._lock:
            for product in self._products.values():
                value = product.stock * product.price_per_unit
                report[product.category] = report.get(product.category, 0.0) + value
        return report


# -------------------------------------------------------------------
# ตัวอย่างการใช้งานตาม Acceptance Criteria (AC)
# -------------------------------------------------------------------
if __name__ == "__main__":
    inv = InventoryManager()
    inv.register_notifier(ConsoleNotifier())
    inv.register_notifier(EmailNotifier()) # US-05

    # เพิ่มสินค้าเริ่มต้น
    inv.add_product(Product(
        id="P001",
        name="สายไฟ 2.5 sq.mm",
        category="อุปกรณ์ไฟฟ้า",
        price_per_unit=200.0,
        stock=20,
        threshold=15
    ))

    print("--- [1] ทดสอบ US-02: จ่ายสินค้าจนสต็อกต่ำกว่า threshold (จ่าย 8 จาก 20) ---")
    inv.issue_stock("P001", 8)  # สต็อกเหลือ 12 -> แจ้งเตือน

    print("\n--- [2] ทดสอบ US-02: รับสินค้าจนสต็อกมากกว่า threshold (รับ 5 เข้าสต็อก 12) ---")
    inv.receive_stock("P001", 5) # สต็อกเป็น 17 -> แจ้งเตือนว่าถูกเติมแล้ว

    print("\n--- [3] ทดสอบ US-03: ดูมูลค่ารวมแยกตามหมวดหมู่ ---")
    # ปรับสต็อกเป็น 50 เพื่อให้ตรงกับ AC US-03
    inv.receive_stock("P001", 33) 
    report = inv.get_stock_value_by_category()
    print(f"มูลค่ารวมหมวดหมู่อุปกรณ์ไฟฟ้า: {report.get('อุปกรณ์ไฟฟ้า'):,.2f} บาท")

    print("\n--- [4] ทดสอบ US-04: แก้ไข Threshold และ Validation ---")
    try:
        inv.update_threshold("P001", -5)
    except ValueError as e:
        print(f"Error จับได้ถูกต้อง: {e}")

    inv.update_threshold("P001", 60) # แก้ threshold เป็น 60 (สต็อกมี 50) -> แจ้งเตือนเปลี่ยนค่า + แจ้งเตือนสต็อกต่ำ