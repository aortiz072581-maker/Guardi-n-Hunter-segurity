FROM python:3.11-slim
LABEL security.level="military-grade"
WORKDIR /app
COPY guardian_hunter/ ./guardian_hunter/
RUN chmod -R 700 /app && useradd -m -u 10244 guardian && chown -R guardian:guardian /app
USER guardian
CMD ["python3", "-m", "guardian_hunter.core"]
