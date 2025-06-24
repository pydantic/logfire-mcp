FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install git (needed for dynamic versioning) and uv
RUN apt-get update && apt-get install -y git && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install uv

# Copy git directory for versioning
COPY .git ./.git

# Copy project files
COPY pyproject.toml uv.lock ./
COPY logfire_mcp/ ./logfire_mcp/
COPY README.md ./

# Install the package
RUN uv pip install --system .

# Remove git directory to reduce image size
RUN rm -rf .git

# Set environment variable to indicate we're running in Docker
ENV DOCKER_CONTAINER=true

# Run the MCP server
ENTRYPOINT ["python", "-m", "logfire_mcp"]