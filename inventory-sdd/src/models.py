from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    """ประเภทของรายการธุรกรรมสต็อก"""
    IN = "IN"
    OUT = "OUT"


@dataclass
class Category:
    """หมวดหมู่สินค้า"""
    id: str
    name: str

    def __post_init__(self) -> None:
        """ตรวจสอบความถูกต้องของข้อมูลหมวดหมู่สินค้า"""
        if not self.id:
            raise ValueError("รหัสหมวดหมู่สินค้าต้องไม่เป็นค่าว่าง")
        if not self.name:
            raise ValueError("ชื่อหมวดหมู่สินค้าต้องไม่เป็นค่าว่าง")


@dataclass
class Product:
    """ข้อมูลสินค้าและสต็อก"""
    id: str
    name: str
    category: Category
    price_per_unit: float
    quantity: int = 0
    threshold: int = 0

    def __post_init__(self) -> None:
        """ตรวจสอบความถูกต้องของข้อมูลสินค้า"""
        if not self.id:
            raise ValueError("รหัสสินค้าต้องไม่เป็นค่าว่าง")
        if not self.name:
            raise ValueError("ชื่อสินค้าต้องไม่เป็นค่าว่าง")
        if self.price_per_unit < 0:
            raise ValueError("ราคาสินค้าต้องไม่ติดลบ")
        if self.quantity < 0:
            raise ValueError("จำนวนสินค้าต้องไม่ติดลบ")
        if self.threshold <= 0:
            raise ValueError("กรุณากรอกตัวเลขที่มากกว่า 0")


@dataclass
class StockTransaction:
    """บันทึกประวัติการรับเข้าและจ่ายออกสินค้า"""
    id: str
    product_id: str
    transaction_type: TransactionType
    quantity: int
    timestamp: datetime = field(default_factory=datetime.now)
    note: Optional[str] = None

    def __post_init__(self) -> None:
        """ตรวจสอบความถูกต้องของประวัติรายการสต็อก"""
        if self.quantity <= 0:
            raise ValueError("จำนวนรายการสินค้าต้องมากกว่า 0")