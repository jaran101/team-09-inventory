# Sequence Diagrams - Inventory System

เอกสารนี้รวบรวม Sequence Diagrams แสดงลำดับการทำงาน (Interaction & Data Flow) ของระบบ Inventory System ตามหลัก Clean Architecture และ SOLID Principles

---

## 1. การจ่ายสินค้าออก (Issue Stock Flow)
ครอบคลุมการตรวจสอบความถูกต้อง, การตรวจสอบสต็อกคงเหลือ (ทั้งกรณีปกติ, สินค้าหมด, และสินค้าไม่พอ), การบันทึกธุรกรรม และการแจ้งเตือนผ่าน Notifiers แบบ Multi-channel

```mermaid
sequenceDiagram
    autonumber
    actor Employee as 👤 Employee / CLI
    participant Service as InventoryService
    participant Product as Product (Domain)
    participant TransLog as StockTransaction Log
    participant Notifier as Notifier Interface
    participant Email as EmailNotifier
    participant SMS as SMSNotifier

    Employee->>Service: issue_stock(product_id, quantity)
    activate Service

    rect rgb(235, 245, 255)
        Note over Service: 1. Input Validation
        Service->>Service: ตรวจสอบ quantity เป็นจำนวนเต็ม และ > 0
        alt quantity <= 0 หรือไม่ใช่จำนวนเต็ม
            Service-->>Employee: raise ValueError
        end
    end

    rect rgb(255, 248, 230)
        Note over Service: 2. Lock & Retrieve Product
        Service->>Service: เข้าสู่ Thread Lock (RLock)
        Service->>Product: ค้นหาสินค้าจาก products[product_id]
        alt ไม่พบสินค้า
            Service-->>Employee: raise KeyError("ไม่พบสินค้าในระบบ")
        end
    end

    rect rgb(255, 235, 235)
        Note over Service: 3. Stock Level Check
        alt product.quantity == 0 (สินค้าหมด)
            Service->>Service: เตรียมข้อความแจ้งเตือน "ไม่มีสินค้าในสต็อก"
            Service->>Service: เตรียมข้อผิดพลาด ValueError
        else product.quantity < quantity (สต็อกไม่พอ)
            Service->>Service: เตรียมข้อความแจ้งเตือน "สินค้าในสต็อกไม่พอ"
            Service->>Service: เตรียมข้อผิดพลาด ValueError
        else สต็อกเพียงพอ (Normal Path)
            Note over Service, Product: 4. Deduct Stock & Record Transaction
            Service->>Product: quantity -= amount
            Service->>TransLog: append(StockTransaction: Type.OUT)
            opt product.quantity < threshold (สต็อกต่ำกว่าเกณฑ์)
                Service->>Service: เตรียมข้อความแจ้งเตือน "สต็อกต่ำกว่า threshold"
            end
        end
    end

    Service->>Service: ปล่อย Thread Lock

    rect rgb(240, 255, 240)
        Note over Service, SMS: 5. Notification Phase (Non-blocking)
        opt มีข้อความแจ้งเตือน (messages)
            Service->>Notifier: _notify_all(messages)
            activate Notifier
            par แจ้งเตือนผ่าน Email
                Notifier->>Email: send(message)
            and แจ้งเตือนผ่าน SMS
                Notifier->>SMS: send(message)
            end
            deactivate Notifier
        end
    end

    alt กรณีมี Error เกิดขึ้น (สต็อกหมด หรือไม่พอ)
        Service-->>Employee: raise ValueError(error_message)
    else จ่ายสินค้าสำเร็จ
        Service-->>Employee: คืนค่า Product ที่อัปเดตแล้ว
    end
    deactivate Service
```

---

## 2. การรับสินค้าเข้าคลัง (Receive Stock Flow)
แสดงลำดับการบันทึกเพิ่มสินค้าเข้าคลัง, การบันทึกธุรกรรมประเภท `IN` และการแจ้งเตือนกรณีสต็อกถูกเติมเต็มหรือสต็อกยังคงต่ำกว่าเกณฑ์

```mermaid
sequenceDiagram
    autonumber
    actor Employee as 👤 Employee / CLI
    participant Service as InventoryService
    participant Product as Product (Domain)
    participant TransLog as StockTransaction Log
    participant Notifier as Notifier (Email/SMS)

    Employee->>Service: receive_stock(product_id, quantity)
    activate Service

    Service->>Service: ตรวจสอบ quantity > 0
    Service->>Service: เข้าสู่ Thread Lock (RLock)
    Service->>Product: ค้นหาสินค้าจาก products[product_id]

    Note over Service, Product: บันทึกสถานะก่อนเติม (was_low = quantity < threshold)
    Service->>Product: quantity += amount
    Service->>TransLog: append(StockTransaction: Type.IN)

    alt product.quantity < threshold
        Service->>Service: แจ้งเตือน: "สินค้าในสต็อกต่ำ ... สต็อกคงเหลือ X"
    else was_low == True (เดิมต่ำ แต่ตอนนี้เติมพ้นเกณฑ์แล้ว)
        Service->>Service: แจ้งเตือน: "สินค้า ... ถูกเติมแล้ว สต็อกคงเหลือ X"
    end

    Service->>Service: ปล่อย Thread Lock

    opt มีข้อความแจ้งเตือน
        Service->>Notifier: _notify_all(messages)
    end

    Service-->>Employee: คืนค่า Product ที่อัปเดตแล้ว
    deactivate Service
```

---

## 3. การปรับปรุงเกณฑ์แจ้งเตือน (Update Threshold Flow)

```mermaid
sequenceDiagram
    autonumber
    actor Manager as 👤 Manager / CLI
    participant Service as InventoryService
    participant Product as Product (Domain)
    participant Notifier as Notifier (Email/SMS)

    Manager->>Service: update_threshold(product_id, new_threshold)
    activate Service

    Service->>Service: แปลงค่า & ตรวจสอบ new_threshold > 0
    Service->>Service: เข้าสู่ Thread Lock (RLock)
    Service->>Product: ค้นหาสินค้าจาก products[product_id]
    Service->>Product: product.threshold = new_threshold

    alt product.quantity < new_threshold
        Service->>Service: ข้อความ: "เปลี่ยน threshold เป็น X และสินค้าในสต็อกต่ำ"
    else
        Service->>Service: ข้อความ: "เปลี่ยน threshold เป็น X"
    end

    Service->>Service: ปล่อย Thread Lock
    Service->>Notifier: _notify_all([message])
    Service-->>Manager: คืนค่า Product ที่อัปเดตแล้ว
    deactivate Service
```

---

## 4. การเริ่มต้นระบบและการทำ Dependency Injection (System Setup)

```mermaid
sequenceDiagram
    autonumber
    actor Main as CLI main()
    participant Factory as NotifierFactory
    participant Email as EmailNotifier
    participant SMS as SMSNotifier
    participant Service as InventoryService

    Main->>Factory: create("email", "manager@company.com")
    Factory-->>Email: new EmailNotifier(...)
    Factory-->>Main: instance of EmailNotifier

    Main->>Factory: create("sms", "081-234-5678")
    Factory-->>SMS: new SMSNotifier(...)
    Factory-->>Main: instance of SMSNotifier

    Main->>Service: new InventoryService(notifiers=[email, sms])
    activate Service
    Service-->>Main: service instance พร้อมทำงาน
    deactivate Service
```
