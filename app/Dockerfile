FROM python:latest

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN pip3 install pip install supervisor

COPY . .

EXPOSE 8080

CMD ["python3", "-u", "app.py"]
 