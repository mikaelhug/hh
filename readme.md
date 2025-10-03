Use pyenv to manage different python versions.
Install and enable in specific directory
```
sudo apt install pyenv
pyenv local 3.11.11
```

Install uv (venv alternative) and install ruff
```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.11.11 hh_env
source hh_env/bin/activate
uv pip install ruff
```

Run commands on the django docker container
```
docker exec hh_app python manage.py startapp main
docker exec hh_app python manage.py makemigrations main
docker exec hh_app python manage.py migrate
```