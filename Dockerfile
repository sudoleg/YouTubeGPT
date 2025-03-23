FROM python:3.12.9-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}"
ENV PIP_ROOT_USER_ACTION=ignore

# Copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt .

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

FROM python:3.12.9-alpine as production

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}"

# Copy application's code and dependencies
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
