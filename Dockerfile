FROM python:3.10
# Install library pendukung suara
RUN apt-get update && apt-get install -y libffi-dev libnacl-dev python3-dev
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
# Port 8080 harus dibuka untuk Web Service
EXPOSE 8080
CMD ["python", "main.py"]
