# Dockerfile

FROM python:3.6.9
COPY requirements.txt /
RUN pip install --trusted-host=pypi.org --trusted-host=pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt
RUN pip install --trusted-host=pypi.org --trusted-host=pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir gunicorn[gevent]

COPY . /app
WORKDIR /app

ENTRYPOINT ["./gunicorn_starter.sh"]

