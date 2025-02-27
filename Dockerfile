# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set non-interactive mode to prevent tzdata prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables for SNPE and NDK
ENV SNPE_ROOT=/app/sdk/v2.22.6.240515/qairt/2.22.6.240515
ENV ANDROID_NDK_ROOT=/app/sdk/android-ndk-r26c-linux/android-ndk-r26c

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    python3.10 \
    python3-pip \
    python3.10-venv \
    libtinfo5 \
    && rm -rf /var/lib/apt/lists/*  # Cleanup to reduce image size

# Copy all project files into the container
COPY . .

# Make setup_env.sh executable
RUN chmod +x setup_env.sh

# Run the environment setup script
RUN ./setup_env.sh

# Ensure SNPE environment variables are available in every new shell
RUN echo "source ${SNPE_ROOT}/bin/envsetup.sh" >> /etc/bash.bashrc

# Expose the Flask app on port 5000
EXPOSE 5000

# Run the Flask app on the specified IP address
CMD ["/bin/bash", "-c", "source ${SNPE_ROOT}/bin/envsetup.sh && python3 app.py --host=192.168.1.125 --port=5000"]
