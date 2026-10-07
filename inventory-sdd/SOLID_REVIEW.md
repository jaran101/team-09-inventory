# รายงานตรวจสอบหลัก SOLID — ระบบจัดการคลังสินค้า (Inventory System)

**ไฟล์ที่ตรวจ:** `models.py`, `notifiers.py`, `service.py`, `main.py`, `inventory_no_context.py` (เวอร์ชันก่อนมี context), `spec.md`, `AI_ITERATION_LOG.md`
**ไฟล์ที่ไม่ได้ตรวจ:** ไฟล์ `.pyc` (bytecode ที่คอมไพล์แล้ว ไม่มีซอร์สให้ตรวจ)

---

## 1. สรุปภาพรวม

| หลักการ | ละเมิดหรือไม่ | ระดับ | จุดที่เกี่ยวข้องหลัก |
|---|---|---|---|
| **S** — Single Responsibility | ละเมิด | สูง | `InventoryService` |
| **O** — Open/Closed | ละเมิดบางส่วน | ปานกลาง | `NotifierFactory.create_notifier`, เงื่อนไขแจ้งเตือนใน `InventoryService` |
| **L** — Liskov Substitution | ไม่ละเมิดโดยตรง (มีความเสี่ยง) | ต่ำ | `Notifier` implementations, `_notify_all` |
| **I** — Interface Segregation | ละเมิดเล็กน้อย | ต่ำ–ปานกลาง | `InventoryService` (อินเทอร์เฟซกว้าง), attribute สาธารณะ |
| **D** — Dependency Inversion | ละเมิดบางส่วน | ปานกลาง | `InventoryService` ผูกกับ dict ในหน่วยความจำ, `uuid` |

**จุดที่ทำได้ดี:** การแยก `Notifier` เป็น `Protocol` และฉีดเข้า `InventoryService` ผ่าน constructor ทำให้เพิ่มช่องทางแจ้งเตือนได้โดยไม่แก้ business logic ซึ่งตรงกับ NFR-02 และ Design Notes ใน spec

---

## 2. S — Single Responsibility Principle

### ละเมิดหรือไม่
**ละเมิด** (ระดับสูง)

### Class / Method ที่เกี่ยวข้อง
- `InventoryService` (ทั้ง class)
  - `update_threshold`
  - `receive_stock`, `issue_stock`
  - `get_stock_value_by_category`
- `main.py` → `main()` (รองรับเป็นรอง)

### อธิบายและผลกระทบ
`InventoryService` มีเหตุผลที่ต้องเปลี่ยนแปลงหลายเหตุผลในคลาสเดียว:

1. **จัดการสต็อก** — บวก/ลบ `product.quantity`
2. **เก็บข้อมูล (persistence)** — ถือ `products`, `categories`, `transactions` ไว้เอง
3. **บันทึกประวัติธุรกรรม** — สร้าง `StockTransaction` และ `uuid` เอง
4. **กำหนดนโยบายและข้อความแจ้งเตือน** — ตัดสินใจว่าเมื่อไรต้องแจ้ง และประกอบข้อความภาษาไทยเอง
5. **แปลงและตรวจสอบ input** — `update_threshold` มีโค้ด parse `str`/`float`/`int` ยาวเกือบ 15 บรรทัด ซึ่งเป็นหน้าที่ของ validation layer
6. **ทำรายงาน** — `get_stock_value_by_category`

ส่วน `main()` ทำทั้งการประกอบ dependency (composition root), seed ข้อมูลตัวอย่าง และวน loop CLI

**ผลกระทบ**
- แก้ถ้อยคำข้อความแจ้งเตือนหรือกฎการแจ้งเตือน ต้องเข้าไปแก้ไฟล์เดียวกับโค้ดตัดสต็อก เสี่ยงทำ logic ส่วนอื่นพัง
- ทดสอบยาก เช่น จะทดสอบ parsing threshold ก็ต้องสร้าง service ทั้งตัว
- คลาสจะบวมเรื่อย ๆ เมื่อเพิ่มฟีเจอร์ (เช่น รายงานชนิดใหม่)

