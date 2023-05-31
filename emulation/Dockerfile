# Use the official image as a parent image
FROM python:3.7
# COPY requirements.txt
COPY requirements.txt /app/requirements.txt
# Set the working directory in the container
WORKDIR /app
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Run the command you want
CMD ["python", "emulate_terminals.py"]

