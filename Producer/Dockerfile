FROM python:3

WORKDIR .

COPY requirements.txt .
RUN pip install -r requirements.txt python-dotenv

COPY . .

CMD ["python","producer.py"]