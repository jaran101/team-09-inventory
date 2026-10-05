sequenceDiagram
    participant Employee as 👤 Employee
    participant Service as InventoryService
    participant ProductStore as Product Store
    participant TransLog as StockTransaction Log
    participant Notifier1 as EmailNotifier
    participant Notifier2 as SMSNotifier
    
    Employee->>Service: issue_stock(product_id, quantity)
    activate Service
    
    rect rgb(200, 220, 255)
        Note over Service: Validation Phase
        Service->>Service: ✓ Check product_id exists
        Service->>Service: ✓ Check quantity > 0
    end
    
    Service->>ProductStore: Get product by ID
    activate ProductStore
    ProductStore-->>Service: Return product object
    deactivate ProductStore
    
    rect rgb(255, 220, 200)
        Note over Service: Stock Check Phase
        Service->>Service: Check if quantity == 0
        Service-->>Service: No (proceed)
        Service->>Service: Check if quantity < threshold
        Service-->>Service: No (proceed)
    end
    
    rect rgb(200, 255, 220)
        Note over Service: Update Stock
        Service->>ProductStore: product.quantity -= quantity
        activate ProductStore
        Note over ProductStore: New quantity < threshold
        ProductStore-->>Service: Updated ✓
        deactivate ProductStore
    end
    
    Service->>TransLog: Create StockTransaction
    activate TransLog
    TransLog->>TransLog: id = uuid.uuid4()
    TransLog->>TransLog: transaction_type = OUT
    TransLog->>TransLog: timestamp = now()
    TransLog-->>Service: Transaction created ✓
    deactivate TransLog
    
    Service->>Service: Append transaction to log
    
    rect rgb(255, 200, 200)
        Note over Service: Stock Alert Phase
        Service->>Service: Check: product.quantity < threshold?
        Service-->>Service: YES → Trigger alert!
    end
    
    rect rgb(255, 240, 100)
        Note over Service: Notification Phase
        Service->>Service: _notify_all(alert message)
        activate Service
        
        par Parallel Notifications
            Service->>Notifier1: send(message)
            activate Notifier1
            Note over Notifier1: "[Email] To: admin@company.com<br/>Message: สต็อกต่ำกว่า threshold..."
            Notifier1-->>Service: ✓ Sent
            deactivate Notifier1
            
        and
            Service->>Notifier2: send(message)
            activate Notifier2
            Note over Notifier2: "[SMS] To: +66812345678<br/>Message: สต็อกต่ำกว่า threshold..."
            Notifier2-->>Service: ✓ Sent
            deactivate Notifier2
        end
        
        deactivate Service
    end
    
    Service-->>Employee: Return updated product object
    deactivate Service
    
    Employee->>Employee: ✓ Transaction complete
