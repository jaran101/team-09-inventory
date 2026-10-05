# รายงาน Phase 2A: Prompt Engineering เทียบกับ Context Engineering

## 1. การทดลองรอบที่ 1: Prompt ที่บกพร่อง (Prompt Engineering)

### Prompt ที่ใช้
```text
เขียน function ลด stock
```

### ผลลัพธ์ที่ได้จาก AI
```python
def reduce_stock(item_id, amount):
    # AI สร้างฟังก์ชันแยกเดี่ยวและสุ่มโครงสร้างขึ้นมาเอง ไม่ตรงกับระบบเดิม
    stock = get_stock(item_id)
    if stock >= amount:
        new_stock = stock - amount
        update_stock(item_id, new_stock)
        return new_stock
    return "Stock not enough"
```

---

## 2. การทดลองรอบที่ 2: Prompt ที่มี Context ครบถ้วน (Context Engineering)

### Prompt ที่ใช้
> *"ปรับปรุงเมธอด sell() ของคลาส Inventory ด้านล่างให้รองรับการขายหลายรายการพร้อมกัน"*
>
> ```python
> import sys
> from src.models import Category, Product
> from src.notifiers import NotifierFactory
> from src.service import InventoryService
> 
> def print_menu() -> None:
>     """แสดงเมนูหลักของระบบ"""
>     print("\n" + "=" * 45)
>     print("      ระบบจัดการคลังสินค้า (Inventory System)")
>     print("=" * 45)
>     print("[1] บันทึกการรับสินค้าเข้า (Receive Stock)")
>     print("[2] บันทึกการจ่ายสินค้าออก (Issue Stock)")
>     print("[3] แก้ไขค่า Threshold สินค้า")
>     print("[4] ดูรายงานมูลค่าสต็อกแยกตามหมวดหมู่")
>     print("[5] แสดงรายการสินค้าทั้งหมดในระบบ")
>     print("[0] ออกจากโปรแกรม")
>     print("=" * 45)
> 
> def main() -> None:
>     email_notifier = NotifierFactory.create_notifier("email", "manager@company.com")
>     sms_notifier = NotifierFactory.create_notifier("sms", "081-234-5678")
>     service = InventoryService(notifiers=[email_notifier, sms_notifier])
>     cat_elec = Category(id="CAT01", name="อุปกรณ์ไฟฟ้า")
>     service.add_category(cat_elec)
>     product_wire = Product(
>         id="P001",
>         name="สายไฟ 2.5 sq.mm",
>         category=cat_elec,
>         price_per_unit=200.0,
>         quantity=50,
>         threshold=15
>     )
>     service.add_product(product_wire)
>     print("เริ่มต้นระบบสำเร็จ! โหลดข้อมูลสินค้าตัวอย่างเรียบร้อยแล้ว")
>     while True:
>         print_menu()
>         choice = input("เลือกรายการทำรายการ (0-5): ").strip()
>         if choice == "1":
>             print("\n--- บันทึกรับสินค้าเข้า ---")
>             p_id = input("รหัสสินค้า (เช่น P001): ").strip()
>             try:
>                 qty = int(input("จำนวนที่รับเข้า: "))
>                 updated_prod = service.receive_stock(p_id, qty)
>                 print(f" SUCCESS: บันทึกรับเข้าสำเร็จ! สต็อกปัจจุบัน: {updated_prod.quantity}")
>             except Exception as e:
>                 print(f" ERROR: {e}")
>         elif choice == "2":
>             print("\n--- บันทึกจ่ายสินค้าออก ---")
>             p_id = input("รหัสสินค้า (เช่น P001): ").strip()
>             try:
>                 qty = int(input("จำนวนที่จ่ายออก: "))
>                 updated_prod = service.issue_stock(p_id, qty)
>                 print(f" SUCCESS: บันทึกจ่ายออกสำเร็จ! สต็อกคงเหลือ: {updated_prod.quantity}")
>             except Exception as e:
>                 print(f" ERROR: {e}")
>         elif choice == "3":
>             print("\n--- แก้ไขค่า Threshold สินค้า ---")
>             p_id = input("รหัสสินค้า (เช่น P001): ").strip()
>             new_val = input("กำหนดค่า Threshold ใหม่: ").strip()
>             try:
>                 updated_prod = service.update_threshold(p_id, new_val)
>                 print(f" SUCCESS: อัปเดต Threshold ของ {updated_prod.name} เป็น {updated_prod.threshold} สำเร็จ")
>             except Exception as e:
>                 print(f" ERROR: {e}")
>         elif choice == "4":
>             print("\n--- รายงานมูลค่าสต็อกแยกตามหมวดหมู่ ---")
>             report = service.get_stock_value_by_category()
>             for cat_name, total_val in report.items():
>                 print(f"• หมวดหมู่ {cat_name} = {total_val:,.2f} บาท")
>         elif choice == "5":
>             print("\n--- รายการสินค้าทั้งหมด ---")
>             for p in service.products.values():
>                 print(f"[{p.id}] {p.name} | หมวดหมู่: {p.category.name} | คงเหลือ: {p.quantity} | Threshold: {p.threshold} | ราคา/หน่วย: {p.price_per_unit} บาท")
>         elif choice == "0":
>             print("\nปิดการทำงานของระบบ สวัสดีครับ!")
>             sys.exit(0)
>         else:
>             print("\n ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
> if __name__ == "__main__":
>     main()
> ```
>
> **ข้อกำหนด:**
> - เพิ่มเมธอด `sell_many(orders: dict[str, int]) -> dict[str, int]` คืน `{ชื่อ: คงเหลือ}`
> - ถ้ามีรายการใดรายการหนึ่ง stock ไม่พอ ต้อง `raise ValueError` และต้องไม่หักรายการใดเลย ทุกรายการต้องสำเร็จพร้อมกันหรือไม่สำเร็จเลย (atomic)
> - ใช้ exception แบบเดียวกับเมธอดเดิม (`KeyError` เมื่อไม่พบสินค้า)
> - ห้ามใช้ library ภายนอก
>
> **โค้ดต้องผ่าน test เหล่านี้:**
> - ขายหลายรายการสำเร็จ คืนคงเหลือถูกต้อง
> - ถ้ารายการที่ 2 stock ไม่พอ ต้องไม่หักรายการที่ 1 (rollback)

