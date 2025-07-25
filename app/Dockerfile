FROM python:3.12

WORKDIR /code

# Instalar dependencias básicas del sistema
RUN apt-get update && apt-get install -y \
    gnupg2 \
    curl \
    unixodbc \
    unixodbc-dev \
    libodbc1 \
    odbcinst1debian2 \
    && rm -rf /var/lib/apt/lists/*

# Agregar repositorio de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instalar driver de SQL Server
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Configurar el driver en odbcinst.ini
RUN echo "[ODBC Driver 18 for SQL Server]\n\
    Description=Microsoft ODBC Driver 18 for SQL Server\n\
    Driver=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.*.so.1.1\n\
    UsageCount=1" >> /etc/odbcinst.ini

COPY ../requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY .. /code/app

CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8080"]