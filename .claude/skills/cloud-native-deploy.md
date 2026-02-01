# Cloud-Native Deployment Skill

This skill provides reusable cloud-native deployment blueprints for the AI-Powered Todo application.

## Available Blueprints

### 1. Minikube Local Deployment
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Build images in Minikube's Docker
eval $(minikube docker-env)
docker build -t todo-backend:latest -f backend/Dockerfile.prod backend/
docker build -t todo-frontend:latest -f frontend/Dockerfile.prod frontend/

# Deploy with Helm
helm install todo-app helm/todo-app --namespace todo-app --create-namespace
```

### 2. DigitalOcean DOKS Deployment
```bash
# Create DOKS cluster
doctl kubernetes cluster create todo-cluster --region nyc1 --size s-2vcpu-4gb --count 3

# Setup registry
doctl registry create todo-registry
doctl registry login

# Push images
docker push registry.digitalocean.com/todo-registry/todo-backend:latest
docker push registry.digitalocean.com/todo-registry/todo-frontend:latest

# Deploy
kubectl apply -f k8s/digitalocean/
helm install todo-app helm/todo-app -n todo-app
```

### 3. Dapr Sidecar Setup
```bash
# Install Dapr
dapr init -k

# Deploy components
kubectl apply -f k8s/digitalocean/dapr-components.yaml

# Verify
dapr status -k
```

### 4. Kafka Event Streaming
```bash
# Deploy Kafka
kubectl apply -f k8s/digitalocean/kafka-deployment.yaml

# Create topics
kubectl exec -it kafka-0 -- kafka-topics.sh --create --topic task-events --bootstrap-server localhost:9092
kubectl exec -it kafka-0 -- kafka-topics.sh --create --topic notifications --bootstrap-server localhost:9092
```

## Usage

To use this skill, invoke it when deploying:
- `/cloud-deploy minikube` - Deploy to local Minikube
- `/cloud-deploy doks` - Deploy to DigitalOcean
- `/cloud-deploy dapr` - Setup Dapr components
- `/cloud-deploy kafka` - Setup Kafka messaging
