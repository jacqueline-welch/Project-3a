FROM python:3.9-slim-buster

WORKDIR /Project-3a

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "Project-3a.py"]