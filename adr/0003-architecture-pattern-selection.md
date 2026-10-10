# ADR-0003: การเลือก Architecture Pattern และการจัดการ Dependency

## สถานะ (Status)
**Accepted** (2026-10-03)

---

## บริบท (Context)
ระบบเดิมในระยะแรกเริ่ม (`inventory.py`) มีแนวโน้มที่จะรวมการตรวจสอบข้อมูล การจัดการสต็อก การคำนวณราคา และการส่งข้อความไว้ในคลาสเดียวกัน ซึ่งเสี่ยงต่อการเกิด Tight Coupling และละเมิดหลัก Single Responsibility Principle (SRP) และ Dependency Inversion Principle (DIP) ทำให้เขียน Mock Test สำหรับช่องทางแจ้งเตือนได้ยาก

---

## ปัจจัยในการตัดสินใจ (Decision Drivers)
- ความสามารถในการแยกส่วนตรรกะทางธุรกิจ (Business Rules) ออกจากการส่งแจ้งเตือนภายนอก (Email, SMS)
- ความง่ายในการเขียน Unit Test แบบ Isolated (ไม่ต้องเชื่อมต่อเซิร์ฟเวอร์ SMTP/SMS จริง)
- รองรับการขยายช่องทางแจ้งเตือนใหม่ ๆ ในอนาคต (Open/Closed Principle)
- ความชัดเจนของโครงสร้างโฟลเดอร์สำหรับสมาชิกในทีม

---

## ทางเลือกที่พิจารณา (Considered Options)
1. **Layered Domain-Centric Architecture with Dependency Injection:** แยก Domain Models, Service Layer และ Notifier Interface ออกจากกันชัดเจน
2. **Monolithic Script Style:** รวมตรรกะทั้งหมดไว้ในโมดูลเดียวเพื่อความกระชับ
3. **Microservices Architecture:** แยก Service แจ้งเตือนและจัดการสินค้าเป็นอิสระต่อกัน (ซับซ้อนเกินไปสำหรับโปรเจกต์ระดับนี้)

---

## การตัดสินใจ (Decision)
ทีมตัดสินใจเลือก **Layered Architecture ร่วมกับ Dependency Injection (DI) และ Factory Pattern**:
1. **Domain Layer:** คลาส `Product`, `Category`, `StockTransaction` เก็บเฉพาะข้อมูลและการตรวจสอบความถูกต้องเบื้องต้น
2. **Service Layer:** `InventoryService` จัดการกฎสต็อก การตัดสต็อก และการแจ้งเตือน
3. **Notifier Interface & Factory:** สร้าง `Notifier` Interface ที่มีเมธอด `send()` และใช้ `NotifierFactory` ในการสร้าง Instance
4. **Constructor Injection:** ส่ง Notifier เข้าไปยัง `InventoryService` ผ่าน Constructor ทำให้ในการรัน Unit Test สามารถส่ง Mock/Fake Notifier เข้าไปได้โดยตรง

---

## ผลที่ตามมา (Consequences)
- **เชิงบวก:** โค้ดตรงตามหลัก SOLID 100%, ทดสอบได้ง่ายมากด้วย Pytest โดยไม่ต้องพึ่งระบบภายนอก, ขยายระบบแจ้งเตือนใหม่ได้ทันที
- **เชิงลบ / สิ่งที่ต้องจัดการ:** จำนวนไฟล์และคลาสเพิ่มขึ้น สมาชิกในทีมต้องเข้าใจรูปแบบการส่ง Dependency ผ่าน Constructor
