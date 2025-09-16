#!/bin/bash
# build-and-push.sh - Build and push all Docker images to Docker Hub

# Configuration
DOCKER_USERNAME="spiritualguest"
VERSION_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Building and pushing Docker images to Docker Hub...${NC}"
echo -e "${YELLOW}Docker Username: ${DOCKER_USERNAME}${NC}"
echo -e "${YELLOW}Version Tag: ${VERSION_TAG}${NC}"
echo ""

# Function to build and push image
build_and_push() {
    local service_name=$1
    local service_dir=$2
    local image_name="${DOCKER_USERNAME}/${service_name}:${VERSION_TAG}"
    
    echo -e "${BLUE}📦 Building ${service_name}...${NC}"
    
    # Build the image
    if docker build -t "${image_name}" "${service_dir}"; then
        echo -e "${GREEN}✅ Successfully built ${image_name}${NC}"
        
        # Push the image
        echo -e "${BLUE}🚀 Pushing ${image_name}...${NC}"
        if docker push "${image_name}"; then
            echo -e "${GREEN}✅ Successfully pushed ${image_name}${NC}"
        else
            echo -e "${RED}❌ Failed to push ${image_name}${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Failed to build ${image_name}${NC}"
        return 1
    fi
    echo ""
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if logged in to Docker Hub
if ! docker info | grep -q "Username:"; then
    echo -e "${YELLOW}⚠️  You may not be logged in to Docker Hub.${NC}"
    echo -e "${YELLOW}Please run: docker login${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${BLUE}Starting build and push process...${NC}"
echo ""

# Build and push all services
build_and_push "dns-resolver" "../dns-resolver-service"
build_and_push "db-service" "../db-service"
build_and_push "gateway-service" "../gateway-service"
build_and_push "health-service" "../health-service"
build_and_push "config-service" "../config-service"
build_and_push "dns-frontend" "../front"

echo -e "${GREEN}🎉 All images built and pushed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Images created:${NC}"
echo -e "  ${DOCKER_USERNAME}/dns-resolver:${VERSION_TAG}"
echo -e "  ${DOCKER_USERNAME}/db-service:${VERSION_TAG}"
echo -e "  ${DOCKER_USERNAME}/gateway-service:${VERSION_TAG}"
echo -e "  ${DOCKER_USERNAME}/health-service:${VERSION_TAG}"
echo -e "  ${DOCKER_USERNAME}/config-service:${VERSION_TAG}"
echo -e "  ${DOCKER_USERNAME}/dns-frontend:${VERSION_TAG}"
echo ""
echo -e "${YELLOW}💡 You can now deploy to Kubernetes with:${NC}"
echo -e "  ./deploy.sh"