### ข้อเสนอปรับปรุง
แยกความรับผิดชอบออกเป็นคลาส/ฟังก์ชันเล็ก ๆ

```python
# validators.py
def parse_threshold(value: Union[int, float, str]) -> int:
    """แปลงและตรวจสอบค่า threshold (ข้อความ error ตาม AC ของ US-04)"""
    ...

# alert_policy.py
class StockAlertPolicy:
    def after_receive(self, product: Product, old_qty: int) -> Optional[str]: ...
    def after_issue(self, product: Product) -> Optional[str]: ...
    def after_threshold_change(self, product: Product) -> str: ...

# reports.py
class StockReportService:
    def value_by_category(self, products: Iterable[Product]) -> Dict[str, float]: ...

# service.py  — เหลือแค่ประสานงาน (orchestrate)
class InventoryService:
    def __init__(self, repo, notifier, policy, id_generator): ...
```

---

## 3. O — Open/Closed Principle

### ละเมิดหรือไม่
**ละเมิดบางส่วน** (ช่องทางแจ้งเตือนผ่าน — แต่ factory และกฎแจ้งเตือนไม่ผ่าน)

### Class / Method ที่เกี่ยวข้อง
- `NotifierFactory.create_notifier` (ใน `notifiers.py`)
- เงื่อนไข `if/else` แจ้งเตือนใน `InventoryService.receive_stock`, `issue_stock`, `update_threshold`

### อธิบายและผลกระทบ
**3.1 `NotifierFactory.create_notifier`** ใช้ `if/elif` ตรวจชนิดเป็นสตริง ถ้าจะเพิ่ม `LineNotifier` หรือ `SlackNotifier` ต้อง **แก้โค้ดใน factory** (แก้ของเดิม ไม่ใช่ขยายเพิ่ม) ทั้งที่คลาส `Notifier` ออกแบบมาให้เพิ่มได้โดยไม่แก้ของเดิม ทำให้ NFR-02 ได้ผลเพียงครึ่งเดียว

**3.2 กฎการแจ้งเตือนฝังใน service** เช่น `if product.quantity > product.threshold` ใน `receive_stock` ถ้าต้องเพิ่มกฎใหม่ (เช่น แจ้งเตือนระดับวิกฤต หรือแจ้งเฉพาะตอนข้ามเส้น threshold) ต้องแก้ method ที่ทำงานหลักของสต็อก

**ผลกระทบ:** ทุกครั้งที่ขยายความสามารถต้อง "แก้ของเดิมที่ทดสอบแล้ว" เสี่ยงเกิด regression

### ข้อเสนอปรับปรุง
**Factory แบบ registry** — เพิ่มชนิดใหม่โดยไม่แก้ factory:

```python
class NotifierFactory:
    _registry: Dict[str, Callable[[str], Notifier]] = {}

    @classmethod
    def register(cls, name: str, builder: Callable[[str], Notifier]) -> None:
        cls._registry[name.lower()] = builder

    @classmethod
    def create_notifier(cls, notifier_type: str, destination: str) -> Notifier:
        try:
            return cls._registry[notifier_type.lower()](destination)
        except KeyError:
            raise ValueError(f"ไม่รองรับประเภทการแจ้งเตือน: {notifier_type}")

NotifierFactory.register("email", EmailNotifier)
NotifierFactory.register("sms", SMSNotifier)
```

**กฎแจ้งเตือน** — ย้ายไปอยู่ใน `StockAlertPolicy` (ดูหัวข้อ SRP) หรือใช้รายการของ rule object (`List[AlertRule]`) แล้วให้ service วนเรียก เมื่อมีกฎใหม่ก็เพิ่ม rule class โดยไม่แตะ service

---

## 4. L — Liskov Substitution Principle

### ละเมิดหรือไม่
**ไม่ละเมิดโดยตรง** แต่มีความเสี่ยงด้านสัญญา (contract) ที่ไม่ชัดเจน

### Class / Method ที่เกี่ยวข้อง
- `Notifier` (Protocol), `EmailNotifier`, `SMSNotifier`
- `InventoryService._notify_all`

