# เทคโนโลยีที่ใช้ในระบบ (Technology Stack)
## โครงการ: Inventory System

เอกสารนี้ระบุรายการเทคโนโลยี ไลบรารี และเครื่องมือที่เลือกใช้ในการพัฒนาและดูแลระบบ Inventory System

---

## 1. ภาษาและแพลตฟอร์มหลัก (Core Platform & Language)
- **ภาษาหลัก:** Python 3.10+ (ใช้ Type Hints แบบมาตรฐาน `dict[str, Any]`, `list[T]`, `Optional[T]`)
- **เหตุผลที่เลือก:** ภาษาที่กระชับ เหมาะสำหรับการพัฒนา Domain-Driven Design, มี Ecosystem เครื่องมือทดสอบและ AI ที่แข็งแกร่ง

---

## 2. การจัดการโค้ดและการทดสอบ (Testing & Code Quality)
- **Test Framework:** `pytest` (v7.x+) สำหรับ Automated Unit Tests และ Characterization Tests
- **Test Coverage:** `pytest-cov` / `coverage.py` สำหรับวัด Test Coverage และค้นหา Test Gaps
- **Linter & Formatter:** `ruff` (กำหนดค่าใน `pyproject.toml`) ตรวจจับสไตล์โค้ด ตรวจสอบ Type Hints และ Clean Code ตามกฎ E, F, I, UP
- **CI/CD Pipeline:** GitHub Actions สำหรับรัน Lint, Test และตรวจวัด Coverage Gate อัตโนมัติทุกครั้งที่เปิด Pull Request

---

## 3. สถาปัตยกรรมและการออกแบบระบบ (Architecture & Design Patterns)
- **รูปแบบสถาปัตยกรรม:** Layered Architecture / Clean Domain Separation
  - **Domain / Models:** ข้อมูลและ Validation Logic (`Product`, `Category`, `StockTransaction`)
  - **Service Layer:** ตรรกะทางธุรกิจหลัก (`InventoryService`)
  - **Notification Layer:** ช่องทางส่งข้อความภายนอกผ่าน Interface (`Notifier`, `EmailNotifier`, `SMSNotifier`)
- **Design Patterns ที่ใช้:**
  - **Dependency Injection (DI):** ส่ง Notifiers เข้าไปยัง Service ผ่าน Constructor เพื่อลดการผูกมัด (DIP)
  - **Factory Pattern:** `NotifierFactory` สำหรับสร้าง Object การแจ้งเตือนตามประเภท
  - **Observer / Publisher-Subscriber:** แจ้งเตือนผู้รับหลายช่องทางเมื่อสต็อกสินค้าตกเกณฑ์

---

## 4. ฐานข้อมูลและการจัดเก็บข้อมูล (Data Storage)
- **ปัจจุบัน (Current MVP):** In-Memory Storage โครงสร้าง Dict/List ภายใน Service เพื่อความรวดเร็วในการทดสอบและการพัฒนาตาม TDD
- **แผนขยายในอนาคต (Target):** SQLite / PostgreSQL ผ่าน Repository Interface โดยไม่กระทบ Service Layer

---

## 5. ส่วนประกอบปัญญาประดิษฐ์ (AI & LLM Components)
- **เป้าหมาย:** ระบบ AI Assistant สำหรับช่วยสรุปสถานะสินค้า แนะนำการสั่งซื้อสินค้าเมื่อสต็อกต่ำ และวิเคราะห์แนวโน้มสินค้า
- **โมเดลที่รองรับ:** Google Gemini API / Groq API (และมี Fallback เป็น Local Open-source LLM ผ่าน Ollama)
- **เครื่องมือประเมินผล AI:** ชุดทดสอบ Golden Dataset ใน `evals/` สำหรับวัดคุณภาพ Prompt และป้องกัน Prompt Regression

---

## 6. สภาพแวดล้อมและการดีพลอย (Environment & Deployment)
- **Package Management:** `pip` + `pyproject.toml` / `requirements.txt`
- **Environment Isolation:** Python Virtual Environment (`venv`)
- **Target Deployment Platform:** Render / Railway หรือ Containerized Runner ผ่าน Docker

---

## 7. สรุปตารางเครื่องมือและเวอร์ชัน (Summary Table)

| หมวดหมู่ | เทคโนโลยี / เครื่องมือ | วัตถุประสงค์การใช้งาน |
|---|---|---|
| Language | Python 3.10+ | พัฒนาระบบ Core Logic & Services |
| Test Runner | Pytest | รัน Unit Tests และ Evals อัตโนมัติ |
| Coverage | Coverage.py / pytest-cov | วัดความครอบคลุมของการทดสอบ |
| Code Quality | Ruff | Linting & Formatting แบบรวดเร็ว |
| Architecture | SOLID / DI / Factory | ออกแบบโครงสร้างระบบให้ขยายง่ายและไม่ผูกติด |
| Version Control | Git / GitHub Flow | บริหารจัดการ Source Code ร่วมกันในทีม |
| CI Pipeline | GitHub Actions | รัน Automated Check ก่อน Merge PR |
| AI Evals | Pytest + JSON Golden Dataset | ตรวจสอบความสม่ำเสมอของผลลัพธ์จาก AI |
