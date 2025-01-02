FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Node.js in a single layer
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libzmq3-dev \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt package.json package-lock.json* ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir jupyter \
    && pip install --no-cache-dir -r requirements.txt


# Install Node.js dependencies
RUN npm install -g ijavascript \
    && ijsinstall

# Copy application code
COPY . .

# Configure container
EXPOSE 8888
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]