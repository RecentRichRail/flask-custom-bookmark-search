# Use the official Python image as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV FLASK_APP=app.py
# For Dev Environment
# ENV allow_logging=True
# ENV require_hanko_login=True
# ENV hanko_server_address=http://localhost:8080
# ENV default_search_server_address=http://localhost:80

# Run flask when the container launches
#CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80"]