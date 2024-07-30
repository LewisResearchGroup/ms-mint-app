# Use the official Python image from the Docker Hub
FROM python:3.12

# Expose the desired port
EXPOSE 9999

# Set environment variables
ENV SQLALCHEMY_DATABASE_URI sqlite:///data/mint.db
ENV MINT_DATA_DIR /data/

# Create the data directory
RUN mkdir -p /data

# Upgrade pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# Install system dependencies required for building certain Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    hdf5-tools \
    gfortran \
    libatlas-base-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into /app in the container
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Install Python dependencies
RUN pip install -e . && pip list

# Make the entrypoint script executable and run it
CMD ["./entrypoint.sh"]
