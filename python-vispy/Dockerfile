# WorldWind Python - VisPy 3D Globe Visualization
# Docker container for running the application

FROM python:3.11-slim

# Install system dependencies for OpenGL and GUI
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglu1-mesa \
    freeglut3 \
    mesa-utils \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY worldwind.py .
COPY download_textures.py .
COPY README.md .

# Set environment variables for display
ENV DISPLAY=:0
ENV QT_QPA_PLATFORM=xcb

# Create textures directory
RUN mkdir -p textures

# Make scripts executable
RUN chmod +x worldwind.py download_textures.py

# Default command
CMD ["python", "worldwind.py"]
