# Architecture Documentation

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Application                       │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌──────────────────┐                      ┌──────────────────┐
│  Order Service   │                      │ Product Service  │
│  (Port 5002)     │                      │  (Port 5001)     │
│                  │                      │                  │
│  - Create Orders │                      │  - Product CRUD  │
│  - View Orders   │────── REST ─────────▶│  - Stock Mgmt    │
│  - Order History │   GET /products/{id} │  - Inventory     │
│                  │   PUT /stock         │                  │
└──────────────────┘                      └──────────────────┘
        │                                           │
        │                                           │
        ▼                                           ▼
┌──────────────────┐                      ┌──────────────────┐
│  Order Data      │                      │  Product Data    │
│  (In-Memory)     │                      │  (In-Memory)     │
└──────────────────┘                      └──────────────────┘
```

## Communication Flow

### Order Creation Sequence

1. **Client** → `POST /orders` → **Order Service**
2. **Order Service** → `GET /products/{id}` → **Product Service** (validate product exists)
3. **Order Service** → `PUT /products/{id}/stock` → **Product Service** (reserve inventory)
4. **Product Service** → Response (success/failure) → **Order Service**
5. **Order Service** → Order created → **Client**

## Service Boundaries

### Product Service Domain
- **Owns**: Product catalog, pricing, inventory levels
- **Responsibilities**: 
  - Product information management
  - Stock level tracking and updates
  - Inventory availability validation
- **Data**: Product ID, name, price, stock quantity

### Order Service Domain
- **Owns**: Order lifecycle, order state
- **Responsibilities**:
  - Order creation and management
  - Order validation (via product-service)
  - Order history
- **Data**: Order ID, items, total, status
- **Dependencies**: Requires product-service for product validation

## Granularity Analysis

### Granularity Disintegrators (Reasons to Separate)

1. **Code Volatility**: Product catalog changes independently from order processing logic. Product prices and inventory are updated frequently, while order processing rules are more stable.

2. **Differing Scalability Needs**: Product catalog queries (browsing, searching) require high read throughput, while order creation has different performance characteristics (write-heavy, transactional).

3. **Fault Tolerance**: If product catalog is temporarily unavailable, we may want to allow order viewing (read-only operations) to continue. Separating services allows independent failure domains.

4. **Extensibility**: Future features like product recommendations, reviews, or categories can be added to product-service without affecting order-service. Similarly, order-service can add features like payment processing, shipping, or order tracking independently.

5. **Team Ownership**: Different teams can own and deploy product catalog vs. order management independently, enabling parallel development.

### Granularity Integrators (Reasons to Keep Together)

1. **Database Transactions**: Order creation requires atomic updates to both order and inventory. However, we've chosen eventual consistency via synchronous REST calls rather than distributed transactions (which would require tighter coupling).

2. **Shared Code**: Minimal shared code between services—only communication contracts (REST API). This is acceptable as it's just an interface definition.

3. **Tight Data Relationships**: Orders reference products, but we've chosen to maintain this as a loose reference (product_id) rather than embedding product data, allowing services to evolve independently.

**Decision**: The disintegrators outweigh the integrators, justifying separate services. The trade-off is accepting eventual consistency and handling failures gracefully rather than maintaining a monolithic system.

