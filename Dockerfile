FROM python:3.10
RUN apt-get update && apt-get install -y libffi-dev libnacl-dev python3-dev
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]