FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m vyora && mkdir -p /app/data && chown -R vyora:vyora /app
USER vyora
ENV PORT=8000 PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["sh","-c","python manage.py migrate && exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
