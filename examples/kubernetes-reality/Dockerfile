FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY server.py probe.py /app/
USER 10001:10001
EXPOSE 8000
CMD ["python", "/app/server.py"]
