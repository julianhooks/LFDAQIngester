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

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \	
    python -m pip install --break-system-packages -r requirements.txt 

# Copy the source code into the container.
COPY . .

# Set environment Variables
ENV DBURL="100.64.192.19"

# Run the application.
CMD sh

