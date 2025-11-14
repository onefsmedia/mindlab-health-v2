# MindLab Health - FastAPI Application
# Multi-stage build for optimized production image

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder to mindlab user home
COPY --from=builder /root/.local /home/mindlab/.local

# Copy application code from parent directory
COPY ../*.py ./
COPY ../frontend/ ./frontend/

# Create non-root user and set ownership
RUN useradd -m -u 1000 mindlab && \
    chown -R mindlab:mindlab /app /home/mindlab/.local && \
    chmod -R 755 /home/mindlab/.local

# Switch to non-root user
USER mindlab

# Update PATH to include .local binaries (accessible by mindlab user)
ENV PATH=/home/mindlab/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application (07_main.py contains the FastAPI app)
CMD ["uvicorn", "07_main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
