ARG PYTHON_VERSION=3.14.3
FROM python:$PYTHON_VERSION-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=0

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layers

# Copy the source code into the container.
COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

	
# RUN python -m pip install --break-system-packages -r requirements.txt 


# Set environment Variables
ENV DBURL="100.64.192.19"

# Run the application.
CMD["python", "src/main.py"]

