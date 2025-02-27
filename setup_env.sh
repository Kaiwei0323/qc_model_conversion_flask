#!/bin/bash

# Exit on any error
set -e

echo "Starting environment setup..."

# Export SNPE_ROOT
echo "SNPE_ROOT is set to: ${SNPE_ROOT}"

# Check Python dependencies
echo "Checking Python dependencies..."
$SNPE_ROOT/bin/check-python-dependency || { echo "Python dependency check failed."; exit 1; }

# Check Linux dependencies
echo "Checking Linux dependencies..."
bash $SNPE_ROOT/bin/check-linux-dependency.sh || { echo "Linux dependency check failed."; exit 1; }

# Install Make if not installed
echo "Installing Make if necessary..."
apt-get update
apt-get install -y make || { echo "Failed to install Make."; exit 1; }

# Export ANDROID_NDK_ROOT
export PATH=${ANDROID_NDK_ROOT}:${PATH}
echo "ANDROID_NDK_ROOT is set to: $ANDROID_NDK_ROOT"

# Check SNPE environment
echo "Checking SNPE environment setup..."
${SNPE_ROOT}/bin/envcheck -c || { echo "SNPE environment check failed."; exit 1; }

# Install Python packages
echo "Installing required Python packages..."
pip install onnx==1.12.0 onnxruntime==1.17.1 ultralytics flask || { echo "Failed to install Python packages."; exit 1; }

# Source SNPE environment setup
echo "Sourcing SNPE environment setup..."
source ${SNPE_ROOT}/bin/envsetup.sh || { echo "Failed to source SNPE environment."; exit 1; }

echo "Environment setup completed successfully."

