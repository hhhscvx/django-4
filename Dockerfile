FROM python:3.10.12

# Задать переменные среды
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Задать рабочий каталог
WORKDIR /code

# Install dependencies
RUN pip install --upgrade pip setuptools
RUN apt-get pudate && apt-get install -y build-essential python3-dev libpcre3 libpcre3-dev
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy the Django project
COPY . /code/