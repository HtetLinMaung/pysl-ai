FROM python:3.9-slim-buster

# Install dependencies
RUN pip install fastapi uvicorn opencv-python-headless numpy dlib face-recognition pytesseract Pillow python-multipart requests

# Set working directory
WORKDIR /app

# Copy the code into the container
COPY . .

# Expose the required port
EXPOSE 8000

# Run the server with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
