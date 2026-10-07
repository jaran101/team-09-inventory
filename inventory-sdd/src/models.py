from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Optional, Union


class TransactionType(Enum):
    """ประเภทของรายการธุรกรรมสต็อก"""
    IN = "IN"
    OUT = "OUT"


def _is_int(value: Any) -> bool:
    """ตรวจว่าเป็น int จริง (ไม่นับ bool)"""
    return isinstance(value, int) and not isinstance(value, bool)


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
    """ข้อมูลสินค้าและสต็อก

    quantity / threshold / price_per_unit ถูกตรวจสอบทุกครั้งที่กำหนดค่า
    (รวมถึงการกำหนดค่าหลังสร้างอ็อบเจ็กต์) เพื่อไม่ให้ข้อมูลผิดหลุดเข้าระบบ
    ราคาเก็บเป็น Decimal เพื่อหลีกเลี่ยงความคลาดเคลื่อนของ float
    """
    id: str
    name: str
    category: Category
    price_per_unit: Union[Decimal, float, int, str]
    quantity: int = 0
    threshold: int = 1

    def __setattr__(self, name: str, value: Any) -> None:
        """ตรวจสอบและแปลงค่าของ field ตัวเลขก่อนกำหนดค่า"""
        if name == "price_per_unit":
            try:
                if isinstance(value, bool):
                    raise InvalidOperation
                value = Decimal(str(value))
                if not value.is_finite():
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                raise ValueError("ราคาสินค้าต้องเป็นตัวเลข")
            if value < 0:
                raise ValueError("ราคาสินค้าต้องไม่ติดลบ")
        elif name == "quantity":
            if not _is_int(value):
                raise ValueError("จำนวนสินค้าต้องเป็นจำนวนเต็ม")
            if value < 0:
                raise ValueError("จำนวนสินค้าต้องไม่ติดลบ")
        elif name == "threshold":
            if not _is_int(value):
                raise ValueError("กรุณากรอกค่าเป็นตัวเลข")
            if value <= 0:
                raise ValueError("กรุณากรอกตัวเลขที่มากกว่า 0")
        object.__setattr__(self, name, value)

    def __post_init__(self) -> None:
        """ตรวจสอบรหัสและชื่อสินค้า (ตัวเลขถูกตรวจใน __setattr__ แล้ว)"""
        if not self.id:
            raise ValueError("รหัสสินค้าต้องไม่เป็นค่าว่าง")
        if not self.name:
            raise ValueError("ชื่อสินค้าต้องไม่เป็นค่าว่าง")


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
