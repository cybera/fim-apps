import flask
import requests

app = flask.Flask(__name__)

@app.route("/")
def app_list():
    apps = get_allowed_apps()
    return flask.render_template("apps.html", apps=apps)

def get_allowed_apps():
    headers = { "Content-Type": "application/json" }
    r = requests.get("https://multidata.dev.myunified.ca/service-providers.json", auth=("metadata.client", ""), headers=headers)

    allowed_apps = []
    my_entity = flask.request.environ.get("Shib-Authenticating-Authority")

    for e in r.json():
        if e.get("name:en") is None:
            continue
        if e["name:en"].startswith("myUnifiED"):
            continue

        login_url = "https://engine.dev.myunified.ca/authentication/idp/unsolicited-single-sign-on?sp-entity-id={}{}"
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

if __name__ == "__main__":
    app.run()
