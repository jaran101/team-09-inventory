
| ประเด็น                              | ก่อนมี context (ขั้นที่ 4) | หลังมี context (ขั้นที่ 6)|
| -----------------------------------| ---------- || -------------------------- |
|1.แยกไฟล์/ความรับผิดชอบ                 | ไม่มีการจะการแยกไฟล์กัน   |แยกไฟล์ชัดเจนตามกฎกำหนด: |
| -----------------------------------| ---------- || -------------------------- |
|2. type hint + docstring              | มี Type hint ครบถ้วนตามมาตรฐาน  • มี Docstring ภาษาไทยเฉพาะบาง method (ยังขาดที่ constructor/add_product)  |• มี Type hint ครบถ้วนทุก function signature • มี Docstring ภาษาไทยใน ทุก public method ตามกฎข้อ 1 |
| -----------------------------------| ---------- || -------------------------- |
|3. service ผูกกับ notifier ตรง ๆ หรือไม่ | ไม่ผูกตรง (ปฏิบัติตามหลัก DIP/SOLID) ใช้อินเทอร์เฟซ NotificationService และรับผ่านการลงทะเบียน  | ไม่ผูกตรง (ปฏิบัติตามหลัก DIP/SOLID) ใช้อินเทอร์เฟซ Notifier และรับผ่าน Constructor (Dependency Injection)|
|4. hardcode config หรือไม่             | ไม่มีการ Hardcode ค่า Config ใน Business Logic  | ไม่มีการ Hardcode ค่า Config ใน Business Logic |