# Setup and Deployment Guide

## Prerequisites

### Required Software
- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Kubernetes**: 
  - Option 1: Docker Desktop with Kubernetes enabled (recommended for local development)
  - Option 2: Minikube ([Install Minikube](https://minikube.sigs.k8s.io/docs/start/))
  - Option 3: Kind ([Install Kind](https://kind.sigs.k8s.io/docs/user/quick-start/))
- **kubectl**: Kubernetes command-line tool ([Install kubectl](https://kubernetes.io/docs/tasks/tools/))
- **Python**: 3.9.6 (only needed for local development, not required for Docker deployment)

### Verify Installation
```bash
docker --version
kubectl version --client
```


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

**Option A: Docker Desktop**
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

**Option A: Port Forwarding (Recommended for Testing)**
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

## Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Services Not Communicating
```bash
# Verify service endpoints
kubectl get endpoints

# Test connectivity from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Inside pod: wget -O- http://product-service/products
```

### Image Pull Errors
```bash
# Ensure images are loaded into cluster
docker images | grep product-service
docker images | grep order-service

```

## Cleanup

```bash
# Delete deployments and services
kubectl delete -f k8s/product-service-deployment.yaml
kubectl delete -f k8s/order-service-deployment.yaml

# Delete all resources
kubectl delete all --all

# Stop cluster (Minikube)
minikube stop

# Delete cluster (Kind)
kind delete cluster --name lab4-cluster
```

