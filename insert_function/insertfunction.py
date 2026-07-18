lass InventoryManager:
    def __init__(self):
        # ข้อมูลถูกเก็บไว้ใน object นี้
        self.inventory = []

    def add_product(self, code, name, quantity):
        # ตรวจสอบความซ้ำซ้อน
        for item in self.inventory:
            if item['code'] == code:
                return False, "มีสินค้าอยู่แล้ว"
        # สร้าง ID อัตโนมัติ
        product_id = len(self.inventory) + 1
        
        # เพิ่มข้อมูล
        new_item = {
            "id": product_id,
            "code": code,
            "name": name,
            "quantity": quantity
        }
        self.inventory.append(new_item)
        return True, "เพิ่มสินค้าสำเร็จ"

    def get_all_products(self):
        # คืนค่ารายการสินค้าทั้งหมดเพื่อนำไปแสดงผล
        return self.inventory

manager = InventoryManager()

while True:
    code = input("รหัสสินค้า : ")
    name = input("ชื่อสินค้า : ")
    
    # แยกส่วนการรับค่าจำนวนมาไว้ในลูปย่อย เพื่อดักจับ Error
    while True:
        try:
            quantity = int(input("จำนวน : "))
            break # ถ้าใส่ตัวเลขถูกต้อง ให้หลุดจากลูปย่อยนี้
        except ValueError:
            print("กรุณากรอกจำนวนเป็นตัวเลขเท่านั้น (เช่น 1, 2, 3)")
    
    # ส่งค่าไปยัง manager
    success, message = manager.add_product(code, name, quantity)
    print(message)
    if not success:
      continue
    break
