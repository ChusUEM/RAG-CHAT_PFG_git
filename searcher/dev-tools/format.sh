#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place "../src" #Eliminar todas las importaciones y variables no utilizadas
isort "../src" #Ordenar las importaciones en los archivos
black "../src" -l 80 #Formatear los archivos con una longitud máxima de línea de 80 caracteres.