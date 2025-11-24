# ADR-002: Synchronous REST for Inter-Service Communication

## Status
Accepted

## Context
Order-service needs to communicate with product-service to validate products and reserve inventory during order creation. We must choose between synchronous (REST/gRPC) or asynchronous (message broker) communication patterns.

## Decision
Use synchronous REST API calls for inter-service communication between order-service and product-service.

## Consequences

### Positive Impacts
- **Immediate Consistency**: Order creation only succeeds if products are available and stock is reserved, preventing overselling
- **Simple Implementation**: REST is straightforward to implement, debug, and test. No additional infrastructure (message brokers) required
- **Request-Response Pattern**: Natural fit for order creation flow where we need immediate feedback
- **Standard Protocol**: HTTP/REST is widely understood, well-documented, and has excellent tooling support
- **Easy Debugging**: Synchronous calls create clear request-response traces that are easy to follow
- **Type Safety**: FastAPI provides automatic validation and type checking for REST endpoints

### Negative Impacts
- **Tight Coupling**: Order-service blocks waiting for product-service response, creating temporal coupling
- **Cascading Failures**: If product-service is slow or unavailable, order creation fails entirely
- **Latency**: Each order creation requires multiple sequential network calls (GET product, PUT stock), adding latency
- **Blocking**: Synchronous calls block order-service threads, potentially limiting throughput under high load
- **No Retry Logic**: Current implementation doesn't handle transient failures gracefully (could be improved with retries/circuit breakers)
- **Scalability**: Synchronous calls don't handle burst traffic as well as asynchronous patterns

### Trade-offs Considered
- **Consistency vs Performance**: Chose strong consistency (synchronous) over higher throughput (asynchronous) to prevent inventory inconsistencies
- **Simplicity vs Resilience**: Chose simpler implementation over more resilient async pattern, accepting risk of cascading failures
- **Latency vs Correctness**: Accepted added latency to ensure correct inventory management

## Alternatives Considered
1. **Asynchronous Messaging (RabbitMQ/Kafka)**: 
   - Pros: Decoupling, better resilience, higher throughput
   - Cons: Eventual consistency, more complex, requires message broker infrastructure
   - Rejected: Need immediate feedback for order creation, and eventual consistency could lead to overselling

2. **gRPC**:
   - Pros: Better performance, type safety, streaming support
   - Cons: More complex setup, less tooling support, requires protocol buffers
   - Rejected: REST provides sufficient performance for this use case and better ecosystem support

3. **GraphQL**:
   - Pros: Flexible queries, reduced over-fetching
   - Cons: More complex, overkill for simple CRUD operations
   - Rejected: REST endpoints are sufficient and simpler to implement

## Future Considerations
- Could add retry logic with exponential backoff for transient failures
- Could implement circuit breaker pattern to prevent cascading failures
- Could add caching layer for frequently accessed products
- Could migrate to async messaging for non-critical operations (e.g., order notifications)

