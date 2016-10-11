#!/bin/bash

function usage () {
    echo "usage: bump-version <version-id>"
}

function commit_hint () {
    msg1="Now please commit with something like:"
    msg2="git commit -a -s -m \"Bumped version number to $1.\""
    echo $msg1 $msg2
}

function update_version_init () {
    sed -e "s/^__version__ = .*$/__version__ = '$1'/g" \
        implib2/__init__.py > .__init__.new
}

function update_version_setup () {
    sed -e "s/version=.*$/version='$1',/g" \
        setup.py > .setup.new
}

function update_version_readme () {
    sed -e "/\*\*Stable Branch/s/(.*)\*\*/($1)**/g" \
        README.rst > .README.new
}

function update_version_sphinx () {
    sed -e "s/version = .*$/version = '$1'/g" \
        -e "s/release = .*$/release = '$1'/g" \
        docs/conf.py > .conf.new
}

if [ $# -ne 1 ]; then
    usage
    exit 1
fi

if ! update_version_init $1; then
    echo "Could not replace version in '__init__.py'!" >&2
    exit 2
else
    mv .__init__.new implib2/__init__.py
fi

if ! update_version_setup $1; then
    echo "Could not replace version in 'setup.py'!" >&2
    exit 2
else
    mv .setup.new setup.py
fi

if ! update_version_readme $1; then
    echo "Could not replace version in 'setup.py'!" >&2
    exit 2
else
    mv .README.new README.rst
fi

if ! update_version_sphinx $1; then
    echo "Could not replace version in 'docs/conf.py'!" >&2
    exit 2
else
    mv .conf.new docs/conf.py
fi

commit_hint $1
