# Backend Dockerfile (Flask)
FROM python:latest

# Set the working directory
WORKDIR /app

COPY docker/dev/backend/devmode.sh /usr/local/bin/devmode.sh

EXPOSE 5000

CMD ["devmode.sh"]
