# Image compatible with ARM and x64
FROM python:3.11-slim

# Where the application will work
WORKDIR /app

# Copy content from the source -> container env
COPY . .

# Dependencies installation
RUN pip install --no-cache-dir -r requirements.txt

# Start bot
CMD ["python", "app/bot.py"]
