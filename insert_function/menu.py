# ชื่อไฟล์: menu.py

# นำเข้า Class InventoryManager จากไฟล์ insertfunction.py
from insertfunction import InventoryManager

def main():
    manager = InventoryManager()
    ADMIN_PASSWORD = "admin"

    while True:
        print("\n=== ระบบจัดการสต็อกสินค้า ===")
        print("1. เพิ่มสินค้า (พิมพ์ 'insert')")
        print("2. เรียกดูสินค้า")
        print("3. แก้ไขสินค้า")
        print("4. ค้นหาสินค้าบางรายการ [Admin Only]")
        print("5. ส่งออกงานสต็อก [Admin Only]")
        print("0. ออกจากโปรแกรม")
        
        command = input("เลือกเมนู : ").strip().lower()

        # --- ฟังก์ชัน Insert ---
        if command == 'insert' or command == '1':
            print("\n=== เพิ่มสินค้า ===")
            name = input("ชื่อสินค้า : ")
            code = input("รหัสสินค้า : ")
            
            while True:
                try:
                    quantity = int(input("จำนวน : "))
                    break
                except ValueError:
                    print("กรุณากรอกจำนวนเป็นตัวเลขเท่านั้น")
            
            # เรียกใช้งานฟังก์ชันจาก manager
            success, message = manager.add_product(name, code, quantity)
            print(message)

        # --- เมนูที่ต้องใช้รหัส Admin ---
        elif command in ['4', '5']:
            pwd = input("กรุณาใส่รหัสผ่าน Admin : ")
            if pwd == ADMIN_PASSWORD:
                if command == '4':
                    print("\n[เข้าสู่ระบบ Admin] ... กำลังเปิดฟังก์ชันค้นหาสินค้า")
                elif command == '5':
                    print("\n[เข้าสู่ระบบ Admin] ... กำลังเปิดฟังก์ชันส่งออกงานสต็อก")
            else:
                print("รหัสผ่านไม่ถูกต้อง! ปฏิเสธการเข้าถึง")

        # --- เมนูอื่นๆ ---
        elif command == '2':
            print("\nกำลังเปิดฟังก์ชันเรียกดูสินค้า...")
        elif command == '3':
            print("\nกำลังเปิดฟังก์ชันแก้ไขสินค้า...")
        
        # --- ออกจากโปรแกรม ---
        elif command == '0':
            print("ปิดโปรแกรม...")
            break
        else:
            print("คำสั่งไม่ถูกต้อง กรุณาเลือกใหม่")

if __name__ == "__main__":
    main()
