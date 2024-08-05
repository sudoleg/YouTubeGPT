FROM python:3.12.4

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install ffmpeg

# Copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Copy application's code
COPY . /app/

# Streamlit's configuration options
ENV PYTHONPATH="/app"
ENV STREAMLIT_CLIENT_TOOLBAR_MODE="viewer"
ENV STREAMLIT_SERVER_PORT=8501
ENV ENVIRONMENT=production

# Expose port for the application
EXPOSE 8501

# Add healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Set the entrypoint
ENTRYPOINT ["streamlit", "run", "main.py", "--server.address=0.0.0.0"]
