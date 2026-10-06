# discount.py  -- โมดูลคิดส่วนลดและสรุปยอด (มี bug จงใจ)

def apply_discount(price: float, percent: float) -> float:
    """คำนวณราคาสินค้าหลังหักส่วนลดเป็นเปอร์เซ็นต์ (0-100)"""
    if not (0 <= percent <= 100):
        raise ValueError("เปอร์เซ็นต์ส่วนลดต้องอยู่ระหว่าง 0 ถึง 100")
    return price * (1 - percent / 100)


def bulk_total(prices: list[float], percent: float) -> float:
    """คำนวณราคารวมของรายการสินค้าหลังหักส่วนลด"""
    return sum(apply_discount(p, percent) for p in prices)


def average_price(prices: list[float]) -> float:
    """คืนราคาเฉลี่ยของรายการสินค้า"""
    if not prices:
        return 0.0
    return sum(prices) / len(prices)


def cheapest_n(prices: list[float], n: int) -> list[float]:
    """คืนรายการราคาที่ถูกที่สุด n อันดับแรก"""
    if not prices or n <= 0:
        return []
    return sorted(prices)[:n]