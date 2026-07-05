FROM python:3.11-slim

WORKDIR /root/task

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /root/task/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /root/task

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
