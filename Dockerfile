# Start from a lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy everything into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    openenv-core \
    openai \
    httpx

# Expose port 7860 (required by Hugging Face Spaces)
EXPOSE 7860

# Health check for HF Spaces
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.post('http://localhost:7860/health')" || exit 1

# Command to start the server when the container runs
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
