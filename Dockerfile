FROM python:3.11-slim

# Set the working directory
WORKDIR /backend

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]