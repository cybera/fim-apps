#!/usr/bin/env python2

import flask
import requests
import logging
import os

app = flask.Flask(__name__)

APPS_JSON_PASS = os.environ['APPS_JSON_PASS']
APPS_JSON_URL = os.environ['APPS_JSON_URL']
APPS_EB_IDP_URL = os.environ['APPS_EB_IDP_URL']

handler = logging.StreamHandler()
app.logger.addHandler(handler)

@app.route("/")
def app_list():
    apps = []
    error = False

    try:
        apps = get_allowed_apps()
    except AppsException:
        app.logger.exception("Could not retrieve app list")
        error = True

    template = flask.request.args.get("template", "apps.html")

    return flask.render_template(template, apps=apps, error=error)

def get_allowed_apps():
    headers = { "Content-Type": "application/json" }
    r = requests.get(APPS_JSON_URL, auth=("metadata.client", APPS_JSON_PASS), headers=headers)

    if r.status_code != 200:
        raise AppsException("Got status code {} for {}".format(r.status_code, APPS_JSON_URL))

    allowed_apps = []
    my_entity = flask.request.environ.get("Shib-Authenticating-Authority")

    for e in r.json():
        if e.get("name:en") is None:
            continue
        if e["name:en"].startswith("myUnifiED"):
            continue

        login_url = APPS_EB_IDP_URL + "?sp-entity-id={}{}"
        app_url = e.get("coin:application_url")
        if app_url is None or app_url == "":
            e["loginUrl"] = login_url.format(e["entityid"], "")
        else:
            e["loginUrl"] = login_url.format(e["entityid"], "&RelayState="+app_url)

        if e.get("allowedall") == "yes":
            allowed_apps.append(e)
        elif e.get("allowedEntities") is not None:
            if my_entity in e["allowedEntities"]:
                allowed_apps.append(e)

    return allowed_apps

class AppsException(Exception):
    pass

if __name__ == "__main__":
    app.run(debug=True)