### อธิบายและผลกระทบ
ระบบนี้ไม่ได้ใช้การสืบทอดคลาส และ `EmailNotifier`/`SMSNotifier` ทำตามลายเซ็น `send(message: str) -> None` ของ Protocol ครบ จึงแทนที่กันได้ในปัจจุบัน

**ความเสี่ยง:** Protocol ไม่ได้ระบุว่า `send` **ห้าม raise exception หรือไม่** เมื่อเปลี่ยนจากการ `print` จำลองเป็นการส่งจริง (ซึ่งอาจ timeout/ล้มเหลว) Notifier ตัวหนึ่งที่ raise จะทำให้
1. `_notify_all` หยุดกลางลูป — Notifier ตัวถัดไปไม่ได้รับข้อความ
2. ธุรกรรมที่ตัดสต็อกไปแล้ว (`product.quantity -= quantity`) แต่ผู้เรียกได้รับ error ทำให้ผู้ใช้เข้าใจผิดว่าจ่ายสินค้าไม่สำเร็จ

นั่นคือ Notifier ที่ "ล้มเหลวได้" แทนที่ Notifier ที่ "ไม่ล้มเหลว" ไม่ได้อย่างปลอดภัย ซึ่งเป็นแนวคิดเดียวกับ LSP (พฤติกรรมของ subtype ต้องไม่ทำให้ผู้ใช้ type เดิมพัง)

### ข้อเสนอปรับปรุง
1. ระบุสัญญาใน docstring ของ `Notifier.send` ว่า "ต้องไม่ raise exception ออกมาสู่ผู้เรียก ให้จัดการ/log ภายใน" หรือกำหนด `NotificationError` ชัดเจน
2. ทำให้ `_notify_all` ทนต่อความล้มเหลวของแต่ละช่องทาง

```python
def _notify_all(self, message: str) -> None:
    for notifier in self.notifiers:
        try:
            notifier.send(message)
        except Exception as exc:  # ช่องทางหนึ่งล้ม ต้องไม่กระทบช่องทางอื่น/ธุรกรรม
            logger.warning("ส่งแจ้งเตือนล้มเหลว: %s", exc)
```

---

## 5. I — Interface Segregation Principle

### ละเมิดหรือไม่
**ละเมิดเล็กน้อย**

### Class / Method ที่เกี่ยวข้อง
- `InventoryService` (อินเทอร์เฟซสาธารณะกว้าง)
- attribute สาธารณะ `products`, `categories`, `transactions`
- `main.py` ตัวเลือกเมนู 5 ที่เข้าถึง `service.products.values()` ตรง ๆ

### อธิบายและผลกระทบ
- `Notifier` มีเมธอดเดียว (`send`) ถือว่า **ผ่าน ISP ดี**
- `InventoryService` เปิดเมธอดทั้งรับ/จ่าย/แก้ threshold/รายงาน/เพิ่มหมวดหมู่ ไว้ใน "อินเทอร์เฟซเดียว" ผู้ใช้ที่ต้องการเพียงอ่านรายงาน (เช่น ผู้จัดการ) จึงต้องพึ่งพาเมธอดแก้ไขข้อมูลด้วย ทำให้ mock/ทดสอบยากและแยกสิทธิ์ภายหลังลำบาก
- `main.py` อ่าน `service.products` ตรง ๆ แสดงว่าโครงสร้างภายใน (dict) รั่วออกมา ถ้าเปลี่ยนการเก็บข้อมูลต้องแก้ฝั่ง CLI ด้วย
- `NotifierFactory.create_notifier(notifier_type, destination)` บังคับให้ทุกชนิดใช้พารามิเตอร์ `destination` ตัวเดียว ซึ่งอาจไม่พอสำหรับช่องทางที่ต้องการ config มากกว่านั้น (เช่น token + channel)

### ข้อเสนอปรับปรุง
แยก Protocol ตามบทบาทผู้ใช้:

