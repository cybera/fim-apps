# README

## Setup
Choose ONE of the following methods

### Pipenv (recommended)
```bash
$ pipenv install
$ pipenv shell
```

### Pip (not recommended)
```bash
$ pip install -r requirements.txt
```


## Configuration
```bash
export APPS_MANAGE_USER=username123
export APPS_MANAGE_PASS=password123
export APPS_MANAGE_URL=https://manage.example.com
export APPS_PDP_PASS=password123
export APPS_PDP_URL=https://pdp.example.com/pdp/api/decide/policy
export APPS_EB_IDP_URL=https://engine.example.com/authentication/idp/unsolicited-single-sign-on
export APPS_HIDE_PREFIX=Pika
```

## Run
```bash
python main.py
```
