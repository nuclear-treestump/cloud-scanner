FROM python:3.11-alpine

WORKDIR /cloudscanner

COPY cloud_scanner /cloudscanner

COPY requirements.txt .
RUN python3 -m pip install --upgrade pip 
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "--app", "/cloudscanner/app.py", "run", "-p", "5000"]

