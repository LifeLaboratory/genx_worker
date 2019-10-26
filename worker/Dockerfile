FROM python:3.6

WORKDIR /worker

copy app /app

RUN pip install -r requirments.txt
CMD ["python", "app.py"]
