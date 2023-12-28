FROM python:3.11.4

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

#CMD ["gunicorn", "-w 4", "app:server", "-b :8080"]
CMD ["python3", "-u", "app.py"]
