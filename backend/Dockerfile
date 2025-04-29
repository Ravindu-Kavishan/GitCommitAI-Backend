# Backend/Dockerfile

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

RUN apt-get update && apt-get install -y build-essential

# Copy requirements file from Backend/
COPY backend/requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app source code from Backend/
COPY . .

EXPOSE 8000

CMD ["uvicorn", "Backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
