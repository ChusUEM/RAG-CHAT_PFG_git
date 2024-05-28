#!/usr/bin/env zsh

set -e #Para detener el script si algún comando devuelve un estado de salida != 0
set -x #Para imprimir cada comando antes de ejecutarlo

mypy "../src" #Comprobación de tipos para Python
flake8 "../src" --ignore=E501,W503,E203,E402 #Herramienta de linting, ignorando ciertos errores
black "../src" --check -l 80 #Herramienta de formateo de código, comprobando si cumplen el formato de black y longitud máxima 80 caracteres
