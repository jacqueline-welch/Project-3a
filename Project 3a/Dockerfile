FROM python:3.9-slim-buster

WORKDIR /Project-3a

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "Project-3a.py"]


# docker build -t project 3a .
# docker run -p 5001:5001 --name project-3a-container project3a:latest