FROM python:3.7-slim-buster

RUN apt-get update \
    && apt-get install -y curl gnupg2 g++ unixodbc-dev python3-dev
  
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get -y install msodbcsql17

WORKDIR /choco

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "db_test.py"]
