# ชื่อไฟล์: list.py

def display_all_products(inventory_data):
    print("\n=== รายการสินค้า ===")
    
    # ตรวจสอบว่ามีสินค้าในระบบหรือไม่
    if not inventory_data:
        print("\nยังไม่มีสินค้าในระบบ")
        return

    # วนลูปแสดงข้อมูลสินค้าแต่ละรายการ
    for item in inventory_data:
        print(f"\nชื่อสินค้า: {item['name']}")
        print(f"รหัสสินค้า: {item['code']}")
        print(f"จำนวนคงเหลือ: {item['quantity']}")
