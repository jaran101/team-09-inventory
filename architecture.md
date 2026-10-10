# สถาปัตยกรรมระบบ (System Architecture)
## โครงการ: Inventory System

เอกสารนี้อธิบายโครงสร้างสถาปัตยกรรม การออกแบบโมดูล และการไหลของข้อมูล (Data Flow) ภายในระบบ Inventory System โดยยึดหลัก Clean Architecture และ SOLID Principles

---

## 1. ภาพรวมสถาปัตยกรรม (Architectural Overview)

ระบบ Inventory System ออกแบบในรูปแบบ **Layered Domain-Centric Architecture** เพื่อแยกส่วนของ Business Logic ออกจากกลไกภายนอก (เช่น ช่องทางส่งข้อความ การติดต่อผู้ใช้ หรือฐานข้อมูล):

```
+-------------------------------------------------------------+
|                     Presentation Layer                      |
|                  (CLI Menu, Web API / UI)                   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                       Service Layer                         |
|                    (InventoryService)                       |
|   - จัดการกฎทางธุรกิจ (Receive, Issue, Threshold, Valuation)      |
|   - ประสานงานระหว่าง Models และ Notifiers                       |
+-------------------------------------------------------------+
            |                                         |
            v                                         v
+-----------------------+                 +-------------------------+
|     Domain Layer      |                 |   Infrastructure Layer  |
|  (Core Business Data) |                 |     (External Output)   |
| - Product             |                 | - Notifier Interface    |
| - Category            |                 | - EmailNotifier         |
| - StockTransaction    |                 | - SMSNotifier           |
+-----------------------+                 | - NotifierFactory       |
                                          +-------------------------+
```

---

## 2. โครงสร้างคลาสและการเชื่อมโยง (Class Diagram)

สถาปัตยกรรมภายในถูกออกแบบให้แยกหน้าที่ตามหลัก OOP โดยมี `InventoryService` ทำหน้าที่เป็น Facade/Service หลัก และรับ Notifiers ผ่าน Dependency Injection:

```mermaid
classDiagram
    class TransactionType {
        <<enumeration>>
        IN
        OUT
    }
    
    class Category {
        +id: str
        +name: str
    }
    
    class Product {
        +id: str
        +name: str
        +category: Category
        +price_per_unit: float
        +quantity: int
        +threshold: int
    }
    
    class StockTransaction {
        +id: str
        +product_id: str
        +transaction_type: TransactionType
        +quantity: int
        +timestamp: datetime
        +note: Optional[str]
    }
    
    class Notifier {
        <<interface>>
        +send(message: str) void
    }
    
    class EmailNotifier {
        -recipient_email: str
        +send(message: str) void
    }
    
    class SMSNotifier {
        -phone_number: str
        +send(message: str) void
    }
    
    class NotifierFactory {
        +create_notifier(notifier_type: str, destination: str) Notifier
    }
    
    class InventoryService {
        -products: Dict[str, Product]
        -categories: Dict[str, Category]
        -transactions: List[StockTransaction]
        -notifiers: List[Notifier]
        +add_category(category: Category) void
        +add_product(product: Product) void
        +receive_stock(product_id: str, quantity: int) Product
        +issue_stock(product_id: str, quantity: int) Product
        +update_threshold(product_id: str, new_threshold: int) Product
        +get_stock_value_by_category() Dict[str, float]
        -_notify_all(message: str) void
    }
    
    Product "1" --> "1" Category: uses
    Product "1" --> "1" TransactionType: references
    StockTransaction --> TransactionType: uses
    
    EmailNotifier ..|> Notifier: implements
    SMSNotifier ..|> Notifier: implements
    NotifierFactory --> Notifier: creates
    
    InventoryService --> Product: manages
    InventoryService --> Category: manages
    InventoryService --> StockTransaction: creates
    InventoryService --> Notifier: uses (dependency injection)
```

---

## 3. ลำดับการทำงานและการไหลของข้อมูล (Sequence Diagram)

ขั้นตอนการจ่ายสินค้าออก (`issue_stock`) ซึ่งมีการตรวจสอบเงื่อนไขความถูกต้องและการแจ้งเตือนสต็อกต่ำ:

```mermaid
sequenceDiagram
    participant Employee as 👤 Employee
    participant Service as InventoryService
    participant ProductStore as Product Store
    participant TransLog as StockTransaction Log
    participant Notifier1 as EmailNotifier
    participant Notifier2 as SMSNotifier
    
    Employee->>Service: issue_stock(product_id, quantity)
    activate Service
    
    rect rgb(230, 240, 255)
        Note over Service: 1. ตรวจสอบความถูกต้อง (Validation Phase)
        Service->>Service: ตรวจสอบ product_id มีอยู่จริง
        Service->>Service: ตรวจสอบ quantity > 0
    end
    
    Service->>ProductStore: ค้นหาข้อมูลสินค้าตาม ID
    activate ProductStore
    ProductStore-->>Service: คืนค่า Product
    deactivate ProductStore
    
    rect rgb(255, 240, 230)
        Note over Service: 2. ตรวจสอบสต็อกคงเหลือ
        Service->>Service: ตรวจสอบ quantity <= product.quantity (ไม่ติดลบ)
    end
    
    rect rgb(230, 255, 230)
        Note over Service: 3. ปรับปรุงยอดสต็อก
        Service->>ProductStore: ตัดสต็อก (quantity -= amount)
    end
    
    Service->>TransLog: บันทึก StockTransaction (OUT)
    
    opt สต็อกคงเหลือใหม่ < threshold
        Note over Service: 4. สต็อกต่ำกว่าเกณฑ์ -> ส่งแจ้งเตือน
        Service->>Notifier1: send("สินค้า ... สต็อกต่ำเหลือ X ชิ้น")
        Service->>Notifier2: send("สินค้า ... สต็อกต่ำเหลือ X ชิ้น")
    end
    
    Service-->>Employee: คืนค่า Product ที่อัปเดตแล้ว
    deactivate Service
```

---

## 4. หลักการออกแบบที่นำมาใช้ (Key Design Principles)

### 4.1 Dependency Inversion Principle (DIP) & Dependency Injection (DI)
- `InventoryService` ไม่ผูกติดกับ `EmailNotifier` หรือ `SMSNotifier` โดยตรง แต่เรียกใช้ผ่าน Abstraction `Notifier`
- การส่งรายชื่อ Notifiers เข้าไปใน Service ทำผ่าน Constructor Injection ทำให้ง่ายต่อการเขียน Mock Test และเพิ่มช่องทางแจ้งเตือนใหม่ในอนาคต (เช่น Line Notify, Slack)

### 4.2 Single Responsibility Principle (SRP)
- **Domain Models (`Product`, `Category`):** มีหน้าที่เก็บข้อมูลและตรวจสอบความถูกต้องของข้อมูลตนเอง (Self-validation)
- **`InventoryService`:** ควบคุม Business Workflow (รับ, จ่าย, ตรวจสอบสต็อก, คำนวณมูลค่า)
- **`Notifier` Classes:** รับผิดชอบเฉพาะการส่งข้อความไปยังช่องทางที่ตนเองดูแล

### 4.3 Open/Closed Principle (OCP)
- หากต้องการเพิ่มช่องทางการแจ้งเตือนใหม่ เช่น `DiscordNotifier` สามารถสร้างคลาสใหม่ที่สืบทอดจาก `Notifier` แล้วส่งเข้า Service ได้ทันที โดยไม่ต้องแก้ไขโค้ดใด ๆ ใน `InventoryService`
