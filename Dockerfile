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

# Expose the port Jupyter Notebook will run on
EXPOSE 8888

# Set the command to run Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
