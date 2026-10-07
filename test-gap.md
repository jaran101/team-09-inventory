# บันทึกการวิเคราะห์ Test Gap (ขั้นที่ 4)

| กรณีที่ AI ให้มา (Happy Path) | กรณีที่ขาด (Edge Cases / Error Path) | Test ที่เราเขียนเสริม (In `tests/test_inventory.py`) |
| :--- | :--- | :--- |
| **จ่ายสินค้าปกติ (จำนวน < สต็อก)**<br>`inv_service.issue_stock("P01", 3)` | **ค่าขอบ:** จ่ายสินค้าเท่ากับจำนวนสต็อกที่มีอยู่ทั้งหมดพอดี (ขายจนหมด สต็อกต้องเหลือ 0 พอดี) | `test_issue_stock_exact_quantity` |
| **จ่ายสินค้าปกติ**<br>`inv_service.issue_stock("P01", 3)` | **ค่าที่ไม่ควรรับ:** จ่ายสินค้าด้วยจำนวน 0 หรือ ติดลบ (ต้องเกิด Error/ValueError) | `test_issue_stock_zero_or_negative_quantity` |
| **จ่ายสินค้าปกติ**<br>`inv_service.issue_stock("P01", 3)` | **เส้นทาง error:** จ่ายสินค้าเกินจำนวนที่มีอยู่ในสต็อก (ต้องเกิด Error/ValueError) | `test_issue_stock_exceeds_available_quantity` |
| **จ่ายสินค้าปกติ**<br>`inv_service.issue_stock("P01", 3)` | **เส้นทาง error:** สั่งจ่ายสินค้าด้วย Product ID ที่ไม่มีในระบบ (ต้องเกิด Exception/KeyError) | `test_issue_stock_product_not_found` |
| **จ่ายสินค้าปกติ**<br>`inv_service.issue_stock("P01", 3)` | **ชนิดข้อมูล:** ใส่จำนวนสินค้าเป็นประเภทข้อมูลที่ไม่ถูกต้อง เช่น ข้อความ (string) หรือ ทศนิยม (float) | `test_issue_stock_invalid_type` |