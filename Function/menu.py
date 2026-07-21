# ชื่อไฟล์: menu.py

from insertfunction import InventoryManager
from list import display_all_products

def main():
    manager = InventoryManager()
    ADMIN_PASSWORD = "admin"

    print("=== ยินดีต้อนรับสู่ระบบจัดการสต็อกสินค้า ===")
    print("พิมพ์ 'help' เพื่อดูคำสั่งทั้งหมด หรือ 'exit' เพื่อออกจากโปรแกรม")

    while True:
        # หน้าต่างรอรับคำสั่งแบบ CLI
        command = input("\nInventoryCLI> ").strip().lower()

        # ป้องกันการกด Enter ค้างโดยไม่ได้พิมพ์อะไร
        if not command:
            continue

        # --- ฟังก์ชัน Insert ---
        if command == 'insert':
            print("\n=== เพิ่มสินค้า ===")
            name = input("ชื่อสินค้า : ")
            code = input("รหัสสินค้า : ")
            
            while True:
                try:
                    quantity = int(input("จำนวน : "))
                    break
                except ValueError:
                    print("กรุณากรอกจำนวนเป็นตัวเลขเท่านั้น")
            
            success, message = manager.add_product(name, code, quantity)
            print(message)

        # --- ฟังก์ชัน List ---
        elif command == 'list':
            display_all_products(manager.inventory)

        # --- เมนูช่วยเหลือ (Help) ---
        elif command == 'help':
            print("\n=== คำสั่งที่ใช้งานได้ ===")
            print("  insert  - เพิ่มสินค้าใหม่")
            print("  list    - เรียกดูรายการสินค้าทั้งหมด")
            print("  edit    - แก้ไขสินค้า (กำลังพัฒนา)")
            print("  search  - ค้นหาสินค้า [Admin Only]")
            print("  export  - ส่งออกข้อมูล [Admin Only]")
            print("  exit    - ออกจากโปรแกรม")

        # --- เมนูที่ต้องใช้รหัส Admin ---
        elif command in ['search', 'export']:
            pwd = input("กรุณาใส่รหัสผ่าน Admin : ")
            if pwd == ADMIN_PASSWORD:
                if command == 'search':
                    print("\n[เข้าสู่ระบบ Admin] ... กำลังเปิดฟังก์ชันค้นหาสินค้า")
                elif command == 'export':
                    print("\n[เข้าสู่ระบบ Admin] ... กำลังเปิดฟังก์ชันส่งออกงานสต็อก")
            else:
                print("รหัสผ่านไม่ถูกต้อง! ปฏิเสธการเข้าถึง")

        # --- เมนูอื่นๆ ---
        elif command == 'edit':
            print("\nกำลังเปิดฟังก์ชันแก้ไขสินค้า...")
        
        # --- ออกจากโปรแกรม ---
        elif command == 'exit':
            print("ออกจากระบบ...")
            break
            
        else:
            print(f"ไม่พบคำสั่ง '{command}' (พิมพ์ 'help' เพื่อดูคำสั่งทั้งหมด)")

if __name__ == "__main__":
    main()
