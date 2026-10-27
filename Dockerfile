FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py remote_server.py auth.py ./
RUN useradd --create-home appuser && mkdir /app/data && chown appuser:appuser /app/data
USER appuser
ENV SOLVERO_DATA_DIR=/app/data
ENV HOST=0.0.0.0
EXPOSE 8000
CMD ["python", "remote_server.py"]
