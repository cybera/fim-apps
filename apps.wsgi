from os import environ
import sys
import logging

sys.path.insert(0, "/var/www/apps")

def application(req_environ, start_response):
    environ['APPS_MANAGE_USER'] = req_environ['APPS_MANAGE_USER']
    environ['APPS_MANAGE_PASS'] = req_environ['APPS_MANAGE_PASS']
    environ['APPS_MANAGE_URL']  = req_environ['APPS_MANAGE_URL']
    environ['APPS_PDP_PASS'] = req_environ['APPS_PDP_PASS']
    environ['APPS_PDP_URL']  = req_environ['APPS_PDP_URL']
    environ['APPS_EB_IDP_URL'] = req_environ['APPS_EB_IDP_URL']
    environ['APPS_HIDE_PREFIX'] = req_environ['APPS_HIDE_PREFIX']

    from main import app as _application
    logging.basicConfig(stream=sys.stderr)

    return _application(req_environ, start_response)
