#!/bin/bash
# docker-setup.sh - Login to Docker Hub and prepare for build

echo "🐳 Docker Hub Setup"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "Please enter your Docker Hub credentials:"
read -p "Username: " username
read -s -p "Password: " password
echo ""

# Login to Docker Hub
echo "🔐 Logging in to Docker Hub..."
echo "$password" | docker login --username "$username" --password-stdin

if [ $? -eq 0 ]; then
    echo "✅ Successfully logged in to Docker Hub"
    echo ""
    echo "You can now run the build script:"
    echo "./build-and-push.sh"
else
    echo "❌ Failed to login to Docker Hub"
    exit 1
fi