class InventoryManager:
    def __init__(self):
        self.inventory = []

    def add_product(self, name, code, quantity):
        # ตรวจสอบรหัสซ้ำ
        for item in self.inventory:
            if item['code'] == code:
                return False, "รหัสสินค้านี้มีอยู่ในระบบแล้ว"
        
        # สร้าง Product ID อัตโนมัติ
        product_id = len(self.inventory) + 1
        
        # บันทึกข้อมูล
        new_item = {
            "id": product_id,
            "name": name,
            "code": code,
            "quantity": quantity
        }
        self.inventory.append(new_item)
        return True, "เพิ่มสินค้าสำเร็จ"
