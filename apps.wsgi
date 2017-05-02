from os import environ
import sys

sys.path.insert(0, "/var/www/apps")

def application(req_environ, start_response):
    environ['APPS_JSON_PASS'] = req_environ['APPS_JSON_PASS']
    environ['APPS_JSON_URL']  = req_environ['APPS_JSON_URL']
    environ['APPS_EB_IDP_URL'] = req_environ['APPS_EB_IDP_URL']
    
    from main import app as _application

    return _application(req_environ, start_response)