```python
class StockCommands(Protocol):
    def receive_stock(self, product_id: str, quantity: int) -> Product: ...
    def issue_stock(self, product_id: str, quantity: int) -> Product: ...
    def update_threshold(self, product_id: str, new_threshold: ...) -> Product: ...

class StockQueries(Protocol):
    def list_products(self) -> Tuple[Product, ...]: ...
    def get_stock_value_by_category(self) -> Dict[str, float]: ...
```

และเพิ่มเมธอด `list_products()` ที่คืนค่าแบบ read-only แทนการเปิด dict `products` ตรง ๆ

---

## 6. D — Dependency Inversion Principle

### ละเมิดหรือไม่
**ละเมิดบางส่วน** (ส่วน Notifier ผ่าน, ส่วนจัดเก็บข้อมูลไม่ผ่าน)

### Class / Method ที่เกี่ยวข้อง
- ✅ ผ่าน: `InventoryService.__init__(notifiers: List[Notifier])`
- ❌ ไม่ผ่าน: `InventoryService.__init__` (สร้าง `self.products = {}` เอง), `receive_stock`/`issue_stock` (เรียก `uuid.uuid4()` และสร้าง `StockTransaction` ตรง ๆ)
- `main.py` ผูกกับ `NotifierFactory` และ `InventoryService` แบบ concrete (ยอมรับได้ เพราะเป็น composition root)

### อธิบายและผลกระทบ
**ส่วนที่ดี:** `InventoryService` (high-level) พึ่งพา `Notifier` (abstraction) ไม่ใช่ `EmailNotifier`/`SMSNotifier` ตรง ๆ และรับผ่าน constructor จริงตามที่ `AI_ITERATION_LOG.md` ระบุ

**ส่วนที่ยังละเมิด:** service (นโยบายระดับสูง) ผูกกับกลไกจัดเก็บ concrete คือ `dict` ในหน่วยความจำ และการสร้าง id ด้วย `uuid` ถ้าอนาคตต้องเปลี่ยนไปใช้ฐานข้อมูล (ซึ่งอยู่นอกขอบเขตของ spec ตอนนี้ แต่เป็นการต่อยอดที่น่าจะเกิด) ต้องแก้ตัว service ทั้งก้อน และทดสอบโดยควบคุม `uuid` ไม่ได้

### ข้อเสนอปรับปรุง
```python
class ProductRepository(Protocol):
    def get(self, product_id: str) -> Optional[Product]: ...
    def save(self, product: Product) -> None: ...
    def all(self) -> Iterable[Product]: ...

class InMemoryProductRepository:
    def __init__(self) -> None:
        self._items: Dict[str, Product] = {}
    ...

class InventoryService:
    def __init__(
        self,
        repo: ProductRepository,
        notifiers: Sequence[Notifier],
        id_generator: Callable[[], str] = lambda: str(uuid.uuid4()),
    ) -> None: ...
```

ในทำนองเดียวกันสามารถแยก `TransactionRepository` เพื่อเก็บประวัติธุรกรรม

---

## 7. ไฟล์ `inventory_no_context.py` (เวอร์ชันก่อนมี context)

| หลักการ | ผล | หมายเหตุ |
|---|---|---|
| S | ละเมิด | `InventoryManager` รวมทั้ง lock, จัดเก็บ, กฎแจ้งเตือน, validation (`update_threshold`), รายงาน |
| O | ละเมิดบางส่วน | ไม่มี factory จึงไม่มีปัญหาเรื่อง `if/elif` แต่กฎแจ้งเตือนฝังใน method เหมือนกัน |
| L | ไม่ละเมิด | `ConsoleNotifier`/`EmailNotifier` ทำตาม Protocol |
| I | ผ่าน | `NotificationService` มีเมธอดเดียว |
| D | ผ่านบางส่วน | ใช้ `register_notifier` (ผ่าน setter) แต่ยังสร้าง dict/lock เองใน class |

