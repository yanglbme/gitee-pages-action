FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade --no-cache-dir requests

COPY main.py .

CMD ["main.py","-OPTIONAL_FLAG"]