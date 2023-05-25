# Use a Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files into the container
COPY /App/bot.py /app/
COPY requirements.txt /app/

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the token build argument (default value is empty)
ARG DISCORD_TOKEN=""

# Set the environment variable using the build argument value
ENV DISCORD_TOKEN=$DISCORD_TOKEN

# Run the bot script inside the container
CMD ["python", "bot.py"]
