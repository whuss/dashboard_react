# Webinterface for the Reprolight Database

Start in development mode using

```
$ python3 app.py
```

The programm then prints the url of the webserver
on the terminal:

```
* Serving Flask app "app" (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 250-654-657
```

The location of the database can be changed by editing
the **_host** variable in db.py

Setup redis:

https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04

# Changes to redis config:

maxmemory 500mb
maxmemory-policy volatile-lfu
supervised systemd
