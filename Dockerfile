FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# Add this line to handle potential bson conflicts
EXPOSE 5001
CMD ["python", "run_server.py"]