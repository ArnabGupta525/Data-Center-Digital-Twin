# Data Center Digital Twin - Docker Image
# Multi-stage build for optimized image size

FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:0

# Install system dependencies for PyQt5 and GUI support
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PyQt5 dependencies
    libqt5gui5 \
    libqt5widgets5 \
    libqt5core5a \
    libqt5dbus5 \
    libqt5network5 \
    libqt5printsupport5 \
    # X11 and display dependencies
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxkbcommon-x11-0 \
    libxcb-xkb1 \
    libxcb-cursor0 \
    libfontconfig1 \
    libfreetype6 \
    libdbus-1-3 \
    # Additional utilities
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/db /app/models /app/data /app/logs

# Initialize the database
RUN python init_db.py

# Generate sample dataset for plug-and-play experience
RUN echo "Generating sample dataset..." && \
    python generate_sample_data.py

# Train optimizer models (this may take a few minutes)
RUN echo "Training optimizer models..." && \
    python train_optimizer.py || echo "Warning: Optimizer training failed, will run without optimization features"

# Create a non-root user for security
RUN useradd -m -u 1000 dcuser && \
    chown -R dcuser:dcuser /app

# Switch to non-root user
USER dcuser

# Make entrypoint script executable
COPY --chown=dcuser:dcuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Expose any ports if needed (currently not used, but reserved for future web interface)
EXPOSE 8080
EXPOSE 8765

# Set the entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command
CMD ["python", "what_if_engine.py"]
