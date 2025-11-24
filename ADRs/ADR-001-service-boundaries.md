# ADR-001: Service Boundary Separation (Product vs Order)

## Status
Accepted

## Context
We need to design a microservices architecture for a Products & Orders domain. The key question is: should product catalog management and order processing be separate services or combined into a single service?

## Decision
Separate the system into two distinct microservices:
- **product-service**: Manages product catalog and inventory
- **order-service**: Manages order creation and lifecycle

## Consequences

### Positive Impacts
- **Independent Scalability**: Product catalog can scale horizontally for high read loads (browsing, searching) while order service scales independently for write-heavy operations
- **Fault Isolation**: Failure in product catalog doesn't immediately crash order processing (though it may prevent new orders)
- **Independent Deployment**: Teams can deploy product updates (price changes, new products) without affecting order processing
- **Technology Flexibility**: Each service can evolve its technology stack independently if needed
- **Clear Ownership**: Clear domain boundaries make it easier to assign team ownership

### Negative Impacts
- **Distributed Transactions**: Cannot use ACID transactions across services. Must handle consistency via synchronous calls or eventual consistency patterns
- **Network Latency**: Order creation requires multiple network calls to product-service, adding latency
- **Coupling**: Order-service depends on product-service availability and API contract
- **Complexity**: More moving parts to deploy, monitor, and debug
- **Data Consistency**: Risk of stale product data in orders if product information changes after order creation

### Trade-offs Considered
- **Consistency vs Availability**: Chose immediate consistency (synchronous REST) over eventual consistency to prevent overselling, accepting that order creation may fail if product-service is unavailable
- **Coupling vs Independence**: Accepted coupling through REST API contract to gain service independence in deployment and scaling
- **Simplicity vs Scalability**: Chose increased complexity for better scalability and maintainability

## Alternatives Considered
1. **Monolithic Service**: Rejected due to inability to scale components independently
2. **Three Services** (Product, Inventory, Order): Rejected as premature optimization—inventory is tightly coupled to products
3. **Event-Driven Architecture**: Considered but rejected for initial implementation due to added complexity; could be future enhancement

