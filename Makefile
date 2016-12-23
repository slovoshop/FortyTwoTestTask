MANAGE=django-admin.py
SETTINGS=fortytwo_test_task.settings
TEST_FOLDER_HELLO=apps/hello/tests/

test: check_noqa
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(SETTINGS) $(MANAGE) test

localtest: check_noqa
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(SETTINGS) $(MANAGE) test
	flake8 --exclude '*migrations*,fortytwo_test_task/settings/__init__.py' \
		--max-complexity=6 apps fortytwo_test_task

check_noqa:
	bash check_noqa.sh

run:
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(SETTINGS) $(MANAGE) runserver

syncdb:
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(SETTINGS) $(MANAGE) syncdb --noinput

migrate:
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(SETTINGS) $(MANAGE) migrate

collectstatic:
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(SETTINGS) $(MANAGE) collectstatic --noinput
.PHONY: test syncdb migrate

req:
	@echo "Installing requirements"
	@pip install --exists-action=s -r requirements.txt

ftest:
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(SETTINGS) $ python \
	$(TEST_FOLDER_HELLO)functional_tests.py
