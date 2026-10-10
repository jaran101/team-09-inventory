# ADR-0001: การเลือก Backend Framework และ Core Execution Model

## สถานะ (Status)
**Accepted** (2026-10-01)

---

## บริบท (Context)
ระบบ Inventory System จำเป็นต้องมีกลไกประมวลผลตรรกะสินค้าคงคลังที่มีความแม่นยำสูง ปฏิบัติตามกฎ Acceptance Criteria (US-01 ถึง US-05) และรองรับการเรียกใช้งานทั้งแบบ CLI และการเปิดเป็น Web API / Integration Interface ในอนาคต

---

## ปัจจัยในการตัดสินใจ (Decision Drivers)
- ความเร็วและง่ายต่อการพัฒนาและเขียน Automated Unit Test
- การรองรับ Type Hinting ที่เข้มงวดเพื่อลด Bug
- ความสามารถในการเชื่อมต่อกับส่วนติดต่อผู้ใช้ (CLI Menu และ REST API)
- ความเข้ากันได้กับ CI/CD Pipeline (GitHub Actions) และ Ruff / Pytest

---

## ทางเลือกที่พิจารณา (Considered Options)
1. **Python Pure Domain Service + FastAPI:** แยก Core Logic เป็น Pure Python Service แล้วหุ้มด้วย FastAPI สำหรับ Web API
2. **Django Framework:** Full-stack framework ที่มี ORM และ Admin Panel ในตัว
3. **Pure CLI Script:** เขียนเป็น Script เดี่ยวรันผ่าน Terminal

---

## การตัดสินใจ (Decision)
ทีมตัดสินใจเลือก **Python Pure Domain Service + FastAPI**:
- พัฒนา Core Business Logic เป็น Pure Python Modules (`src.models`, `src.service`) ที่เป็นอิสระจาก Framework เพื่อให้ทดสอบได้ง่ายด้วย Pytest 100%
- ในระยะแรกใช้ Interactive CLI สำหรับการรันและทดสอบระบบ (`main.py`)
- หากต้องการเปิดเชื่อมต่อ Web Interface จะใช้ FastAPI มาเรียกใช้ `InventoryService` โดยตรง

---

## ผลที่ตามมา (Consequences)
- **เชิงบวก:** Core Logic เป็นอิสระ (Decoupled), ความเร็วในการรัน Test สูงมาก, ไม่ผูกติดกับ Heavy Framework
- **เชิงลบ / สิ่งที่ต้องจัดการ:** หากต้องการต่อ Database หรือจัดการ Session ต้องเขียน Abstraction เพิ่มเติมเอง
