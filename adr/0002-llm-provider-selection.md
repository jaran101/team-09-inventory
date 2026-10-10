# ADR-0002: การเลือก LLM Provider และ Free Alternative สำหรับโมดูล AI

## สถานะ (Status)
**Accepted** (2026-10-02)

---

## บริบท (Context)
โปรเจกต์ต้องการโมดูล AI สำหรับช่วยวิเคราะห์สถานะคลังสินค้า สรุปแนวโน้มการใช้วัตถุดิบ และร่างข้อความแจ้งเตือนผู้จัดการ อย่างไรก็ตาม ตามข้อตกลงทีมใน `TEAM_CHARTER.md` กำหนดไว้ชัดเจนว่า **ต้องไม่มีค่าใช้จ่าย และไม่บังคับซื้อ Subscription** ดังนั้นการเลือก LLM Provider จึงต้องมีตัวเลือกที่ใช้งานได้ฟรี เสถียร และมีทางเลือกสำรอง (Fallback) ที่ทำงานแบบ Local ได้

---

## ปัจจัยในการตัดสินใจ (Decision Drivers)
- นโยบายค่าใช้จ่ายเป็นศูนย์ (Zero Cost / Free Tier)
- อัตราการตอบสนอง (Latency) และ Rate Limits เพียงพอสำหรับการทดสอบและรัน Eval
- รองรับ Structured Output (JSON Schema) สำหรับสร้างการแจ้งเตือน
- ความสามารถในการทำงานแบบ Local หรือ Offline หากระบบเครือข่ายมีปัญหา

---

## ทางเลือกที่พิจารณา (Considered Options)
1. **Google Gemini API (Gemini 1.5 Flash) ร่วมกับ Groq (Llama 3.1 8B):** ทั้งสองเจ้ามี Free Tier ใช้งานได้ฟรี ตอบสนองรวดเร็วมาก
2. **OpenAI API (GPT-4o):** มีความสามารถสูง แต่ต้องเสียค่าใช้จ่ายแบบ Pay-as-you-go ขัดกับนโยบายของทีม
3. **Local LLM ผ่าน Ollama (เช่น Llama-3-8B-Instruct):** รันบนเครื่องตนเอง ไม่มีค่าใช้จ่ายและปลอดภัยต่อข้อมูล แต่ต้องใช้เครื่องที่มี GPU/RAM เพียงพอ

---

## การตัดสินใจ (Decision)
ทีมตัดสินใจเลือก **แนวทาง Multi-Provider ที่มี Fallback**:
- **Primary Cloud Provider:** ใช้ **Google Gemini API (Gemini 1.5 Flash)** เป็นตัวหลัก เนื่องจากมี Free Tier 15 RPM, รองรับภาษาไทยได้ดีเยี่ยม และรองรับ System Instructions
- **Secondary Cloud Fallback:** ใช้ **Groq API** (Llama 3.1 8B) สำหรับกรณีที่ Rate Limit ของ Gemini เต็ม
- **Local Free Alternative:** รองรับ **Ollama** เป็น Fallback บนเครื่อง Developer เพื่อให้สามารถรัน CI/CD หรือทำการทดสอบแบบ Offline ได้โดยไม่ต้องพึ่งพิง API Key

---

## ผลที่ตามมา (Consequences)
- **เชิงบวก:** ไม่มีค่าใช้จ่าย, สมาชิกทุกคนในทีมเข้าถึงได้, มีระบบสำรองกรณี API ล่ม
- **เชิงลบ / สิ่งที่ต้องจัดการ:** ต้องออกแบบ Provider Interface ให้สอดคล้องกันเพื่อสลับใช้งานระหว่าง Gemini / Groq / Ollama ได้อย่างไร้รอยต่อ และต้องประเมินผลผ่านชุด `evals/` เพื่อให้แน่ใจว่าคุณภาพ Prompt ไม่ตกหล่น
