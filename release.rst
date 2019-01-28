Flowbber Release
================

#. Edit version::

    nano .cookiecutter.json lib/flowbber/__init__.py

#. Update changelog in README.rst::

    git log > the.log
    nano README.rst

#. Commit, tag::

    git commit -a
        chg: dev: Bumping version number to x.y.z.
    git tag x.y.z

#. Build wheel package::

    tox -e build

#. Push new revision and tag::

    git push
    git push --tags

#. Upload to PyPI::

    twine upload --username kuralabs --sign --identity info@kuralabs.io  dist/flowbber-x.y.z-py3-none-any.whl
