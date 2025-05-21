from flask import Blueprint

systems_bp = Blueprint('systems', __name__)

from . import systems
from . import login
from . import users
from . import roles
from . import tanks
from . import materials
from . import sensors
from . import reports
from . import backups