### ผลลัพธ์ที่ได้จาก AI
```python
elif choice == "2.1":  
    print("\n--- บันทึกขายสินค้าหลายรายการ (Batch Sell) ---")
    orders = {}
    while True:
        p_id = input("รหัสสินค้า (กด Enter เมื่อใส่ครบแล้ว): ").strip()
        if not p_id:
            break
        try:
            qty = int(input("จำนวน: "))
            orders[p_id] = qty
        except ValueError:
            print("กรุณากรอกจำนวนเป็นตัวเลข")
    if orders:
        try:
            summary = service.sell_many(orders)
            print("\n SUCCESS: บันทึกการขายสำเร็จทุกรายการ!")
            for name, remaining in summary.items():
                print(f" • {name}: สต็อกคงเหลือ {remaining}")
        except (KeyError, ValueError) as e:
            print(f"\n ERROR: ยกเลิกการทำรายการทั้งหมด -> {e}")
```

### การวิเคราะห์ผลลัพธ์
* **ความเข้ากันได้กับโค้ดเดิม:** สามารถนำไปต่อยอดกับเมนู CLI และคลาส `Inventory` ได้ทันที
* **การจัดการ Exception:** ตรงตามเงื่อนไข `KeyError` และ `ValueError` ตามสไตล์การจัดการข้อผิดพลาดของโค้ดเดิม
* **Business Logic:** ทำงานถูกต้องตามกฎ Transaction คือตรวจสอบความพร้อมทั้งหมดก่อนตัด Stock (Atomic Operation)

---

