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
    my_entity = flask.request.environ.get("Shib-Identity-Provider")

    for e in r.json():
        if e.get("name:en") is None:
            continue
        if e["name:en"].startswith("myUnifiED"):
            continue

        if e["allowedall"] == "yes":
            allowed_apps.append(e)
        elif e.get("allowedEntities") is not None:
            if my_entity in e["allowedEntities"]:
                allowed_apps.append(e)

    return allowed_apps

if __name__ == "__main__":
    app.run()
