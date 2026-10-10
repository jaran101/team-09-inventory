# Architecture Decision Records (ADR)
## โครงการ: Inventory System

โฟลเดอร์นี้รวบรวมบันทึกการตัดสินใจเชิงสถาปัตยกรรม (Architectural Decision Records - ADR) ที่สำคัญของระบบ Inventory System เพื่อบันทึกบริบท เหตุผล ทางเลือกที่พิจารณา และผลกระทบของการตัดสินใจ

---

## ดัชนีรายการ ADR (ADR Index)

| รหัส | หัวข้อการตัดสินใจ | สถานะ | วันที่บันทึก |
|---|---|---|---|
| [ADR-0001](0001-backend-framework-selection.md) | การเลือก Backend Framework และ Core Execution Model | Accepted | 2026-10-01 |
| [ADR-0002](0002-llm-provider-selection.md) | การเลือก LLM Provider และ Free Alternative สำหรับ AI Assistance | Accepted | 2026-10-02 |
| [ADR-0003](0003-architecture-pattern-selection.md) | การเลือก Architecture Pattern: Layered Domain-Centric with Dependency Injection | Accepted | 2026-10-03 |
| [ADR-0004](0004-deployment-platform-selection.md) | การเลือกแพลตฟอร์มการดีพลอย (Deployment Platform) และ CI/CD Strategy | Accepted | 2026-10-04 |

---

## รูปแบบโครงสร้างของ ADR (Format Template)
แต่ละไฟล์ ADR จะประกอบด้วยหัวข้อหลักดังนี้:
1. **Title & Status:** ชื่อเรื่องและสถานะ (Proposed, Accepted, Deprecated, Superseded)
2. **Context:** ปัญหา ความท้าทาย และบริบทที่นำไปสู่การตัดสินใจ
3. **Decision Drivers:** ปัจจัยหลักที่ใช้ตัดสินใจ
4. **Considered Options:** ทางเลือกที่พิจารณาพร้อมข้อดี-ข้อเสีย
5. **Decision:** สิ่งที่ทีมตัดสินใจเลือก
6. **Consequences:** ผลกระทบทั้งเชิงบวกและข้อจำกัดที่ต้องยอมรับ
