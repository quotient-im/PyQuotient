# PyQuotient

## Getting started

1. Use poetry to install dependencies(recommended):

   `poetry install`

   or use pip with qt repository `http://download.qt.io/official_releases/QtForPython/`(see dependencies and their versions in pyproject.toml) [More](https://doc.qt.io/qtforpython/shiboken6/gettingstarted.html): 
   
   `pip3 install --index-url=http://download.qt.io/official_releases/QtForPython/ --trusted-host download.qt.io shiboken6 PySide6 shiboken6-generator`

2. Clone libQuotient:

   `git clone https://github.com/quotient-im/libQuotient.git PyQuotient/libQuotient`

3. Run cmake project:

   `cmake -DBUILD_TESTING=OFF -DBUILD_WITH_QT6=ON .`
   `make`

Optional parameters:

- QT_PATH
- PYTHON_ENV_VERSION
- USE_POETRY

## Development

If you use pip, install development requirements:

`pip install pytest`

Run tests:

* If you use poetry: `poetry run python -m pytest`

* otherwise: `python -m pytest`
