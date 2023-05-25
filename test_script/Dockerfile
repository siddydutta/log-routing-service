FROM python:3.9

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY test_script.py .

CMD ["python", "test_script.py"]
