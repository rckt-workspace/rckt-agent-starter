#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Building Frontend React SPA..."
cd frontend
npm install
npm run build
cd ..

echo "Build successfully completed! Frontend assets generated in frontend/dist."
