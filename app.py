# app.py

from flask import Flask

from modules.systems import systems_bp
from modules.actions import actions_bp
from modules.resources import resources_bp
from modules.roles import roles_bp
from modules.users import users_bp
from modules.tanks import tanks_bp
from modules.materials import materials_bp
from modules.sensors import sensors_bp
from modules.works import works_bp
from modules.operations import operations_bp
from modules.features import features_bp
from modules.reports import reports_bp
from modules.backups import backups_bp

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(systems_bp, url_prefix = '/systems')
    app.register_blueprint(actions_bp, url_prefix = '/actions')
    app.register_blueprint(resources_bp, url_prefix = '/resources')
    app.register_blueprint(roles_bp, url_prefix = '/roles')
    app.register_blueprint(users_bp, url_prefix = '/users')
    app.register_blueprint(tanks_bp, url_prefix = '/tanks')
    app.register_blueprint(materials_bp, url_prefix = '/materials')
    app.register_blueprint(sensors_bp, url_prefix = '/sensors')
    app.register_blueprint(works_bp, url_prefix = '/works')
    app.register_blueprint(operations_bp, url_prefix = '/operations')
    app.register_blueprint(features_bp, url_prefix = '/features')
    app.register_blueprint(reports_bp, url_prefix = '/reports')
    app.register_blueprint(backups_bp, url_prefix = '/backups')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug = True)
