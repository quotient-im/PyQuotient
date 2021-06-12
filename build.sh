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

if [[ $POETRY = true ]]; then
    SHIBOKEN_COMMAND = "poetry shell"
fi

shiboken6  $SHIBOKEN_INCLUDE_ARG \
    --project-file=pyside_typesystem/project.in \
    --typesystem-paths=$(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")/PySide6/typesystems/ \
    ./pyside_typesystem/bindings.h \
    ./pyside_typesystem/avatar.xml
