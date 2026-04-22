FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# --- SYSTEM ---
RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    unzip \
    python3 \
    python3-pip \
    python3-venv \
    libxrender1 \
    libxext6 \
    libsm6 \
    libxi6 \
    libx11-6 \
    libgl1 \
    libglib2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    libxfixes3 \
    libxrandr2 \
    libxcursor1 \
    libxinerama1 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

# --- PYTHON DEPENDENCIES ---
RUN pip3 install --no-cache-dir \
    boto3 \
    python-dotenv

# --- BLENDER DOWNLOAD AND INSTALL ---
RUN wget https://download.blender.org/release/Blender3.6/blender-3.6.0-linux-x64.tar.xz \
    && tar -xf blender-3.6.0-linux-x64.tar.xz \
    && mv blender-3.6.0-linux-x64 /opt/blender \
    && ln -s /opt/blender/blender /usr/local/bin/blender

ENV BLENDER_PATH=/opt/blender

# --- IMPORTLDRAW ADDON DOWNLOAD AND INSTALL ---
RUN wget https://github.com/TobyLobster/ImportLDraw/archive/refs/heads/master.zip -O /tmp/ldraw_addon.zip && \
    unzip /tmp/ldraw_addon.zip -d /tmp/ && \
    mkdir -p $BLENDER_PATH/3.6/scripts/addons && \
    mv /tmp/ImportLDraw-master $BLENDER_PATH/3.6/scripts/addons/io_scene_importldraw

# --- COPY PIPELINE CODE ---
COPY src/conversion /app/src/conversion
COPY src/messaging /app/src/messaging

ENTRYPOINT ["python3", "-m", "src.conversion.main"]