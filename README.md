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
- GTAD_PATH
- MATRIX_DOC_PATH

**Note:**: deprecated API(properties, methods, etc) is not tested!

### Usage

After PyQuotient import use also `__feature__` import to be able to use API with snake case and true properties:

```python
from PyQuotient import Quotient
from __feature__ import snake_case, true_property

...

```

if you use PySide, `__feature__` import must be after both PyQuotient and PySide, order of imports is important.

## Development

If you use pip, install development requirements:

`pip install pytest`

Run tests:

- If you use poetry: `poetry run python -m pytest`

- otherwise: `python -m pytest`

Update resources in demo client: `poetry run pyside6-rcc demo/resources.qrc -o demo/resources.py`
