import logging
from typing import Callable, Dict, Protocol

logger = logging.getLogger(__name__)


class Notifier(Protocol):
    """อินเทอร์เฟซของ Observer สำหรับรับการแจ้งเตือนจาก InventoryService

    สัญญา: send() ต้องไม่ทำให้ผู้เรียกล้ม ถ้าส่งไม่สำเร็จให้จัดการ/log ภายใน
    (InventoryService ป้องกันซ้ำอีกชั้นหนึ่ง)
    """

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


NotifierBuilder = Callable[[str], Notifier]


class NotifierFactory:
    """Factory แบบ registry: เพิ่มช่องทางใหม่ด้วย register() โดยไม่ต้องแก้คลาสนี้ (OCP)"""

    _registry: Dict[str, NotifierBuilder] = {}

    @classmethod
    def register(cls, channel: str, builder: NotifierBuilder) -> None:
        """ลงทะเบียนช่องทางแจ้งเตือนใหม่"""
        cls._registry[channel.lower()] = builder

    @classmethod
    def create(cls, channel: str, destination: str) -> Notifier:
        """สร้าง Notifier ตามช่องทางและปลายทางที่ระบุ"""
        builder = cls._registry.get(channel.lower())
        if builder is None:
            raise ValueError(f"ไม่รองรับประเภทการแจ้งเตือน: {channel}")
        return builder(destination)

    @classmethod
    def create_notifier(cls, notifier_type: str, destination: str) -> Notifier:
        """ชื่อเดิม เก็บไว้เพื่อให้โค้ดเก่าเรียกได้ (ชี้ไป create)"""
        return cls.create(notifier_type, destination)


NotifierFactory.register("email", EmailNotifier)
NotifierFactory.register("sms", SMSNotifier)
