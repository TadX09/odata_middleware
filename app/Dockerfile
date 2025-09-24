FROM python:3.12

WORKDIR /code

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar requirements desde raíz del contexto
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copiar el código y archivos necesarios desde raíz del proyecto
COPY app /code/app
#COPY tests /code/tests
#COPY pytest.ini /code/pytest.ini

# Ejecutar tests
#RUN pytest

# Crear carpeta de datos
RUN mkdir -p /code/app/data && chmod 777 /code/app/data

CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8080"]
