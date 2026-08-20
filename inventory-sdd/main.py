import sys
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


def main() -> None:
    # 1. ตั้งค่า Notifiers ผ่าน Factory (รองรับทั้ง Email และ SMS)
    email_notifier = NotifierFactory.create_notifier("email", "manager@company.com")
    sms_notifier = NotifierFactory.create_notifier("sms", "081-234-5678")
    
    # 2. ฉีด Dependency เข้าสู่ InventoryService
    service = InventoryService(notifiers=[email_notifier, sms_notifier])

    # 3. เตรียมข้อมูล Mock Data สำหรับเริ่มต้นใช้งาน
    cat_elec = Category(id="CAT01", name="อุปกรณ์ไฟฟ้า")
    service.add_category(cat_elec)

    # สินค้าตัวอย่างตาม Spec (สายไฟ 2.5 sq.mm, ราคา 200 บาท, สต็อก 50, threshold 15)
    product_wire = Product(
        id="P001",
        name="สายไฟ 2.5 sq.mm",
        category=cat_elec,
        price_per_unit=200.0,
        quantity=50,
        threshold=15
    )
    service.add_product(product_wire)

    print("เริ่มต้นระบบสำเร็จ! โหลดข้อมูลสินค้าตัวอย่างเรียบร้อยแล้ว")

    # Loop การทำงานหน้า CLI
    while True:
        print_menu()
        choice = input("เลือกรายการทำรายการ (0-5): ").strip()

        if choice == "1":
            print("\n--- บันทึกรับสินค้าเข้า ---")
            p_id = input("รหัสสินค้า (เช่น P001): ").strip()
            try:
                qty = int(input("จำนวนที่รับเข้า: "))
                updated_prod = service.receive_stock(p_id, qty)
                print(f" SUCCESS: บันทึกรับเข้าสำเร็จ! สต็อกปัจจุบัน: {updated_prod.quantity}")
            except Exception as e:
                print(f" ERROR: {e}")

        elif choice == "2":
            print("\n--- บันทึกจ่ายสินค้าออก ---")
            p_id = input("รหัสสินค้า (เช่น P001): ").strip()
            try:
                qty = int(input("จำนวนที่จ่ายออก: "))
                updated_prod = service.issue_stock(p_id, qty)
                print(f" SUCCESS: บันทึกจ่ายออกสำเร็จ! สต็อกคงเหลือ: {updated_prod.quantity}")
            except Exception as e:
                print(f" ERROR: {e}")

        elif choice == "3":
            print("\n--- แก้ไขค่า Threshold สินค้า ---")
            p_id = input("รหัสสินค้า (เช่น P001): ").strip()
            new_val = input("กำหนดค่า Threshold ใหม่: ").strip()
            try:
                updated_prod = service.update_threshold(p_id, new_val)
                print(f" SUCCESS: อัปเดต Threshold ของ {updated_prod.name} เป็น {updated_prod.threshold} สำเร็จ")
            except Exception as e:
                print(f" ERROR: {e}")

        elif choice == "4":
            print("\n--- รายงานมูลค่าสต็อกแยกตามหมวดหมู่ ---")
            report = service.get_stock_value_by_category()
            for cat_name, total_val in report.items():
                print(f"• หมวดหมู่ {cat_name} = {total_val:,.2f} บาท")

        elif choice == "5":
            print("\n--- รายการสินค้าทั้งหมด ---")
            for p in service.products.values():
                print(f"[{p.id}] {p.name} | หมวดหมู่: {p.category.name} | คงเหลือ: {p.quantity} | Threshold: {p.threshold} | ราคา/หน่วย: {p.price_per_unit} บาท")

        elif choice == "0":
            print("\nปิดการทำงานของระบบ สวัสดีครับ!")
            sys.exit(0)

        else:
            print("\n ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")


if __name__ == "__main__":
    main()