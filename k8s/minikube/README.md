# Minikube Local Deployment Guide (Phase IV)

## Prerequisites
- Docker Desktop
- Minikube installed (`choco install minikube` or `brew install minikube`)
- Helm 3.x (`choco install kubernetes-helm`)
- kubectl (`choco install kubernetes-cli`)
- kubectl-ai plugin (optional)
- kagent (optional)

## Quick Start

### 1. Start Minikube
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Install Dapr
```bash
# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Initialize Dapr in Kubernetes
dapr init -k
dapr status -k
```

### 3. Build Docker Images
```bash
# Point shell to minikube's docker
eval $(minikube docker-env)

# Build images
docker build -t todo-backend:latest -f backend/Dockerfile.prod backend/
docker build -t todo-frontend:latest -f frontend/Dockerfile.prod frontend/
```

### 4. Deploy with Helm
```bash
# Add dependencies
helm repo add bitnami https://charts.bitnami.com/bitnami
helm dependency update helm/todo-app

# Install
helm install todo-app helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --set secrets.jwtSecret=your-secret-key \
  --set secrets.openrouterApiKey=your-api-key \
  --set secrets.databaseUrl=postgresql://user:pass@host/db
```

### 5. Access Application
```bash
# Get Minikube IP
minikube ip

# Or use tunnel for LoadBalancer
minikube tunnel

# Access at http://localhost or http://<minikube-ip>
```

## kubectl-ai Integration (Bonus)
```bash
# Install kubectl-ai
kubectl krew install ai

# Use AI to manage resources
kubectl ai "scale todo-backend to 5 replicas"
kubectl ai "show me pods with high memory usage"
kubectl ai "create a job to backup the database"
```

## kagent Integration (Bonus)
```bash
# Install kagent
pip install kagent

# Configure kagent
kagent init --cluster minikube

# Use kagent for AI-powered operations
kagent "deploy new version of backend"
kagent "rollback frontend to previous version"
kagent "analyze cluster health"
```

## Useful Commands
```bash
# Check all resources
kubectl get all -n todo-app

# View logs
kubectl logs -f deployment/todo-app-backend -n todo-app

# Port forward for debugging
kubectl port-forward svc/todo-app-backend 8000:8000 -n todo-app

# Scale manually
kubectl scale deployment todo-app-backend --replicas=5 -n todo-app

# Helm upgrade
helm upgrade todo-app helm/todo-app -n todo-app

# Uninstall
helm uninstall todo-app -n todo-app
```

## Troubleshooting
```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check Dapr sidecar
dapr status -k
kubectl logs <pod-name> -c daprd -n todo-app
```
