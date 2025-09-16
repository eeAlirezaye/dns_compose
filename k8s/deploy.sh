#!/bin/bash
# deploy.sh - Deploy all services to Kubernetes

echo "🚀 Deploying DNS Lookup Application to Kubernetes..."

# Create namespace first
echo "Creating namespace..."
kubectl apply -f namespace.yaml

# Apply ConfigMap and Secrets
echo "Applying ConfigMap and Secrets..."
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml

# Deploy MySQL first (other services depend on it)
echo "Deploying MySQL database..."
kubectl apply -f mysql-deployment.yaml

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
kubectl wait --for=condition=ready pod -l app=mysql -n domain-lookup-app --timeout=300s

# Deploy backend services
echo "Deploying backend services..."
kubectl apply -f dns-resolver-deployment.yaml
kubectl apply -f db-service-deployment.yaml
kubectl apply -f health-service-deployment.yaml
kubectl apply -f config-service-deployment.yaml

# Wait for backend services to be ready
echo "Waiting for backend services to be ready..."
kubectl wait --for=condition=ready pod -l app=dns-resolver-service -n domain-lookup-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=db-service -n domain-lookup-app --timeout=300s

# Deploy gateway service
echo "Deploying gateway service..."
kubectl apply -f gateway-service-deployment.yaml

# Wait for gateway to be ready
echo "Waiting for gateway service to be ready..."
kubectl wait --for=condition=ready pod -l app=gateway-service -n domain-lookup-app --timeout=300s

# Deploy frontend
echo "Deploying frontend..."
kubectl apply -f frontend-deployment.yaml

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n domain-lookup-app --timeout=300s

echo "✅ Deployment complete!"
echo ""
echo "📋 Check deployment status:"
echo "kubectl get pods -n domain-lookup-app"
echo "kubectl get services -n domain-lookup-app"
echo "kubectl get ingress -n domain-lookup-app"
echo ""
echo "🔍 Access your application:"
echo "If using port-forward: kubectl port-forward svc/frontend-service 3000:80 -n domain-lookup-app"
echo "Then access: http://localhost:3000"
echo ""
echo "📊 Monitor logs:"
echo "kubectl logs -f deployment/gateway-service -n domain-lookup-app"