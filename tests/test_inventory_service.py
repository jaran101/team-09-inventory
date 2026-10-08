from decimal import Decimal

import pytest
from src.models import Category, Product, StockTransaction, TransactionType
from src.notifiers import EmailNotifier, NotifierFactory, SMSNotifier
from src.service import InventoryService


class RecordingNotifier:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)


class FailingNotifier:
    def send(self, message):
        raise RuntimeError("delivery failed")


def make_service(quantity=10, threshold=5, notifiers=None, category=None):
    service = InventoryService(notifiers)
    category = category or Category("CAT01", "General")
    service.add_category(category)
    product = Product("P01", "Widget", category, "2.50", quantity, threshold)
    service.add_product(product)
    return service, product


def test_categories_products_and_product_list_copy():
    service, product = make_service()

    products = service.list_products()
    products.clear()

    assert service.list_products() == [product]
    with pytest.raises(ValueError):
        service.add_product(product)
    with pytest.raises(ValueError):
        service.add_product(Product("P02", "Other", Category("CAT02", "Missing"), 1))


@pytest.mark.parametrize(
    ("category_id", "name"),
    [("", "General"), ("CAT01", "")],
)
def test_category_requires_id_and_name(category_id, name):
    with pytest.raises(ValueError):
        Category(category_id, name)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"price_per_unit": True}, "ราคาสินค้าต้องเป็นตัวเลข"),
        ({"price_per_unit": "invalid"}, "ราคาสินค้าต้องเป็นตัวเลข"),
        ({"price_per_unit": -1}, "ราคาสินค้าต้องไม่ติดลบ"),
        ({"quantity": True}, "จำนวนสินค้าต้องเป็นจำนวนเต็ม"),
        ({"quantity": -1}, "จำนวนสินค้าต้องไม่ติดลบ"),
        ({"threshold": False}, "กรุณากรอกค่าเป็นตัวเลข"),
        ({"threshold": 0}, "กรุณากรอกตัวเลขที่มากกว่า 0"),
        ({"id": ""}, "รหัสสินค้าต้องไม่เป็นค่าว่าง"),
        ({"name": ""}, "ชื่อสินค้าต้องไม่เป็นค่าว่าง"),
    ],
)
def test_product_validation(kwargs, message):
    values = {
        "id": "P01",
        "name": "Widget",
        "category": Category("CAT01", "General"),
        "price_per_unit": "2.50",
        "quantity": 1,
        "threshold": 1,
    }
    values.update(kwargs)

    with pytest.raises(ValueError, match=message):
        Product(**values)


def test_stock_transaction_requires_positive_quantity():
    with pytest.raises(ValueError, match="มากกว่า 0"):
        StockTransaction("T01", "P01", TransactionType.IN, 0)


def test_receive_stock_alerts_and_records_transactions():
    notifier = RecordingNotifier()
    service, product = make_service(quantity=2, notifiers=[notifier])

    service.receive_stock("P01", 1)
    service.receive_stock("P01", 2)
    service.receive_stock("P01", 1)

    assert product.quantity == 6
    assert "สต็อกในระบบคงเหลือ 3" in notifier.messages[0]
    assert "ถูกเติมแล้ว" in notifier.messages[1]
    assert len(notifier.messages) == 2
    assert [transaction.transaction_type for transaction in service.transactions] == [
        TransactionType.IN,
        TransactionType.IN,
        TransactionType.IN,
    ]


@pytest.mark.parametrize("quantity", [0, -1, True, 1.5, "2"])
def test_stock_changes_reject_invalid_quantities(quantity):
    service, _ = make_service()

    with pytest.raises(ValueError):
        service.receive_stock("P01", quantity)

    with pytest.raises(ValueError):
        service.issue_stock("P01", quantity)


def test_issue_stock_empty_insufficient_and_successful_paths():
    notifier = RecordingNotifier()
    empty_service, _ = make_service(quantity=0, notifiers=[notifier])
    with pytest.raises(ValueError, match="ไม่มีสินค้า"):
        empty_service.issue_stock("P01", 1)

    service, product = make_service(quantity=2, threshold=2, notifiers=[notifier])
    with pytest.raises(ValueError, match="ไม่พอ"):
        service.issue_stock("P01", 3)
    service.issue_stock("P01", 1)

    assert product.quantity == 1
    assert service.transactions[0].transaction_type is TransactionType.OUT
    assert "ต่ำกว่า threshold" in notifier.messages[-1]


def test_missing_products_raise_key_error():
    service = InventoryService()

    with pytest.raises(KeyError, match="ไม่พบสินค้า"):
        service.receive_stock("missing", 1)
    with pytest.raises(KeyError, match="ไม่พบสินค้า"):
        service.update_threshold("missing", 1)


@pytest.mark.parametrize("new_threshold", [" 4 ", 4.0, 4])
def test_update_threshold_accepts_integer_values_and_alerts_when_low(new_threshold):
    notifier = RecordingNotifier()
    service, product = make_service(quantity=2, notifiers=[notifier])

    service.update_threshold("P01", new_threshold)

    assert product.threshold == 4
    assert "สินค้าในสต็อกต่ำ" in notifier.messages[-1]


@pytest.mark.parametrize("new_threshold", [True, "1.5", "invalid", 1.5, 0, -1])
def test_update_threshold_rejects_invalid_values(new_threshold):
    service, _ = make_service()

    with pytest.raises(ValueError):
        service.update_threshold("P01", new_threshold)


def test_update_threshold_without_low_stock_alert():
    notifier = RecordingNotifier()
    service, _ = make_service(quantity=10, notifiers=[notifier])

    service.update_threshold("P01", 5)

    assert "ต่ำ" not in notifier.messages[0]


def test_category_values_are_summed_using_decimal():
    service, _ = make_service(quantity=3)
    service.add_product(Product("P02", "Gadget", service.categories["CAT01"], 1, 2, 1))

    assert service.get_stock_value_by_category() == {"General": Decimal("9.50")}


def test_failed_notifier_is_logged_and_does_not_block_other_notifiers(caplog):
    notifier = RecordingNotifier()
    service, _ = make_service(notifiers=[FailingNotifier(), notifier])

    service._notify_all(["notice"])

    assert notifier.messages == ["notice"]
    assert "ส่งการแจ้งเตือนล้มเหลว" in caplog.text


def test_notifier_factory_creates_email_and_sms_notifiers(capsys):
    email = NotifierFactory.create_notifier("EMAIL", "team@example.test")
    sms = NotifierFactory.create_notifier("sms", "555-0100")

    assert isinstance(email, EmailNotifier)
    assert isinstance(sms, SMSNotifier)
    email.send("hello")
    sms.send("hello")
    assert "[Email] To: team@example.test" in capsys.readouterr().out

    with pytest.raises(ValueError, match="ไม่รองรับ"):
        NotifierFactory.create_notifier("push", "device")
