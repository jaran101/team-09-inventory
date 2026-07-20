class InventorySystem:
    def __init__(self):
        # จำลองฐานข้อมูลสต็อกสินค้า
        self.stock = {}

    def add_product(self, product_id: str, product_name: str, quantity: int):
        """
        ฟังก์ชันสำหรับเพิ่มสินค้าใหม่เข้าระบบ
        """
        # Tasks 1-3: ตรวจสอบว่ามีสินค้าอยู่ในระบบหรือไม่
        if product_id in self.stock:
            # Expected Result: กรณีมีสินค้าอยู่แล้ว
            print("มีสินค้าในระบบอยู่แล้ว")
            return False
        
        # Task 4: หากไม่มีสินค้า ให้ดำเนินการเพิ่มสินค้าต่อ
        self.stock[product_id] = {
            "name": product_name,
            "quantity": quantity
        }
        
        # Expected Result: กรณีไม่มีสินค้า
        print(f"ชื่อสินค้า : {product_name}")
        print(f"รหัสสินค้า : {product_id}")
        print(f"จำนวน : {quantity}")
        return True
