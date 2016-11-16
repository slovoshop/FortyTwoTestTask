#!/bin/bash
_filename=$(date +"%m_%d_%Y")

python manage.py print_objects_count 2>> ${_filename}.dat
