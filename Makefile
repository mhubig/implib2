##############################################################################
#
#  Simple Makefile based wrapper for tox.
#    written by Markus Hubig <mhubig@gmail.com>
#
##############################################################################

TOX = tox
TOX_WORKDIR_FLAG = --workdir
TOX_PYTEST_FLAGS = -e py27
TOX_FLAKE8_FLAGS = -e flake8
TOX_SPHINX_FLACS = -e docs

TEMPDIR := $(shell mktemp -d -u)
MKDIR_P  = mkdir -p

TRASH_FILES  = .coverage coverage.xml unittests.xml
TRASH_FILES += *.pyc */*.pyc
TRASH_DIRS   = .tox/ .cache/ build/ dist/ docs/_build/
TRASH_DIRS  += .eggs/ IMPLib2.egg-info/ */__pycache__

.PHONY: pytest flake8 docs clean help

all:
	$(MKDIR_P) $(TEMPDIR)
	$(TOX) $(TOX_WORKDIR_FLAG) $(TEMPDIR)
	$(RM) -rf $(TEMPDIR)

pytest:
	$(MKDIR_P) $(TEMPDIR)
	$(TOX) $(TOX_WORKDIR_FLAG) $(TEMPDIR) $(TOX_PYTEST_FLAGS)
	$(RM) -rf $(TEMPDIR)

flake8:
	$(MKDIR_P) $(TEMPDIR)
	$(TOX) $(TOX_WORKDIR_FLAG) $(TEMPDIR) $(TOX_FLAKE8_FLAGS)
	$(MKDIR_P) $(TEMPDIR)

docs:
	$(MKDIR_P) $(TEMPDIR)
	$(TOX) $(TOX_WORKDIR_FLAG) $(TEMPDIR) $(TOX_SPHINX_FLACS)
	$(MKDIR_P) $(TEMPDIR)

release:
ifndef VERSION
	$(error VERSION is not set)
endif
	git flow release start $(VERSION)
	./bump-version.sh $(VERSION)
	git commit -a -s -m \"Bumped version number to $(VERSION).\"

clean:
	$(RM) -r $(TRASH_FILES) $(TRASH_DIRS) $(TEMPDIR)

help:
	@echo
	@echo "  make [target] [OPTIONS]"
	@echo
	@echo " Targets:"
	@echo "     all             Run all the tests (default)."
	@echo "     clean           Clean all the files and folders."
	@echo "     pytest          Run all the tests with pytest."
	@echo "     flake8          Run the flake8 checks."
	@echo "     sphinx          Only build the docs with sphinx."
	@echo "     release         start a new release (use option VERSION=0.0.0)."
	@echo "     help            Prints this message."
	@echo
	@echo " Options:"
	@echo "     VERSION=0.0.0   Set the version number for new release."
	@echo
