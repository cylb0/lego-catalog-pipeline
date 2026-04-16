FROM blendergrid/blender:latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 python3-pip wget unzip && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages boto3

RUN wget https://github.com/TobyLobster/ImportLDraw/archive/refs/heads/master.zip -O /tmp/ldraw_addon.zip && \
    unzip /tmp/ldraw_addon.zip -d /tmp/ && \
    mv /tmp/ImportLDraw-master /opt/ImportLDraw

COPY src/conversion/ldraw_to_gltf_converter.py .
COPY src/conversion/blender_script.py .

ENTRYPOINT ["python3", "ldraw_to_gltf_converter.py"]