# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required Python packages
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir jupyter \
    && pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get install -y build-essential && \
    apt-get clean 

# Install Node.js (version 20 in this case)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

RUN npm install -g ijavascript
# Set up the IJavascript kernel
RUN ijsinstall

COPY package.json /app/

# Install npm dependencies based on package-lock.json
RUN npm install

# Expose the port Jupyter Notebook will run on
EXPOSE 8888

# Set the command to run Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