**เปรียบเทียบกับเวอร์ชันใหม่:** เวอร์ชันใหม่แยกไฟล์ (`models`/`notifiers`/`service`) และฉีด dependency ผ่าน constructor ดีขึ้นในด้านโครงสร้างไฟล์และ DIP แต่ **ปัญหา SRP ของตัว service ยังเหมือนเดิม** และเวอร์ชันใหม่ **ตกหล่นเรื่อง thread-safety** (ดูหัวข้อถัดไป)

---

## 8. ข้อสังเกตเพิ่มเติมนอกเหนือ SOLID (พบระหว่างอ่านโค้ด)

ไม่ใช่การละเมิด SOLID โดยตรง แต่ควรรู้เพราะเกี่ยวกับ spec และคุณภาพโค้ด

1. **NFR-03 (ความปลอดภัยเมื่อแก้ไขพร้อมกัน):** `inventory_no_context.py` มี `threading.Lock` แต่ `service.py` ไม่มี ทำให้ requirement นี้ไม่ได้รับการตอบสนองในเวอร์ชันหลัก
2. **เงื่อนไขแจ้งเตือนตอนรับสินค้าไม่ตรง spec:** `receive_stock` ใน `service.py` ส่งข้อความ "ถูกเติมแล้ว" ทุกครั้งที่ `quantity > threshold` แม้สต็อกเดิมจะสูงกว่า threshold อยู่แล้ว ขณะที่เวอร์ชันเดิมตรวจ `old_stock <= threshold` ด้วย นอกจากนี้ค่า `quantity == threshold` จะถือเป็น "สต็อกต่ำ" ตอนรับเข้า แต่ตอนจ่ายออก (`issue_stock`) ที่ `quantity == threshold` จะไม่แจ้งเตือน (ตรง AC ข้อสาม) ทำให้นิยามขอบเขตไม่สอดคล้องกัน ควรกำหนดเป็นกฎเดียวใน `StockAlertPolicy`
3. **ค่า default ขัดกับ validation:** `Product.threshold` มี default `= 0` แต่ `__post_init__` ปฏิเสธ `threshold <= 0` ทำให้การสร้าง `Product` โดยไม่ระบุ threshold จะ error เสมอ
4. **การเข้าถึง state ตรง ๆ (anemic model):** `service` แก้ `product.quantity` ตรง ๆ ควรย้ายกฎอย่าง "สต็อกพอไหม" ไปเป็นเมธอดของ `Product` (เช่น `product.remove(qty)`) เพื่อห่อหุ้มข้อมูล
5. **Hardcode ค่า config:** `AI_ITERATION_LOG.md` ระบุว่า "ไม่มีการ Hardcode ค่า Config" แต่ใน `main.py` มีอีเมล `manager@company.com` และเบอร์ `081-234-5678` ฝังอยู่ในโค้ด รวมถึงข้อความแจ้งเตือนทั้งหมดใน `service.py` ควรย้ายไปไฟล์ config หรือ environment variable
6. **รายละเอียดเล็กน้อย:** `notifiers.py` import `List` ที่ไม่ได้ใช้; `notifiers: List[Notifier] = None` ควรเป็น `Optional[List[Notifier]]`; `main.py` ใช้ `except Exception` กว้างเกินไป

---

## 9. ลำดับความสำคัญในการปรับปรุงที่แนะนำ

| ลำดับ | งาน | หลักการ | ความยากโดยประมาณ |
|---|---|---|---|
| 1 | แยก `parse_threshold` และ `StockAlertPolicy` ออกจาก service | S, O | ต่ำ |
| 2 | ทำ `NotifierFactory` เป็น registry | O | ต่ำ |
| 3 | ทำให้ `_notify_all` ทนต่อ error + ระบุสัญญาของ `Notifier.send` | L | ต่ำ |
| 4 | เพิ่ม `ProductRepository` + ฉีด `id_generator` | D | ปานกลาง |
| 5 | เพิ่ม lock ใน service (NFR-03) และแก้เงื่อนไขแจ้งเตือนตอนรับสินค้า | นอก SOLID | ต่ำ |
| 6 | แยก `StockCommands` / `StockQueries` และเลิกเปิด dict ตรง ๆ | I | ปานกลาง |
