python_home = '/home/wilfried/.virtualenvs/infinity'

activate_this = python_home + '/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

import sys
sys.path.insert(0, '/home/wilfried/projects/dashboard/')

from app import app as application

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    application.run()

# ----------------------------------------------------------------------------------------------------------------------
