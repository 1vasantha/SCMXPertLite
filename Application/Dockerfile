FROM python:3

WORKDIR .

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "SCM:app", "--reload", "--host=0.0.0.0","--port= 8000"]
