# bbscore

## Setup to Run

Create and activate a project-local virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

```sh
python -m pip install -r requirements.lock
```

## Update Requirements (for developers)

```sh
./update.sh
```

It runs:

```sh
pip install -r requirements.txt
pip freeze > requirements.lock
```
