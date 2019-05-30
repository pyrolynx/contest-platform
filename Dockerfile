FROM python:3.7-slim

WORKDIR /opt

COPY requirements.txt requirements.txt

RUN pip3.7 install -r requirements.txt

COPY . .

VOLUME /opt/data

EXPOSE 5000

ENV PYTHONPATH=/opt

ENTRYPOINT ["python3.7", "application/web.py"]