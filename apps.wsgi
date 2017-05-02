import sys
sys.path.insert(0, "/var/www/apps")

from os import environ

from main import app as _application

def application(req_environ, start_response):
  environ['APPS_JSON_PASS'] = req_environ['APPS_JSON_PASS']
  environ['APPS_JSON_URL']  = req_environ['APPS_JSON_URL']
  environ['APPS_EB_IDP_URL'] = req_environ['APPS_EB_IDP_URL']

  return _application(req_environ, start_response)
