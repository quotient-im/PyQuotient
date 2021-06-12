#!/bin/bash

QT_PATH=""
POETRY=true

while getopts q:p: flag
do
    case "${flag}" in
        q) QT_PATH=${OPTARG};;
        p) POETRY=${OPTARG};;
    esac
done

SHIBOKEN_INCLUDE_ARG=""
if [[ ! -z "$QT_PATH" ]]; then
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$QT_PATH/lib"
    SHIBOKEN_INCLUDE_ARG="-I$QT_PATH/include/"
fi

SHIBOKEN_COMMAND="shiboken6"
PYTHON_COMMAND="python3"
if [[ $POETRY = true ]]; then
    SHIBOKEN_COMMAND="poetry run $SHIBOKEN_COMMAND"
    PYTHON_COMMAND="poetry run $PYTHON_COMMAND"
fi

echo $PWD $PYTHON_COMMAND
poetry show
TYPESYSTEM_PATH=$($PYTHON_COMMAND -c "import PySide6, os; print(os.path.dirname(PySide6.__file__))")/typesystems/
echo $TYPESYSTEM_PATH

$SHIBOKEN_COMMAND  $SHIBOKEN_INCLUDE_ARG \
    --project-file=pyside_typesystem/project.in \
    --typesystem-paths=$($PYTHON_COMMAND -c "import PySide6, os; print(os.path.dirname(PySide6.__file__))")/typesystems/ \
    ./pyside_typesystem/bindings.h \
    ./pyside_typesystem/avatar.xml
