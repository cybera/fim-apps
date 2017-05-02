#!/usr/bin/env python2

import flask
import requests
import os

app = flask.Flask(__name__)

@app.route("/")
def app_list():
    error = False
    try:
        apps = get_allowed_apps()
    except AppsException:
        apps = []
        error = True
    return flask.render_template("apps.html", apps=apps, error=error)

def get_allowed_apps():
    try:
        APPS_JSON_PASS = flask.request.environ['APPS_JSON_PASS']
        APPS_JSON_URL = flask.request.environ['APPS_JSON_URL']
        APPS_EB_IDP_URL = flask.request.environ['APPS_EB_IDP_URL']
    except KeyError as e:
        # TODO: Do proper logging
        print("Key error")
        return []

    headers = { "Content-Type": "application/json" }
    r = requests.get(APPS_JSON_URL, auth=("metadata.client", APPS_JSON_PASS), headers=headers)

    if r.status_code != 200:
        raise AppsException("Got non-200 status code")

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

        if e["allowedall"] == "yes":
            allowed_apps.append(e)
        elif e.get("allowedEntities") is not None:
            if my_entity in e["allowedEntities"]:
                allowed_apps.append(e)

    return allowed_apps

class AppsException(Exception):
    pass

if __name__ == "__main__":
    app.run()
