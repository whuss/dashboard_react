# Dockerfile
# Starting from Python 3.6.9 base image
FROM python:3.6.9


# Set the WORKDIR
WORKDIR /app

COPY requirements.txt ./
RUN pip install --trusted-host=pypi.org --trusted-host=pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt
RUN pip install --trusted-host=pypi.org --trusted-host=pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir gunicorn[gevent]

COPY . ./

ENV CACHE_DB mysqlcache
ENV PYTHONPATH .

#ENTRYPOINT ["./gunicorn_starter.sh"]

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

# initialize cache tables
CMD ["python", "scripts/cache_queries.py", "init", "--yes"]