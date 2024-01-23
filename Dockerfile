FROM python:3.11
WORKDIR /app
COPY ./pdns-acme-api/ /app/
RUN mkdir -p /var/lib/pdns-acme-api
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
