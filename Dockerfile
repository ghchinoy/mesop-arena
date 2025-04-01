FROM python:3.11-slim

WORKDIR .

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080

# Run the application
CMD mesop main.py --port=$PORT
