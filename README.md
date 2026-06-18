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

## How to Run

```sh
python src/main.py top
python src/main.py text <gameid>
```

To process local sample HTML instead of fetching from the web:

```sh
python src/main.py text --src ref/2021040661_text.html
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
