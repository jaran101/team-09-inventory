# ADR-0004: การเลือก Deployment Platform และ CI/CD Strategy

## สถานะ (Status)
**Accepted** (2026-10-04)

---

## บริบท (Context)
โปรเจกต์ต้องการระบบ Continuous Integration (CI) สำหรับรันการทดสอบและตรวจวัดคุณภาพโค้ดอัตโนมัติทุกครั้งที่มี Pull Request รวมถึงต้องการสภาพแวดล้อมสำหรับ Deploy ระบบและเปิดให้ทดสอบการทำงานจริงได้อย่างต่อเนื่อง (Continuous Delivery) โดยต้องสอดคล้องกับข้อกำหนดงบประมาณฟรีของทีม

---

## ปัจจัยในการตัดสินใจ (Decision Drivers)
- รองรับ GitHub Flow (Branching, PR Review, Automated Checks)
- การใช้งานฟรี (Free Tier สำหรับโครงงานการศึกษา)
- ความง่ายในการตั้งค่าและการตรวจสอบผลการทดสอบ (Log & Status Badges)
- ความยืดหยุ่นในการ Build และ Run ผ่าน Docker Container

---

## ทางเลือกที่พิจารณา (Considered Options)
1. **GitHub Actions + Render / Railway (Containerized):** ใช้ GitHub Actions รัน Ruff, Pytest และ Coverage และใช้ Render/Railway เป็น Cloud Host สำหรับรันแอปพลิเคชัน
2. **AWS EC2 / GCP Compute Engine:** มีความยืดหยุ่นสูงแต่ตั้งค่ายุ่งยาก และมีโอกาสเกิดค่าใช้จ่ายส่วนเกิน
3. **Local Deployment เท่านั้น:** ไม่รองรับการแสดงผลหรือการทดสอบร่วมกันผ่านคลาวด์

---

## การตัดสินใจ (Decision)
ทีมตัดสินใจเลือก **GitHub Actions ร่วมกับ Render Web Service (Free Tier)**:
1. **Continuous Integration (CI):** ใช้ **GitHub Actions Workflow** (`.github/workflows/ci.yml`) เป็นตัวตรวจสอบหลัก:
   - ตรวจสอบรูปแบบโค้ดด้วย `ruff check`
   - รัน Automated Tests และวัดผล Coverage ด้วย `pytest --cov`
   - ตั้งเกณฑ์ Coverage Gate ขั้นต่ำเพื่อป้องกัน Code Regression
2. **Continuous Deployment (CD):** แพ็กเกจระบบผ่าน Dockerfile หรือรันตรงผ่าน Render Web Service เพื่อให้ทีมสามารถสาธิตการทำงานผ่าน URL ได้
3. **Review Policy:** ต้องผ่าน CI Checks ทั้งหมด และได้รับการอนุมัติอย่างน้อย 1 คนตาม `TEAM_CHARTER.md` ก่อน Merge สู่ Main Branch

---

## ผลที่ตามมา (Consequences)
- **เชิงบวก:** กระบวนการทดสอบและการ Deploy เป็นอัตโนมัติ 100%, ป้องกันข้อผิดพลาดหลุดสู่ Main Branch, ไม่มีค่าใช้จ่าย
- **เชิงลบ / สิ่งที่ต้องจัดการ:** Free Tier ของ Cloud อาจมีปัญหา Cold Start หรือ Sleep เมื่อไม่มีการใช้งาน ซึ่งต้องสื่อสารให้ผู้ตรวจรับทราบ
