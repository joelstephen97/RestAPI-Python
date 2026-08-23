FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
# the sqlite file lands in /app/data so it can be mounted from the host
ENV DB_PATH=/app/data/database.db
RUN mkdir -p /app/data
ENTRYPOINT ["python", "main.py"]
CMD ["menu"]
