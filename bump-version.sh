#!/bin/bash

function usage () {
    echo "usage: bump-version <version-id>"
}

function commit_hint () {
    msg1="Now please commit with something like:"
    msg2="git commit -a -s -m \"Bumped version number to $1.\""
    echo $msg1 $msg2
}

function update_version_implib () {
    sed -e "s/^__version__ = .*$/__version__ = '$1'/g" \
        implib2/__version__.py > .__version__.new
}

function update_version_readme () {
    sed -e "/\*\*Stable Branch/s/(.*)\*\*/($1)**/g" \
        README.rst > .README.new
}

if [ $# -ne 1 ]; then
    usage
    exit 1
fi

if ! update_version_implib $1; then
    echo "Could not replace version in '__version__.py'!" >&2
    exit 2
else
    mv .__version__.new implib2/__version__.py
fi

if ! update_version_readme $1; then
    echo "Could not replace version in 'README.rst'!" >&2
    exit 2
else
    mv .README.new README.rst
fi

commit_hint $1
