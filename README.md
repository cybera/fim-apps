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
```

## Run
```bash
python main.py
```
