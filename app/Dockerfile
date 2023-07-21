FROM python:latest

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

#CMD ["python3", "-u", "app.py"]
CMD ["gunicorn", "-w 4", "app:server", "-b :8080"]
 