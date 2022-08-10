FROM python:3.6.9

WORKDIR /app
COPY . /app

EXPOSE 5000
RUN pip3 install -r requirements.txt

CMD ["python", "/app/application.py"]
