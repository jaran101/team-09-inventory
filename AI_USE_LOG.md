# บันทึกการใช้งาน AI ในการพัฒนา (AI Use Log)
## โครงการ: Inventory System

เอกสารนี้ใช้บันทึกประวัติการใช้ Generative AI ในการช่วยออกแบบ เขียนโค้ด รีแฟกเตอร์ และสร้างชุดทดสอบของทีม ตามนโยบายที่กำหนดไว้ใน [TEAM_CHARTER.md](file:///c:/Users/dass0/OneDrive/%E0%B9%80%E0%B8%94%E0%B8%AA%E0%B8%81%E0%B9%8C%E0%B8%97%E0%B9%87%E0%B8%AD%E0%B8%9B/workshop/team-09-inventory/TEAM_CHARTER.md)

---

## 1. นโยบายและแนวปฏิบัติของทีม (AI Usage Policy)
1. **Human in the Loop:** โค้ดทุกบรรทัดที่ AI สร้างขึ้น สมาชิกในทีมต้องอ่าน ตรวจสอบความถูกต้อง และทำความเข้าใจก่อน Commit
2. **Commit Message Review:** Commit message ที่ AI ร่าง ต้องตรวจและแก้ไขให้ตรงกับ git diff จริงเสมอ
3. **No Blind Copy-Paste:** ห้ามวางโค้ดโดยไม่มีชุดทดสอบ (Unit Test) รองรับ
4. **Data Privacy & Secrets:** ห้ามใส่ Secret Key, API Token หรือข้อมูลส่วนบุคคลใด ๆ ลงใน AI Prompt
5. **No Subscription Required:** ใช้เฉพาะเครื่องมือ AI ที่เข้าถึงได้โดยไม่มีค่าใช้จ่าย ไม่บังคับซื้อ Subscription

---

## 2. ตารางบันทึกประวัติการใช้งาน AI (AI Interaction Log)

| ลำดับ | วันที่ | ผู้บันทึก | กิจกรรม / งานที่ทำ | เครื่องมือ AI ที่ใช้ | สรุป Prompt / คำสั่ง | ผลลัพธ์ที่ได้จาก AI | สิ่งที่ทีมตรวจพบและแก้ไขเอง (Human Edits) |
|---|---|---|---|---|---|---|---|
| 01 | 2026-09-15 | จรัลชัย | ร่างโค้ดระบบจัดการสินค้าเริ่มต้น (`inventory.py`) | Claude 3.5 Sonnet / Copilot | "สร้างคลาส InventoryItem และ Inventory พร้อมฟังก์ชัน add_item, restock, sell" | โครงคลาสพื้นฐานพร้อมฟังก์ชันคำนวณ | เพิ่ม Validation ตรวจสอบชื่อว่างเปล่า จำนวนติดลบ และราคา <= 0 ด้วยตนเอง |
| 02 | 2026-09-22 | ภูมิพัฒน์ | ออกแบบและสร้าง Unit Tests สำหรับ US-01 และ US-02 | ChatGPT (GPT-4o mini) | "เขียน unit tests สำหรับ Inventory system โดยใช้ pytest ครอบคลุมกรณีปกติและ error" | ชุด test สำหรับ add_item, restock, sell | ปรับแก้ Test assertions ให้สอดคล้องกับข้อความ error ภาษาไทย และเพิ่ม boundary cases |
| 03 | 2026-09-29 | ธนกฤต | ตรวจสอบ Code Smells ใน `pricing_legacy.py` | Google Gemini 1.5 Flash | "วิเคราะห์จุดที่อ่านยากและ code smells ในโค้ดคำนวณราคานี้" | ระบุ 5 จุด (magic numbers, long function, side effects) | เพิ่มรายละเอียดจุดอ่านยากเป็น 10 ข้อ ชี้บรรทัดในโค้ด และเขียน characterization tests คลุมก่อน refactor |
| 04 | 2026-10-05 | จรัลชัย | ออกแบบสถาปัตยกรรม SDD และ Notifier Interface | Google Gemini / Claude | "ออกแบบระบบแจ้งเตือนสต็อกต่ำตามหลัก SOLID และ Dependency Injection" | แนะนำแยก Notifier Interface และสร้าง NotifierFactory | เพิ่ม SMSNotifier, ออกแบบ Data models ด้วย dataclass และแยก Service Layer ชัดเจน |
| 05 | 2026-10-10 | ทั้งทีม | จัดทำเอกสารโปรเจกต์ Capstone (`PROJECT.md`, `requirements.md`, `tech-stack.md`) | Antigravity AI Assistant | "ร่างเอกสารโครงการ โครงสร้างไฟล์ และสถาปัตยกรรมระบบ" | ร่างเอกสารและโครงสร้างตารางไฟล์สำคัญ | ปรับแต่งเนื้อหาให้ตรงกับสภาพแวดล้อมจริงของ repo และตอบโจทย์เกณฑ์หลักสูตร |

---

## 3. สรุปบทเรียนจากการใช้ AI (Lessons Learned)
- **จุดแข็ง:** AI ช่วยร่างแบบสถาปัตยกรรม สร้าง Boilerplate Code และคิด Edge Case สำหรับชุดทดสอบได้รวดเร็วมาก
- **จุดที่ต้องระวัง (Pitfalls):** 
  - AI มักจะเขียน Test ที่ "ผ่านง่ายเกินไป" (Tautological / Weak Assertions) ทีมจึงต้องเสริม Test cases ที่เข้มงวดด้วยตนเอง
  - AI มักจะสมมติโครงสร้างไฟล์หรือไลบรารีที่ไม่ได้ติดตั้งจริง จึงต้องตรวจสอบเทียบกับ Environment จริงเสมอ
