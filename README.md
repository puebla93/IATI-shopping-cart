# IATI shopping cart

Shopping Cart Backend Application.

## Preparation

1. Install docker.
   
2. Create a Python 3.10 virtualenv.
   
3. `pip install pip-tools`
   
4. `pip-sync requirements.txt requirements-dev.txt`.

## Dependency management

We use pip-tools for dependency management. [Docs](https://morioh.com/p/fb3fafb53095)

## Start the development server

To start the development server, use the command `runserver` in manage.py and go to [localhost:8000](http://localhost:8000/).

### Start the development server (docker version)

To start the development server, use the command `docker compose up`
and go to [localhost:8000](http://localhost:8000/).

## Tests

* Run `pytest` (this will run all tests). 

If you need more control: 
* Use `pytest -k test_fancy_func` to run all tests with the name `test_fancy_func`.
* Use `pytest -k TestClassName` to run all tests that are located inside `TestClassName` class.
* Use `pytest -q /path/to/test_foo.py` to run all tests inside the file `test_foo.py`.

## Coverage

* Run `pytest --cov=.` (this will run all tests and show coverage).

> See [pytest-cov’s documentation](https://pytest-cov.readthedocs.io/en/latest/)

## Debug the app

### VS Code

Add the following to the `configurations` array in `.vscode/launch.json`

```json
{
    "name": "IATI: Shopping Cart",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/manage.py",
    "args": [
        "runserver"
    ],
    "django": true,
    "justMyCode": true
}
```
> See [Python debugging in VS Code](https://code.visualstudio.com/docs/python/debugging)
