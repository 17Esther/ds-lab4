# Microservices Lab: Products & Orders

## Requirements

- **Python Version**: Python 3.9.6 (specified in Dockerfiles)
- **Framework**: FastAPI 0.104.1
- **Containerization**: Docker
- **Orchestration**: Kubernetes

## Service Boundaries

### Product Service
The **product-service** is responsible for managing product catalog information and inventory. It maintains product details (name, price, stock levels) and provides stock management operations. This service owns all product-related data and enforces business rules around inventory availability.

### Order Service
The **order-service** handles order creation and management. It orchestrates the order fulfillment process by communicating with the product-service to validate product availability and reserve inventory. The order-service maintains order state but does not store product details—it fetches them from the product-service when needed.

**Boundary Principle**: Each service owns its domain data. Product-service owns product catalog and inventory; order-service owns order lifecycle and fulfillment logic.

---

## REST Endpoints

### Product Service (`http://product-service`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint |
| `GET` | `/products` | Get all products |
| `GET` | `/products/{id}` | Get product by ID |
| `GET` | `/products/{id}/stock` | Get stock level for a product |
| `PUT` | `/products/{id}/stock` | Update stock level (used by order-service) |

### Order Service (`http://order-service`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint |
| `GET` | `/orders` | Get all orders |
| `GET` | `/orders/{id}` | Get order by ID |
| `POST` | `/orders` | Create a new order (requires items with product_id and quantity) |

---

## Inter-Service Communication

The order-service communicates with the product-service using synchronous REST calls during order creation. When a new order is submitted, the order-service validates each product by calling `GET /products/{id}` to retrieve product details and check availability. If products are available, it reserves inventory by calling `PUT /products/{id}/stock` to decrement stock levels. This synchronous approach ensures immediate consistency—the order is only created if all products are available and stock is successfully reserved.

**Pros of Synchronous REST**: Immediate feedback ensures data consistency and prevents overselling. The request-response pattern is simple to implement and debug, making it ideal for operations that require immediate validation. REST is a standard protocol with excellent tooling support and easy integration. **Cons**: Synchronous calls create tight coupling between services—if the product-service is slow or unavailable, order creation fails entirely. This can lead to cascading failures and reduced system resilience. Additionally, synchronous calls block the order-service thread, potentially limiting throughput under high load. Each order creation requires multiple sequential network calls, adding latency compared to asynchronous patterns.

**Trade-off Analysis**: We chose synchronous REST over asynchronous messaging (e.g., RabbitMQ/Kafka) because order creation requires immediate validation and consistency. Asynchronous patterns would provide better resilience and throughput but introduce eventual consistency risks that could lead to overselling. The simplicity and immediate consistency of synchronous REST outweigh the performance benefits of async messaging for this critical business operation.

---

## Quick Start

For detailed setup instructions, see [SETUP.md](SETUP.md).

## Deployment

### Building Docker Images

```bash
# Build product-service image
cd product-service
docker build -t product-service:latest .

# Build order-service image
cd ../order-service
docker build -t order-service:latest .
```

### Deploying to Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/product-service-deployment.yaml
kubectl apply -f k8s/order-service-deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get services
```

### Testing

```bash
# Port forward to access services locally
kubectl port-forward service/product-service 5001:80
kubectl port-forward service/order-service 5002:80

# Test product-service
curl http://localhost:5001/products

# Test order-service
curl -X POST http://localhost:5002/orders \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": 1, "quantity": 2}]}'
```

### API Documentation

FastAPI automatically generates interactive API documentation:
- Product Service: `http://localhost:5001/docs` (Swagger UI) or `http://localhost:5001/redoc` (ReDoc)
- Order Service: `http://localhost:5002/docs` (Swagger UI) or `http://localhost:5002/redoc` (ReDoc)

## Architecture Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture diagrams and granularity analysis.

## Architectural Decision Records (ADRs)

See the [ADRs/](ADRs/) directory for documented architectural decisions:
- [ADR-001: Service Boundary Separation](ADRs/ADR-001-service-boundaries.md)
- [ADR-002: Synchronous REST Communication](ADRs/ADR-002-synchronous-rest.md)
- [ADR-003: FastAPI Framework Selection](ADRs/ADR-003-fastapi-framework.md)

