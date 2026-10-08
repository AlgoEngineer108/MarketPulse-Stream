FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir dash plotly pandas cassandra-driver openpyxl gunicorn

EXPOSE 8050

CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "2", "--threads", "4", \
     "--timeout", "90", "--graceful-timeout", "30", "dashboard:server"]