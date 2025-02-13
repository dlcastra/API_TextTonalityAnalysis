ARG PYTHON_VERSION=3.13.0
FROM python:${PYTHON_VERSION} AS base
ENV DOCKERIZED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash admin
WORKDIR /usr/src/service

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Switch to a non-privileged user if necessary (optional)
USER admin

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8030

# Run the application.
CMD uvicorn 'application:app' --host=0.0.0.0 --port=8030
