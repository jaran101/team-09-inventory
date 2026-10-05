classDiagram
    class TransactionType{
        <<enumeration>>
        IN
        OUT
    }
    
    class Category{
        -id: str
        -name: str
        +__post_init__() void
    }
    
    class Product{
        -id: str
        -name: str
        -category: Category
        -price_per_unit: float
        -quantity: int
        -threshold: int
        +__post_init__() void
    }
    
    class StockTransaction{
        -id: str
        -product_id: str
        -transaction_type: TransactionType
        -quantity: int
        -timestamp: datetime
        -note: Optional[str]
        +__post_init__() void
    }
    
    class Notifier{
        <<interface>>
        +send(message: str) void*
    }
    
    class EmailNotifier{
        -recipient_email: str
        +__init__(recipient_email: str) void
        +send(message: str) void
    }
    
    class SMSNotifier{
        -phone_number: str
        +__init__(phone_number: str) void
        +send(message: str) void
    }
    
    class NotifierFactory{
        +create_notifier(notifier_type: str, destination: str) Notifier*
    }
    
    class InventoryService{
        -products: Dict[str, Product]
        -categories: Dict[str, Category]
        -transactions: List[StockTransaction]
        -notifiers: List[Notifier]
        +__init__(notifiers: List[Notifier]) void
        +add_category(category: Category) void
        +add_product(product: Product) void
        -_notify_all(message: str) void
        +receive_stock(product_id: str, quantity: int) Product
        +issue_stock(product_id: str, quantity: int) Product
        +update_threshold(product_id: str, new_threshold: Union) Product
        +get_stock_value_by_category() Dict[str, float]
    }
    
    Product "1" --> "1" Category: uses
    Product "1" --> "1" TransactionType: references
    StockTransaction --> TransactionType: uses
    
    EmailNotifier ..|> Notifier: implements
    SMSNotifier ..|> Notifier: implements
    NotifierFactory --> Notifier: creates
    
    InventoryService --> Product: manages
    InventoryService --> Category: manages
    InventoryService --> StockTransaction: creates
    InventoryService --> Notifier: uses (dependency injection)
