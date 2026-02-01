# DigitalOcean Kubernetes (DOKS) Deployment - Phase V

## Prerequisites
- DigitalOcean account with DOKS cluster
- doctl CLI installed and authenticated
- kubectl configured for DOKS
- Helm 3.x installed
- Docker for building images
- DigitalOcean Container Registry

## 1. Create DOKS Cluster
```bash
# Install doctl
choco install doctl  # Windows
brew install doctl   # macOS

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3 \
  --auto-upgrade

# Save kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster
```

## 2. Setup Container Registry
```bash
# Create registry
doctl registry create todo-registry

# Login to registry
doctl registry login

# Build and push images
docker build -t registry.digitalocean.com/todo-registry/todo-backend:latest -f backend/Dockerfile.prod backend/
docker build -t registry.digitalocean.com/todo-registry/todo-frontend:latest -f frontend/Dockerfile.prod frontend/
docker push registry.digitalocean.com/todo-registry/todo-backend:latest
docker push registry.digitalocean.com/todo-registry/todo-frontend:latest

# Enable registry integration with cluster
doctl kubernetes cluster registry add todo-cluster
```

## 3. Install Dapr
```bash
# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Initialize Dapr in cluster
dapr init -k --enable-mtls --enable-ha

# Verify
dapr status -k
```

## 4. Deploy Infrastructure
```bash
# Create namespace
kubectl apply -f k8s/digitalocean/doks-deployment.yaml

# Create secrets
kubectl create secret generic todo-secrets -n todo-app \
  --from-literal=database-url='postgresql://user:pass@host:5432/db' \
  --from-literal=jwt-secret='your-jwt-secret' \
  --from-literal=openrouter-api-key='your-api-key'

# Deploy Kafka
kubectl apply -f k8s/digitalocean/kafka-deployment.yaml

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app=kafka -n todo-app --timeout=300s

# Deploy Dapr components
kubectl apply -f k8s/digitalocean/dapr-components.yaml
```

## 5. Deploy with Helm
```bash
# Add repos
helm repo add bitnami https://charts.bitnami.com/bitnami
helm dependency update helm/todo-app

# Install Redis
helm install redis bitnami/redis -n todo-app \
  --set auth.enabled=false \
  --set architecture=standalone

# Deploy application
helm install todo-app helm/todo-app \
  --namespace todo-app \
  --set image.backend.repository=registry.digitalocean.com/todo-registry/todo-backend \
  --set image.frontend.repository=registry.digitalocean.com/todo-registry/todo-frontend \
  --set dapr.enabled=true \
  --set kafka.enabled=false \  # Using external Kafka
  --set redis.enabled=false    # Using external Redis
```

## 6. Configure DNS & SSL
```bash
# Get LoadBalancer IP
kubectl get svc todo-frontend -n todo-app

# Add DNS A record pointing to LoadBalancer IP
# Add SSL certificate in DigitalOcean dashboard
```

## 7. Monitoring
```bash
# Install Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3001:80 -n monitoring
# Default: admin / prom-operator
```

## Architecture
```
┌──────────────────────────────────────────────────────────────┐
│                    DigitalOcean DOKS                         │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Frontend   │  │  Frontend   │  │  Frontend   │         │
│  │   (Next.js) │  │   (Next.js) │  │   (Next.js) │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│                    ┌─────▼─────┐                           │
│                    │  Ingress  │                           │
│                    │   (Nginx) │                           │
│                    └─────┬─────┘                           │
│                          │                                  │
│  ┌───────────────────────┼───────────────────────┐         │
│  │                       │                       │         │
│  │  ┌─────────────┐  ┌───▼───────┐  ┌─────────┐ │         │
│  │  │   Backend   │  │  Backend  │  │ Backend │ │         │
│  │  │  + Dapr     │  │  + Dapr   │  │ + Dapr  │ │         │
│  │  └──────┬──────┘  └─────┬─────┘  └────┬────┘ │         │
│  │         │               │              │      │         │
│  │         └───────────────┼──────────────┘      │         │
│  │                         │                     │         │
│  │  ┌──────────────────────┼──────────────────┐  │         │
│  │  │                      │                  │  │         │
│  │  │  ┌─────────┐    ┌────▼────┐   ┌──────┐ │  │         │
│  │  │  │  Redis  │    │  Kafka  │   │ Neon │ │  │         │
│  │  │  │ (Cache) │    │(Events) │   │ (DB) │ │  │         │
│  │  │  └─────────┘    └─────────┘   └──────┘ │  │         │
│  │  └────────────────────────────────────────┘  │         │
│  └──────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────┘
```

## Useful Commands
```bash
# Check cluster status
doctl kubernetes cluster get todo-cluster

# View all resources
kubectl get all -n todo-app

# Check Dapr status
dapr status -k

# View Kafka topics
kubectl exec -it kafka-0 -n todo-app -- kafka-topics.sh --list --bootstrap-server localhost:9092

# Scale deployment
kubectl scale deployment todo-backend --replicas=5 -n todo-app

# Rollback
kubectl rollout undo deployment/todo-backend -n todo-app

# Delete cluster (cleanup)
doctl kubernetes cluster delete todo-cluster
```
