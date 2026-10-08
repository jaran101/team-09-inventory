import pytest
from src.models import Category, Product
from src.service import InventoryService


@pytest.fixture
def service():
    """Fixture สำหรับสร้าง InventoryService และ Category ตัวอย่าง"""
    inv_service = InventoryService()
    cat = Category(id="CAT01", name="สินค้าทั่วไป")
    inv_service.add_category(cat)
    return inv_service, cat


def test_low_stock_items_all_above_threshold(service):
    # 1. สินค้าทุกรายการมีจำนวนมากกว่า threshold -> คืน list ว่าง
    inv_service, cat = service
    inv_service.add_product(Product("P01", "Laptop", cat, 20000, quantity=10, threshold=5))
    inv_service.add_product(Product("P02", "Mouse", cat, 500, quantity=5, threshold=2))
    
    assert inv_service.low_stock_items(2) == []


def test_low_stock_items_equal_to_threshold(service):
    # 2. มีสินค้าที่จำนวนเท่ากับ threshold พอดี -> ต้องถูกนับรวมด้วย
    inv_service, cat = service
    inv_service.add_product(Product("P01", "Keyboard", cat, 1000, quantity=3, threshold=2))
    inv_service.add_product(Product("P02", "Monitor", cat, 4000, quantity=5, threshold=2))
    
    result = inv_service.low_stock_items(3)
    assert "Keyboard" in result


def test_low_stock_items_multiple_items_sorted(service):
    # 3. มีสินค้าเข้าเกณฑ์หลายรายการ -> ผลลัพธ์ต้องเรียงตามชื่อ (Alphabetical order)
    inv_service, cat = service
    inv_service.add_product(Product("P01", "Zebra Printer", cat, 5000, quantity=2, threshold=2))
    inv_service.add_product(Product("P02", "Adapter", cat, 300, quantity=1, threshold=2))
    inv_service.add_product(Product("P03", "Cable", cat, 150, quantity=2, threshold=2))
    
    assert inv_service.low_stock_items(2) == ["Adapter", "Cable", "Zebra Printer"]


def test_low_stock_items_empty_inventory():
    # 4. คลังว่างเปล่า -> คืน list ว่าง ไม่ใช่ error
    inv_service = InventoryService()
    assert inv_service.low_stock_items(5) == []


def test_low_stock_items_threshold_zero(service):
    # 5. threshold ที่ส่งให้เมธอด low_stock_items เป็น 0 -> คืนเฉพาะสินค้าที่มี quantity <= 0
    inv_service, cat = service
    inv_service.add_product(Product("P01", "Out of stock item", cat, 100, quantity=0, threshold=5))
    inv_service.add_product(Product("P02", "In stock item", cat, 200, quantity=5, threshold=5))
    
    assert inv_service.low_stock_items(0) == ["Out of stock item"]


def test_low_stock_items_negative_threshold(service):
    # 6. threshold ที่ส่งให้เมธอด low_stock_items ติดลบ -> คืน list ว่าง
    inv_service, cat = service
    inv_service.add_product(Product("P01", "Item A", cat, 100, quantity=1, threshold=5))
    
    assert inv_service.low_stock_items(-1) == []

def test_issue_stock_exact_quantity(service):
    # 1. ค่าขอบ: จ่ายเท่ากับจำนวนที่มีอยู่ทั้งหมด (สต็อกต้องเหลือ 0 พอดี)
    inv_service, cat = service
    inv_service.add_product(Product("P01", "Laptop", cat, 20000, quantity=5, threshold=2))
    
    updated = inv_service.issue_stock("P01", 5)
    assert updated.quantity == 0


def test_issue_stock_zero_or_negative_quantity(service):
    # 2. ค่าที่ไม่ควรรับ: จ่ายจำนวน 0 หรือ ติดลบ (ต้อง raise ValueError)
    inv_service, cat = service
    inv_service.add_product(Product("P01", "Laptop", cat, 20000, quantity=5, threshold=2))
    
    with pytest.raises(ValueError):
        inv_service.issue_stock("P01", 0)
        
    with pytest.raises(ValueError):
        inv_service.issue_stock("P01", -3)


def test_issue_stock_exceeds_available_quantity(service):
    # 3. เส้นทาง error: จ่ายเกินจำนวนสต็อกที่มี (ต้อง raise ValueError)
    inv_service, cat = service
    inv_service.add_product(Product("P01", "Laptop", cat, 20000, quantity=5, threshold=2))
    
    with pytest.raises(ValueError):
        inv_service.issue_stock("P01", 10)


def test_issue_stock_product_not_found(service):
    # 4. เส้นทาง error: จ่ายสินค้าที่ไม่มีในคลัง (ต้อง raise Exception)
    inv_service, _ = service
    
    with pytest.raises(Exception):
        inv_service.issue_stock("NON_EXISTENT_ID", 1)


def test_issue_stock_invalid_type(service):
    # 5. ชนิดข้อมูล: ใส่จำนวนเป็น string หรือ float (ต้อง raise ValueError/TypeError)
    inv_service, cat = service
    inv_service.add_product(Product("P01", "Laptop", cat, 20000, quantity=5, threshold=2))
    
    with pytest.raises((ValueError, TypeError)):
        inv_service.issue_stock("P01", "three")  # type: ignore