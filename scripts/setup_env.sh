#!/usr/bin/env bash
set -euo pipefail

source .env

# Required variables checked by the submission system.
export HF_TOKEN
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export IMAGE_NAME="my-pattern-env:latest"

echo "Environment variables exported for this shell session."
echo "Tip: run 'source scripts/setup_env.sh' to keep them in your current terminal."
