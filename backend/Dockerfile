FROM python:3.11.4

WORKDIR /backend

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-u", "main_download.py" ]