# bbscore

## Setup to Run

Create and activate a project-local virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.lock
```

## Update Requirements (for developers)

```sh
# Install the latest dependencies according to requirements.txt
python -m pip install -r requirements.txt
# Dump and save exact installed versions
python -m pip freeze > requirements.lock
```
