FROM docker.io/library/python:3.12-slim-trixie

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

# Single worker: game state lives in a module-global dict, not a database.
# A second worker would run a second, disjoint copy of it.
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "1", "--access-logfile", "-", "app:app"]
