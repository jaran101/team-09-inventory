# คู่มือการติดตั้งและปฏิบัติการระบบ (System Runbook)
## โครงการ: Inventory System

เอกสารฉบับนี้เป็นคู่มือแนะนำขั้นตอนการติดตั้ง การรันระบบ การทดสอบ การตรวจสอบคุณภาพโค้ด และแนวทางการแก้ไขปัญหา (Troubleshooting) สำหรับนักพัฒนาและผู้ดูแลระบบ

---

## 1. ข้อกำหนดของระบบ (Prerequisites)
- **ระบบปฏิบัติการ:** Windows, macOS หรือ Linux
- **Python:** เวอร์ชัน 3.10 หรือสูงกว่า
- **Git:** สำหรับการดึงและจัดการซอร์สโค้ด

---

## 2. ขั้นตอนการติดตั้ง (Installation & Setup)

### 2.1 โคลน Repository และเข้าสู่ไดเรกทอรี
```bash
git clone https://github.com/jran101/team-09-inventory.git
cd team-09-inventory
```

### 2.2 สร้างและเปิดใช้งาน Virtual Environment (venv)
```bash
# บน Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# บน macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2.3 ติดตั้ง Dependencies
```bash
pip install --upgrade pip
pip install -r tests/requirements.txt
```

*(หมายเหตุ: แพ็กเกจหลักที่ติดตั้งประกอบด้วย `pytest`, `pytest-cov`, `ruff`)*

---

## 3. การรันระบบ (Running the Application)

### 3.1 การรันระบบหลักแบบ Interactive CLI (Inventory SDD Core)
```bash
python inventory-sdd/main.py
```
- ระบบจะเปิดเมนูสำหรับบันทึกการรับสินค้าเข้า, จ่ายสินค้าออก, แก้ไข Threshold, และดูรายงานมูลค่าสต็อกตามหมวดหมู่

### 3.2 การรันโมดูลต้นแบบ (Core Module)
```bash
python inventory.py
```

---

## 4. การทดสอบและการวัดความครอบคลุม (Testing & Coverage)

### 4.1 รัน Automated Unit Tests
```bash
pytest
```

### 4.2 รันการทดสอบแบบแสดงรายละเอียด
```bash
pytest -v
```

### 4.3 ตรวจวัด Test Coverage
```bash
pytest --cov=inventory-sdd/src --cov=inventory --cov-report=term-missing
```

---

## 5. การตรวจสอบรูปแบบโค้ด (Linting & Code Quality)

### 5.1 ตรวจสอบความถูกต้องของสไตล์โค้ดด้วย Ruff
```bash
ruff check .
```

### 5.2 สั่งแก้ไขปัญหาสไตล์โค้ดอัตโนมัติ
```bash
ruff check --fix .
```

---

## 6. การประเมินผลโมดูล AI (Running AI Evals)

รันชุดทดสอบคุณภาพของ AI และตรวจสอบการเกิด Prompt Regression:
```bash
# รันการประเมินผลด้วย Prompt v2
python evals/run_eval.py v2

# รันเพื่อเปรียบเทียบผลลัพธ์กับ Prompt v1
python evals/run_eval.py v1
```

---

## 7. คู่มือการแก้ไขปัญหาเบื้องต้น (Troubleshooting Guide)

| อาการ / ข้อผิดพลาด | สาเหตุที่เป็นไปได้ | แนวทางการแก้ไข |
|---|---|---|
| `ValueError: จำนวนสินค้าต้องไม่ติดลบ` | มีการส่งจำนวนรับเข้าหรือจ่ายออกที่มีค่าน้อยกว่าหรือเท่ากับศูนย์ | ตรวจสอบข้อมูลนำเข้า ให้กรอกเฉพาะจำนวนเต็มบวกเท่านั้น |
| `KeyError: ไม่พบสินค้า '...' ในระบบ` | รหัสหรือชื่อสินค้าไม่มีอยู่ในระบบ | ตรวจสอบ ID สินค้าผ่านเมนูแสดงรายการสินค้าก่อนทำรายการ |
| `ValueError: สต็อกคงเหลือไม่เพียงพอ` | พยายามจ่ายสินค้าออกมากกว่าจำนวนที่มีอยู่ในคลัง | ตรวจสอบยอดคงเหลือจริงก่อนทำการจ่ายออก |
| `ruff` รายงานข้อผิดพลาดตอนทำ PR | มีการจัดฟอร์แมตหรือ import ที่ไม่ตรงตามมาตรฐาน | รันคำสั่ง `ruff check --fix .` ในเครื่องตนเองก่อนเปิด PR |
| Pytest หาโมดูลใน `src` ไม่พบ | ไม่ได้ตั้งค่า `PYTHONPATH` | ให้รันคำสั่งโดยระบุ PYTHONPATH เช่น `python -m pytest` จาก Root ของโปรเจกต์ |
| สคริปต์ `run_eval.py` ล้มเหลว | ไม่พบไฟล์ `golden_dataset.json` | ตรวจสอบให้แน่ใจว่าไฟล์อยู่ในไดเรกทอรี `evals/` |

---

## 8. ขั้นตอนการนำขึ้นระบบและการส่งมอบงาน (Deployment & Release)
1. ตรวจสอบว่าโค้ดผ่าน CI บน Branch ของตนเอง (ทั้ง Ruff, Pytest และ Evals ผ่าน 100%)
2. สร้าง Pull Request ไปยัง branch `main`
3. ให้สมาชิกในทีมอย่างน้อย 1 คนรีวิวและ Approve ตามนโยบายใน `TEAM_CHARTER.md`
4. Merge เข้าสู่ `main` เมื่อการตรวจสอบครบถ้วน
