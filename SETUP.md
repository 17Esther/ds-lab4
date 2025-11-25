# Setup and Deployment Guide

## Docker Setup

### 1. Build Docker Images

```bash
# Build product-service image
cd product-service
docker build -t product-service:latest .

# Build order-service image
cd ../order-service
docker build -t order-service:latest .
```

### 2. Verify Images
```bash
docker images | grep -E "product-service|order-service"
```



## Kubernetes Deployment

### 1. Start Kubernetes Cluster

- Enable Kubernetes in Docker Desktop settings
- Wait for cluster to be ready


### 2. Load Docker Images into Kubernetes

**For Docker Desktop:**
- Images are automatically available


### 3. Deploy Services

```bash
# Deploy product-service
kubectl apply -f k8s/product-service-deployment.yaml

# Deploy order-service
kubectl apply -f k8s/order-service-deployment.yaml

# Wait for deployments to be ready
kubectl wait --for=condition=available --timeout=300s deployment/product-service
kubectl wait --for=condition=available --timeout=300s deployment/order-service
```

### 4. Verify Deployment

```bash
# Check deployments
kubectl get deployments

# Check pods
kubectl get pods

# Check services
kubectl get services

# View logs
kubectl logs -l app=product-service --tail=50
kubectl logs -l app=order-service --tail=50
```

### 5. Access Services
```bash
# Terminal 1 - Product Service
kubectl port-forward service/product-service 5001:80

# Terminal 2 - Order Service
kubectl port-forward service/order-service 5002:80
```


## Testing

### 1. Health Checks
```bash
# Product Service
curl http://localhost:5001/health

# Order Service
curl http://localhost:5002/health
```

### 2. Product Service
```bash
# Get all products
curl http://localhost:5001/products

# Get specific product
curl http://localhost:5001/products/1

# Get stock level
curl http://localhost:5001/products/1/stock
```

### 3. Order Service
```bash
# Get all orders
curl http://localhost:5002/orders

# Create an order
curl -X POST http://localhost:5002/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ]
  }'

# Get specific order
curl http://localhost:5002/orders/1
```

### 4. API Documentation
- Product Service: http://localhost:5001/docs
- Order Service: http://localhost:5002/docs