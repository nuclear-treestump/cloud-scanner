FROM python:3.11-alpine

WORKDIR /cloudscanner

COPY cloud_scanner /cloudscanner

COPY requirements.txt .
RUN python3 -m pip install --upgrade pip 
RUN pip install -r requirements.txt

ENV FLASK_APP=cloudscanner/app.py

EXPOSE 5000

CMD ["python3", "app.py"]

