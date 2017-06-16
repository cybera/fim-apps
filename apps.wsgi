from os import environ
import sys
import logging

sys.path.insert(0, "/var/www/apps")

def application(req_environ, start_response):
    environ['APPS_MULTIDATA_PASS'] = req_environ['APPS_MULTIDATA_PASS']
    environ['APPS_MULTIDATA_URL']  = req_environ['APPS_MULTIDATA_URL']
    environ['APPS_PDP_PASS'] = req_environ['APPS_PDP_PASS']
    environ['APPS_PDP_URL']  = req_environ['APPS_PDP_URL']
    environ['APPS_EB_IDP_URL'] = req_environ['APPS_EB_IDP_URL']

    from main import app as _application
    logging.basicConfig(stream=sys.stderr)

    return _application(req_environ, start_response)
