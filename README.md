# README

## Setup
```bash
pip install -r requirements.txt
```

## Configuration
```bash
export APPS_MULTIDATA_PASS=password123
export APPS_MULTIDATA_URL=https://multidata.example.com/service-providers.json
export APPS_PDP_PASS=password123
export APPS_PDP_URL=https://pdp.example.com/pdp/api/decide/policy
export APPS_EB_IDP_URL=https://engine.example.com/authentication/idp/unsolicited-single-sign-on
export APPS_GROUP_ADMIN=urn:collab:group:example.com:apps_admin
export APPS_VOOT_SERVICEURL=https://voot.example.com
export APPS_VOOT_ACCESSTOKENURI=https://authz.vm.openconext.org/oauth/token
export APPS_VOOT_CLIENTID=apps
export APPS_VOOT_CLIENTSECRET=super_secure_secret
export APPS_DB_HOST=db.example.com
export APPS_DB_PORT=3306
export APPS_DB_USER=apps
export APPS_DB_PASS=apps_passwd
```

## Run
```bash
python main.py
```
