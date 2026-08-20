from typing import Protocol, List


class Notifier(Protocol):
    """Protocol สำหรับระบบการแจ้งเตือนตามหลัก DIP/OCP"""
    def send(self, message: str) -> None:
        """ส่งข้อความแจ้งเตือนไปยังปลายทาง"""
        ...


class EmailNotifier:
    """ระบบแจ้งเตือนผ่าน Email"""
    def __init__(self, recipient_email: str) -> None:
        """กำหนดตัวแปรเริ่มต้นสำหรับ EmailNotifier"""
        self.recipient_email = recipient_email

    def send(self, message: str) -> None:
        """จำลองการส่งข้อความผ่าน Email"""
        print(f"[Email] To: {self.recipient_email} | Message: {message}")


class SMSNotifier:
    """ระบบแจ้งเตือนผ่าน SMS"""
    def __init__(self, phone_number: str) -> None:
        """กำหนดตัวแปรเริ่มต้นสำหรับ SMSNotifier"""
        self.phone_number = phone_number

    def send(self, message: str) -> None:
        """จำลองการส่งข้อความผ่าน SMS"""
        print(f"[SMS] To: {self.phone_number} | Message: {message}")


class NotifierFactory:
    """Factory สำหรับสร้าง Instance ของ Notifier ต่างๆ"""
    
    @staticmethod
    def create_notifier(notifier_type: str, destination: str) -> Notifier:
        """สร้าง Notifier ตามประเภทและปลายทางที่ระบุ"""
        notifier_type_lower = notifier_type.lower()
        if notifier_type_lower == "email":
            return EmailNotifier(recipient_email=destination)
        elif notifier_type_lower == "sms":
            return SMSNotifier(phone_number=destination)
        else:
            raise ValueError(f"ไม่รองรับประเภทการแจ้งเตือน: {notifier_type}")