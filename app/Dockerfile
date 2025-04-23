FROM openfabric/tee-python-cpu:dev

# Copy only necessary files for Poetry installation
COPY app/pyproject.toml ./pyproject.toml

# Install dependencies using Poetry
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade poetry && \
    python3 -m poetry install --only main && \
    rm -rf ~/.cache/pypoetry/{cache,artifacts}

# Copy the rest of the source code into the container
COPY app/ ./app/

# Expose port for the app
EXPOSE 8888

# Start the app using the start.sh script
CMD ["sh","app/start.sh"]