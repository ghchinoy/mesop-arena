FROM python:3.11-slim

WORKDIR .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port that your Mesop app will run on.
# This is important so that Docker knows to forward traffic to this port.
EXPOSE 8080

# Run the Mesop application using Gunicorn as a WSGI server
# Gunicorn is recommended for production deployments
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "main:me"]
