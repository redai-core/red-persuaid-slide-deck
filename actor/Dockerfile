FROM apify/actor-python:3.11

USER root

# Install system dependencies for Firefox, Xvfb virtual display, and graphics libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    xauth \
    libgtk-3-0 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxtst6 \
    libdbus-glib-1-2 \
    libxt6 \
    libpci3 \
    libxss1 \
    libnss3 \
    libdrm2 \
    libgbm1 \
    fonts-liberation \
    fonts-noto-color-emoji \
    && mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix \
    && rm -rf /var/lib/apt/lists/*

# Switch back to default unprivileged user for Apify sandbox compatibility
USER myuser

WORKDIR /home/myuser

# Copy requirements and install Python dependencies into user directory
COPY --chown=myuser:myuser requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# Ensure user-installed binaries and camoufox cache are in PATH and accessible
ENV PATH="/home/myuser/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

# Pre-fetch the Camoufox patched Firefox browser binary into /home/myuser/.cache/
RUN python3 -m camoufox fetch

# Copy the actor code and startup script
COPY --chown=myuser:myuser . ./

# Execute via start.sh
CMD ["./start.sh"]
