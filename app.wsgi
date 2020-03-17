python_home = '/home/wilfried/.virtualenvs/infinity'

activate_this = python_home + '/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

from app import app

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app.run()

# ----------------------------------------------------------------------------------------------------------------------
