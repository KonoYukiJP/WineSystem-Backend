# wine_system.py

from flask import Flask
from blueprints.systems import systems_bp
from blueprints.users import users_bp
from blueprints.roles import roles_bp
from blueprints.tanks import tanks_bp
from blueprints.materials import materials_bp
from blueprints.sensors import sensors_bp
from blueprints.actions import actions_bp
from blueprints.resources import resources_bp
from blueprints.works import works_bp
from blueprints.operations import operations_bp
from blueprints.features import features_bp
from blueprints.reports import reports_bp
from blueprints.backups import backups_bp

app = Flask(__name__)

# Blueprintの登録
app.register_blueprint(systems_bp, url_prefix = '/systems')
app.register_blueprint(users_bp, url_prefix = '/users')
app.register_blueprint(roles_bp, url_prefix = '/roles')
app.register_blueprint(tanks_bp, url_prefix = '/tanks')
app.register_blueprint(materials_bp, url_prefix = '/materials')
app.register_blueprint(sensors_bp, url_prefix = '/sensors')
app.register_blueprint(actions_bp, url_prefix = '/actions')
app.register_blueprint(resources_bp, url_prefix = '/resources')
app.register_blueprint(works_bp, url_prefix = '/works')
app.register_blueprint(operations_bp, url_prefix = '/operations')
app.register_blueprint(features_bp, url_prefix = '/features')
app.register_blueprint(reports_bp, url_prefix = '/reports')
app.register_blueprint(backups_bp, url_prefix = '/backups')

if __name__ == '__main__':
    app.run(debug=True)
