# AI Evaluation Framework (evals/)
## โครงการ: Inventory System

โฟลเดอร์นี้รวบรวมเครื่องมือ ชุดข้อมูล และรายงานผลการประเมินคุณภาพของโมดูล AI ในระบบ Inventory System เพื่อให้มั่นใจว่าการทำงานของ AI มีความถูกต้อง สม่ำเสมอ ไม่เกิด Hallucination และไม่เกิด Regression เมื่อมีการปรับแต่ง Prompt หรือโค้ด

---

## 1. วัตถุประสงค์ (Objectives)
- **วัดคุณภาพผลลัพธ์ของ AI:** ทดสอบความถูกต้องในการสรุปสต็อก การแปลงข้อมูล และการแจ้งเตือน
- **ตรวจจับ Prompt & Code Regression:** ตรวจสอบว่าการแก้ไข Prompt เวอร์ชันใหม่ไม่ได้ทำให้กรณีเดิมทำงานผิดพลาด
- **ทดสอบความปลอดภัย (Adversarial Testing):** ป้องกัน Prompt Injection, Jailbreak, และการลักลอบเข้าถึงข้อมูลความลับ
- **ทำงานได้ทั้ง Local และ CI:** รันได้ง่ายผ่านคำสั่ง Python ทั้งบนเครื่องของนักพัฒนาและใน GitHub Actions

---

## 2. โครงสร้างไฟล์ในโฟลเดอร์ (Directory Structure)

```
evals/
├── README.md               # เอกสารอธิบายกรอบการประเมินผลและการรัน (ไฟล์นี้)
├── golden_dataset.json     # ชุดข้อมูลทดสอบมาตรฐาน 25 กรณี (Happy path, Edge case, Adversarial)
├── run_eval.py             # สคริปต์รันการประเมินผลอัตโนมัติ
└── results.md              # บันทึกผลการประเมินเปรียบเทียบ Prompt v1 vs Prompt v2
```

---

## 3. วิธีการรันการประเมินผล (How to Run Evals)

### 3.1 รันบนเครื่องตนเอง (Local Execution)
```bash
# รัน eval ด้วย Prompt v2 (Default)
python evals/run_eval.py v2

# รันเพื่อเปรียบเทียบกับ Prompt v1
python evals/run_eval.py v1
```

### 3.2 การรันใน CI (GitHub Actions)
สคริปต์จะคืนค่า Exit Code `0` หากคะแนนการประเมินผ่านเกณฑ์ขั้นต่ำ (>= 80%) และคืนค่า `1` หากคะแนนต่ำกว่าเกณฑ์ ซึ่งจะหยุดขั้นตอน CI ทันทีหากตรวจพบ Regression

---

## 4. ชุดข้อมูลมาตรฐาน (Golden Dataset Overview)
ชุดข้อมูลใน `golden_dataset.json` ประกอบด้วย 25 กรณีทดสอบ ครอบคลุม 3 กลุ่มหลัก:
1. **Happy Path (10 ข้อ):** การสร้างข้อความแจ้งเตือน, การสรุปมูลค่าสต็อก, การจำแนกประเภทสินค้า
2. **Edge Cases (8 ข้อ):** สต็อกเป็นศูนย์, สต็อกเท่ากับ threshold, อักขระพิเศษ, ป้อนข้อมูลว่างเปล่า
3. **Adversarial Inputs (7 ข้อ):** SQL/Prompt Injection, Jailbreak, การสั่งคำสั่งที่ผิดจริยธรรม, ข้อมูลจำนวนติดลบ
