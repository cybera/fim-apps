#!/usr/bin/env python2

import flask
import requests
import os
import json

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
    metadata = get_metadata()

    allowed_apps = []
    idp = flask.request.environ.get("Shib-Authenticating-Authority")

    for e in metadata:
        sp = e["entityid"]

        if e.get("name:en") is None:
            continue
        if e["name:en"].startswith("myUnifiED"):
            continue
        if e.get("coin:policy_enforcement_decision_required", 0) == 1:
            if not is_user_authorized(sp):
                continue

        login_url = APPS_EB_IDP_URL + "?sp-entity-id={}{}"
        app_url = e.get("coin:application_url")
        if app_url is None or app_url == "":
            e["loginUrl"] = login_url.format(sp, "")
        else:
            e["loginUrl"] = login_url.format(sp, "&RelayState="+app_url)

        if e.get("logo:0:url", "https://.png") == "https://.png":
            e["logo:0:url"] = flask.url_for("static", filename="images/placeholder.png")

        if e.get("allowedall") == "yes":
            allowed_apps.append(e)
        elif e.get("allowedEntities") is not None:
            if idp in e["allowedEntities"]:
                allowed_apps.append(e)

    return allowed_apps

def get_metadata():
    headers = { "Content-Type": "application/json" }
    r = requests.get(APPS_MULTIDATA_URL, auth=("metadata.client", APPS_MULTIDATA_PASS), headers=headers)

    if r.status_code != 200:
        raise AppsException("Got status code {} for {}".format(r.status_code, APPS_MULTIDATA_URL))

    return r.json()

def is_user_authorized(service_provider=None):
    headers = { "Content-Type": "application/json" }
    idp = flask.request.environ.get("Shib-Authenticating-Authority")
    name_id = flask.request.environ.get("name-id")

    pdp_policy = {
        "Request": {
            "ReturnPolicyIdList": False,
            "CombinedDecision": False,
            "AccessSubject": {
                "Attribute": [{
                        "AttributeId": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
                        "Value": name_id
                }]
            },
            "Resource": {
                "Attribute": [
                    {
                        "AttributeId": "SPentityID",
                        "Value": service_provider
                    },
                    {
                        "AttributeId": "IDPentityID",
                        "Value": idp
                    }
                ]
            }
        }
    }

    r = requests.post(APPS_PDP_URL, auth=("pdp_admin", APPS_PDP_PASS), headers=headers, data=json.dumps(pdp_policy))

    if r.status_code != 200:
        app.logger.error("Got status code {} for {}".format(r.status_code, APPS_PDP_URL))
        return False

    return r.json()['Response'][0]['Decision'] != "Deny"


class AppsException(Exception):
    pass

@app.errorhandler(AppsException)
def handle_error(e):
    app.logger.error(e.message)
    return flask.render_template("error.html", message="Could not retrieve apps, please try again later.")

if __name__ == "__main__":
    app.run(debug=True)
