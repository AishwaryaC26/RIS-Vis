FROM python:latest

WORKDIR /backend

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-u", "main_download.py" ]