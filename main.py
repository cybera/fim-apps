#!/usr/bin/env python2

import flask
import requests
import os

app = flask.Flask(__name__)

APPS_MULTIDATA_PASS = os.environ['APPS_MULTIDATA_PASS']
APPS_MULTIDATA_URL = os.environ['APPS_MULTIDATA_URL']
APPS_PDP_PASS = os.environ['APPS_PDP_PASS']
APPS_PDP_URL = os.environ['APPS_PDP_URL']
APPS_EB_IDP_URL = os.environ['APPS_EB_IDP_URL']

@app.route("/")
def app_list():
    template = flask.request.args.get("template", "apps.html")
    apps = get_allowed_apps()
    return flask.render_template(template, apps=apps)

def get_allowed_apps():
    headers = { "Content-Type": "application/json" }
    r = requests.get(APPS_MULTIDATA_URL, auth=("metadata.client", APPS_MULTIDATA_PASS), headers=headers)

    if r.status_code != 200:
        raise AppsException("Got status code {} for {}".format(r.status_code, APPS_MULTIDATA_URL))

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

        if e.get("logo:0:url", "https://.png") == "https://.png":
            e["logo:0:url"] = flask.url_for("static", filename="images/placeholder.png")

        if e.get("allowedall") == "yes":
            allowed_apps.append(e)
        elif e.get("allowedEntities") is not None:
            if my_entity in e["allowedEntities"]:
                allowed_apps.append(e)

    return allowed_apps

class AppsException(Exception):
    pass

@app.errorhandler(AppsException)
def handle_error(e):
    app.logger.error(e.message)
    return flask.render_template("error.html", message="Could not retrieve apps, please try again later.")

if __name__ == "__main__":
    app.run(debug=True)
