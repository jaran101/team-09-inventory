import sys
from collections.abc import Callable

from src.models import Category, Product
from src.notifiers import NotifierFactory
from src.service import InventoryService


def print_menu() -> None:
    """แสดงเมนูหลักของระบบ"""
    print("\n" + "=" * 45)
    print("      ระบบจัดการคลังสินค้า (Inventory System)")
    print("=" * 45)
    print("[1] บันทึกการรับสินค้าเข้า (Receive Stock)")
    print("[2] บันทึกการจ่ายสินค้าออก (Issue Stock)")
    print("[3] แก้ไขค่า Threshold สินค้า")
    print("[4] ดูรายงานมูลค่าสต็อกแยกตามหมวดหมู่")
    print("[5] แสดงรายการสินค้าทั้งหมดในระบบ")
    print("[0] ออกจากโปรแกรม")
    print("=" * 45)


def read_quantity(prompt: str) -> int:
    """อ่านจำนวนเต็มจากผู้ใช้ พร้อมข้อความ error ภาษาไทย"""
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        raise ValueError("กรุณากรอกจำนวนเป็นตัวเลขจำนวนเต็ม")


def run_action(action: Callable[[], str]) -> None:
    """รัน action และแสดงผลสำเร็จ/ข้อผิดพลาดแบบเดียวกันทุกเมนู"""
    try:
        print(f" SUCCESS: {action()}")
    except KeyError as e:
        print(f" ERROR: {e.args[0] if e.args else e}")
    except ValueError as e:
        print(f" ERROR: {e}")


def build_service() -> InventoryService:
    """สร้าง service พร้อม notifier และข้อมูลตัวอย่าง"""
    email_notifier = NotifierFactory.create("email", "manager@company.com")
    sms_notifier = NotifierFactory.create("sms", "081-234-5678")
    service = InventoryService(notifiers=[email_notifier, sms_notifier])

    cat_elec = Category(id="CAT01", name="อุปกรณ์ไฟฟ้า")
    service.add_category(cat_elec)
    service.add_product(
        Product(
            id="P001",
            name="สายไฟ 2.5 sq.mm",
            category=cat_elec,
            price_per_unit=200.0,
            quantity=50,
            threshold=15,
        )
    )
    return service


def main() -> None:
    """จุดเริ่มต้นของโปรแกรม CLI"""
    service = build_service()
    print("เริ่มต้นระบบสำเร็จ! โหลดข้อมูลสินค้าตัวอย่างเรียบร้อยแล้ว")

    while True:
        print_menu()
        try:
            choice = input("เลือกรายการทำรายการ (0-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nปิดการทำงานของระบบ")
            return

        try:
            if choice == "1":
                print("\n--- บันทึกรับสินค้าเข้า ---")
                p_id = input("รหัสสินค้า (เช่น P001): ").strip()
                run_action(lambda: _receive(service, p_id))
            elif choice == "2":
                print("\n--- บันทึกจ่ายสินค้าออก ---")
                p_id = input("รหัสสินค้า (เช่น P001): ").strip()
                run_action(lambda: _issue(service, p_id))
            elif choice == "3":
                print("\n--- แก้ไขค่า Threshold สินค้า ---")
                p_id = input("รหัสสินค้า (เช่น P001): ").strip()
                new_val = input("กำหนดค่า Threshold ใหม่: ").strip()
                run_action(lambda: _threshold(service, p_id, new_val))
            elif choice == "4":
                print("\n--- รายงานมูลค่าสต็อกแยกตามหมวดหมู่ ---")
                for cat_name, total_val in service.get_stock_value_by_category().items():
                    print(f"• หมวดหมู่ {cat_name} = {total_val:,.2f} บาท")
            elif choice == "5":
                print("\n--- รายการสินค้าทั้งหมด ---")
                for p in service.list_products():
                    print(
                        f"[{p.id}] {p.name} | หมวดหมู่: {p.category.name} | "
                        f"คงเหลือ: {p.quantity} | Threshold: {p.threshold} | "
                        f"ราคา/หน่วย: {p.price_per_unit} บาท"
                    )
            elif choice == "0":
                print("\nปิดการทำงานของระบบ สวัสดีครับ!")
                sys.exit(0)
            else:
                print("\n ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
        except (EOFError, KeyboardInterrupt):
            print("\nปิดการทำงานของระบบ")
            return


def _receive(service: InventoryService, p_id: str) -> str:
    """อ่านจำนวนและบันทึกรับเข้า"""
    qty = read_quantity("จำนวนที่รับเข้า: ")
    prod = service.receive_stock(p_id, qty)
    return f"บันทึกรับเข้าสำเร็จ! สต็อกปัจจุบัน: {prod.quantity}"


def _issue(service: InventoryService, p_id: str) -> str:
    """อ่านจำนวนและบันทึกจ่ายออก"""
    qty = read_quantity("จำนวนที่จ่ายออก: ")
    prod = service.issue_stock(p_id, qty)
    return f"บันทึกจ่ายออกสำเร็จ! สต็อกคงเหลือ: {prod.quantity}"


def _threshold(service: InventoryService, p_id: str, new_val: str) -> str:
    """อัปเดต threshold"""
    prod = service.update_threshold(p_id, new_val)
    return f"อัปเดต Threshold ของ {prod.name} เป็น {prod.threshold} สำเร็จ"


if __name__ == "__main__":
    main()