## 3. ตารางสรุปเปรียบเทียบผลการทดลอง

| ประเด็นการเปรียบเทียบ | การทดลองรอบที่ 1: Prompt ที่บกพร่อง (Prompt Engineering) | การทดลองรอบที่ 2: Prompt ที่มี Context ครบถ้วน (Context Engineering) |
| :--- | :--- | :--- |
| **ระดับความชัดเจนของคำสั่ง (Scope & Specificity)** | **ต่ำมาก / สั้นเกินไป**<br>สั่งเพียง `"เขียน function ลด stock"` โดยไม่ระบุชื่อฟังก์ชัน/เมธอด, Signature, หรือชนิดข้อมูล | **สูงมาก / ชัดเจนครบถ้วน**<br>ระบุการเพิ่มตัวเลือก CLI (`choice == "2.1"`), โครงสร้างการรับข้อมูล และการจัดการ `orders: dict[str, int]` ชัดเจน |
| **การรับรู้บริบทระบบเดิม (Context Awareness)** | **ไม่รับรู้บริบทเดิม (No Context)**<br>AI คาดเดาและสร้างฟังก์ชันแยกเดี่ยว เช่น `reduce_stock(item_id, amount)` ที่ไม่ได้เชื่อมต่อกับระบบเดิม | **สอดคล้องกับระบบเดิม (Full Context)**<br>AI ยึดโครงสร้าง CLI, เมนูหลัก และเรียกใช้งาน `service.sell_many(orders)` ต่อจาก `InventoryService` ได้ทันที |
| **การจัดการ Exception & Edge Cases** | **ไม่มีมาตรฐาน Error Handling**<br>คืนค่าเป็น String เช่น `"Stock not enough"` ซึ่งไม่ถูกต้องตามหลักการจัดการ Exception ของระบบ | **ตรงตามข้อกำหนดระบบ (Exception Handling)**<br>ครอบ `try-except` ดักจับ `KeyError` และ `ValueError` พร้อมแสดงข้อความยกเลิกรายการเมื่อเกิด Error |
| **พฤติกรรมของระบบ (Business Logic & Atomicity)** | **ไม่มีคุณสมบัติ Transaction**<br>หากมีการหักสต็อกหลายรายการ อาจถูกตัดไปบางส่วนก่อนที่จะพบข้อผิดพลาดในรายการถัดไป | **เป็น Atomic Transaction**<br>รองรับกฎการขายแบบ Batch คือตรวจสอบความพร้อมทั้งหมดก่อน หากมีรายการใดผิดพลาดจะ Cancel และ Rollback ทั้งหมด |
| **ความพร้อมในการนำไปใช้งานจริง (Usability)** | **ใช้งานจริงไม่ได้**<br>ต้องเขียนโค้ดและปรับโครงสร้างใหม่เกือบทั้งหมดเพื่อให้เข้ากับระบบ | **นำไป integrated ได้ทันที**<br>นำบล็อกโค้ด `elif choice == "2.1":` ไปวางต่อใน Loop ของไฟล์หลักเพื่อใช้งานได้เลย |

---

## 4. สรุปบทเรียนที่ได้รับ (Key Takeaways)
1. **Context คือหัวใจสำคัญของการเจนโค้ด:** การระบุเพียง Prompt สั้นๆ ทำให้ AI สุ่มโครงสร้างขึ้นมาเอง แต่การส่ง Context ทั้งโค้ดเดิม, เงื่อนไข Error และ Test Cases ช่วยให้ AI สร้างโค้ดที่ทำงานร่วมกับระบบเดิมได้แม่นยำ
2. **การทำ Atomic Operations:** การใส่เงื่อนไขความต้องการเรื่อง Rollback/Atomic ใน Context ทำให้ AI เลือกใช้รูปแบบ Validate ทั้งหมดก่อนสั่ง Execution ส่งผลให้ระบบคงความถูกต้องของข้อมูล (Data Integrity) ได้อย่างสมบูรณ์