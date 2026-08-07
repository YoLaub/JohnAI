# Build context is the repo root (see server/docker-compose.yaml: context: ..)
# so this stage can reach client/ to build the PWA static assets.
FROM node:20-slim AS client-builder
WORKDIR /client
COPY client/package*.json ./
RUN npm install
COPY client/ .
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server/ .

# Client PWA static assets, served by main.py at "/"
COPY --from=client-builder /client/dist ./static

# Create persistent data volume directory
RUN mkdir -p /app/data

EXPOSE 8000

ENV PORT=8000
ENV DB_PATH=/app/data/johnai_memory.db
ENV UPLOAD_DIR=/app/data/uploads

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
