# Inventory System

## 1. บทนำ (Project Overview)
**Inventory System** คือระบบจัดการคลังสินค้าที่พัฒนาด้วยภาษา Python เพื่อช่วยจัดการข้อมูลสินค้าคงคลัง โดยรองรับฟังก์ชันหลัก ได้แก่ การเพิ่มสินค้าใหม่ การเติมสต็อกสินค้า (Restock) การตัดสต็อกเมื่อขายสินค้า (Sell) พร้อมการตรวจสอบความถูกต้องของข้อมูล (Validation) และการคำนวณมูลค่ารวมของสินค้าทั้งหมดในคลัง มีการออกแบบตามหลัก Clean Architecture, SOLID Principles, และมีระบบประเมินผล AI Component ที่ได้มาตรฐาน

---

## 2. แผนผังและหน้าที่ของไฟล์สำคัญ (Key Files & Directories)

| ไฟล์ / โฟลเดอร์ | หน้าที่และความสำคัญ | สถานะ |
|---|---|---|
| `README.md` | ข้อมูลภาพรวมเบื้องต้นของ Repository และคำแนะนำการเริ่มต้นใช้งาน | มีอยู่แล้ว |
| `requirements.md` | เอกสารรวบรวมฟังก์ชันและความต้องการของระบบ (SRS) ทั้ง Functional และ Non-functional | มีอยู่แล้ว |
| `tech-stack.md` | รายการเทคโนโลยี ไลบรารี สถาปัตยกรรม และเครื่องมือที่เลือกใช้ในโครงการ | มีอยู่แล้ว |
| `team-charter.md` | ข้อตกลงการทำงานของทีม สมาชิก บทบาท GitHub Flow และ AI Usage Policy (ไฟล์ `TEAM_CHARTER.md`) | มีอยู่แล้ว (`TEAM_CHARTER.md`) |
| `AI_USE_LOG.md` | บันทึกประวัติและนโยบายการใช้งาน AI ในการพัฒนาโค้ดและการสร้างเอกสาร | มีอยู่แล้ว |
| `architecture.md` | เอกสารสถาปัตยกรรมระบบ โครงสร้างซอฟต์แวร์ Class/Sequence Diagrams และ SOLID Analysis | มีอยู่แล้ว |
| `adr/` | Architectural Decision Records (ADR) บันทึกการตัดสินใจหลัก 4 ฉบับ (Framework, LLM, Pattern, Deploy) | มีอยู่แล้ว |
| `tests/` | โฟลเดอร์สำหรับ Automated Unit Tests เช่น `tests/test_inventory.py` สำหรับทดสอบตรรกะระบบ | มีอยู่แล้ว |
| `evals/` | ชุดประเมิน AI Component พร้อม Golden Dataset 25 กรณีทดสอบ, สคริปต์รัน และผลลัพธ์ Regression | มีอยู่แล้ว |
| `docs/ethics-review.md` | เอกสารการประเมินจริยธรรม ตอบ 5 คำถาม (§14.4.13), สิ่งที่ตัดสินใจไม่ทำ และ 10-item checklist | มีอยู่แล้ว |
| `docs/runbook.md` | คู่มือการติดตั้ง การรันระบบ การทดสอบ การรัน Lint และแนวทางแก้ไขปัญหา (Troubleshooting) | มีอยู่แล้ว |
| `inventory.py` | โค้ดหลัก (Core Module) สำหรับจัดการสินค้าและคลังสินค้า (`Inventory`, `InventoryItem`) | มีอยู่แล้ว |
| `Story+AC/` | โฟลเดอร์จัดเก็บ User Stories และ Acceptance Criteria (US-01 ถึง US-05) | มีอยู่แล้ว |

---

## 3. สถานะปัจจุบันของโปรเจกต์ (Current Status)
- **ขั้นตอนการพัฒนา:** ดำเนินการตามแนวทาง Agile / GitHub Flow มีเอกสารและการออกแบบระบบครบถ้วนทุกมิติ
- **ส่วนที่ทำเสร็จแล้ว:** โมดูลจัดการสินค้าพื้นฐาน (`inventory.py` และ `inventory-sdd/`), ชุดทดสอบอัตโนมัติ (`tests/`), ชุดประเมินผล AI (`evals/`), บันทึกการตัดสินใจสถาปัตยกรรม (`adr/`), การประเมินจริยธรรม (`docs/ethics-review.md`), และคู่มือการรัน (`docs/runbook.md`)
- **แผนงานถัดไป:** เชื่อมต่อ REST API และพัฒนาหน้าจอผู้ใช้เพิ่มเติม พร้อมรักษามาตรฐานการทดสอบและ CI ในทุก Pull Request
