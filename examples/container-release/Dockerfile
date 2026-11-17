# Pinned base observed locally; pinning identifies bytes, not vulnerability safety.
FROM python:3.13-slim@sha256:ffb752e139c0a19692a43af8d8523b274222dd68eebad5d583b45c2201c6e30a
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY service.py /app/service.py
USER 10001:10001
EXPOSE 8080
CMD ["python", "/app/service.py"]
