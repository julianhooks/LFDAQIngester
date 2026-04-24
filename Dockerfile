# Stage 1 build: pull from python slim source
ARG PYTHON_VERSION=3.14.3
FROM python:$PYTHON_VERSION-slim AS builder

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=0

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

#
WORKDIR /build

RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    curl \
    unzip \
    udev \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN curl https://files.labjack.com/installers/LJM/Linux/AArch64/release/LabJack-LJM_2025-05-07.zip > labjackDrivers.zip
RUN unzip labjackDrivers.zip
RUN ./labjack_ljm_installer.run -- --no-restart-device-rules 

COPY requirements.txt .

RUN pip install -r requirements.txt

# Stage 2 build
FROM builder 

WORKDIR /app
COPY . .

# Set environment Variables
ENV DBURL="100.64.192.19"

# Run the application.
CMD ["python", "src/main.py"]
