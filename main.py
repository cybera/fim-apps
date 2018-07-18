#!/usr/bin/env python2

import flask
import requests
import os
import json
from urlparse import urlparse

app = flask.Flask(__name__)

APPS_MANAGE_URL = os.environ['APPS_MANAGE_URL']
APPS_MANAGE_USER = os.environ['APPS_MANAGE_USER']
APPS_MANAGE_PASS = os.environ['APPS_MANAGE_PASS']
APPS_PDP_PASS = os.environ['APPS_PDP_PASS']
APPS_PDP_URL = os.environ['APPS_PDP_URL']
APPS_EB_IDP_URL = os.environ['APPS_EB_IDP_URL']
APPS_HIDE_PREFIX = os.environ['APPS_HIDE_PREFIX']

@app.route("/")
def app_list():
    template = flask.request.args.get("template", "apps.html")
    apps = get_allowed_apps()
    display_name = flask.request.environ.get("displayName", "")
    return flask.render_template(template, display_name=display_name, apps=apps)

def get_allowed_apps():
    metadata = get_metadata()

    allowed_apps = []
    idp = flask.request.environ.get("Shib-Authenticating-Authority")

    for e in metadata:
        sp_data = {}
        metadata_fields = e["data"].get("metaDataFields")

        sp_entityid = e["data"].get("entityid")
        sp_name = metadata_fields.get("name:en")
        sp_app_url = metadata_fields.get("coin:application_url")
        sp_logo_url = metadata_fields.get("logo:0:url", "https://.png")
        sp_logo_width = metadata_fields.get("logo:0:width", "50")
        sp_logo_height = metadata_fields.get("logo:0:height", "50")
        sp_allowed_entities = e["data"].get("allowedEntities")
        sp_login_url_template = APPS_EB_IDP_URL + "?sp-entity-id={}{}"
        sp_allowed_all = bool(e["data"].get("allowedall"))
        sp_supports_idp_init = int(metadata_fields.get("coin:supports_idp_init_login", 0))
        sp_policy_decision_required = int(metadata_fields.get("coin:policy_enforcement_decision_required", 0))

        assert sp_entityid is not None
        assert metadata_fields is not None
        assert sp_supports_idp_init in [0,1]
        assert sp_policy_decision_required in [0,1]

        # Hide app if no name or starts with prefix
        if sp_name is None:
            app.logger.error("SP {} has no name set".format(sp_entityid))
            continue
        elif sp_name.startswith(APPS_HIDE_PREFIX):
            app.logger.info("SP {} being skipped because it starts with {}".format(sp_entityid, APPS_HIDE_PREFIX))
            continue

        # Don't show app if user not authorized to use it
        if sp_policy_decision_required:
            if not is_user_authorized(sp_entityid):
                app.logger.info("Skipping SP {} due to no access".format(sp_entityid))
                continue

        if sp_supports_idp_init:
            app.logger.info("SP {} supports IDP initiated login".format(sp_entityid))
            # IDP initiated login supported

            if sp_app_url:
                u_template = sp_login_url_template.format(sp_entityid, "&RelayState="+sp_app_url)
            else:
                u_template = sp_login_url_template.format(sp_entityid, "")

            sp_login_url = urlparse(u_template)

        else:
            app.logger.info("SP {} doesn't support IDP initiated login".format(sp_entityid))

            if sp_app_url:
                try:
                  sp_login_url = urlparse(sp_app_url)
                except Exception as e:
                    app.logger.exception(e)
                    continue
            else:
                # Drop entity from showing up as there's no login URL
                app.logger.error("Dropping SP {} due to no application URL".format(sp_entityid))
                continue

        if sp_logo_url == "https://.png":
            sp_logo_url = flask.url_for("static", filename="images/placeholder.png")

        sp_data["name:en"] = sp_name
        sp_data["loginUrl"] = sp_login_url.geturl()
        sp_data["logo:0:url"] = sp_logo_url
        sp_data["logo:0:width"] = sp_logo_width
        sp_data["logo:0:height"] = sp_logo_height

        if sp_allowed_all:
            allowed_apps.append(sp_data)
        elif sp_allowed_entities is not None:
            if idp in sp_allowed_entities:
                allowed_apps.append(sp_data)
            else:
                app.logger.info("SP {} not in sp_allowed_entities: {}".format(sp_entityid, sp_allowed_entities))

    return allowed_apps

def get_metadata():
    headers = { "Content-Type": "application/json" }
    post_data = '{"ALL_ATTRIBUTES":true}'

    r = requests.post(APPS_MANAGE_URL + '/manage/api/internal/search/saml20_sp', auth=(APPS_MANAGE_USER, APPS_MANAGE_PASS), headers=headers, data=post_data)

    if r.status_code != 200:
        raise AppsException("Unexpected status code {} for {}".format(r.status_code, APPS_MULTIDATA_URL))

    return r.json()

def is_user_authorized(service_provider):
    headers = { "Content-Type": "application/json" }
    idp = flask.request.environ.get("Shib-Authenticating-Authority")
    name_id = flask.request.environ.get("name-id")

    assert idp is not None
    assert name_id is not None
    assert service_provider is not None

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
        app.logger.error("Unexpected status code {} for {}".format(r.status_code, APPS_PDP_URL))
        return False

    try:
        return r.json()['Response'][0]['Decision'] != "Deny"
    except (KeyError, TypeError, IndexError):
        app.logger.error("Unexpected response body for {}: {}".format(APPS_PDP_URL, r.json()))

    return False

class AppsException(Exception):
    pass

@app.errorhandler(AppsException)
def handle_error(e):
    app.logger.error(e.message)
    return flask.render_template("error.html", message="Could not retrieve apps, please try again later.")

if __name__ == "__main__":
    app.run(debug=True)
