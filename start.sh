#!/bin/bash
set -e

echo "Installing Playwright browsers..."
playwright install chromium --with-deps || playwright install chromium

echo "Starting API service..."
exec python api_service.py
