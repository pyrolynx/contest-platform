FROM python:3.7-slim

WORKDIR /opt

COPY requirements.txt requirements.txt

RUN pip3.7 install -r requirements.txt

COPY . .

RUN mkdir -p data/solutions && mkdir -p data/tasks

EXPOSE 5000

ENV PYTHONPATH=/opt

ENTRYPOINT ["python3.7", "application/web.py"]