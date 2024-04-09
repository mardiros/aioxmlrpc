package := 'aioxmlrpc'
default_unittest_suite := 'tests/unittests'
default_functest_suite := 'tests/functionals'

install:
    poetry install

test test_suite=default_unittest_suite:
    poetry run pytest -sxv {{test_suite}}

lf:
    poetry run pytest -sxvvv --lf

cov test_suite=default_unittest_suite:
    rm -f .coverage
    rm -rf htmlcov
    poetry run pytest --cov-report=html --cov={{package}} {{test_suite}}
    xdg-open htmlcov/index.html

black:
    poetry run isort .
    poetry run black .

release major_minor_patch: test && changelog
    poetry version {{major_minor_patch}}
    poetry install

changelog:
    poetry run python scripts/write_changelog.py
    cat CHANGELOG.rst >> CHANGELOG.rst.new
    rm CHANGELOG.rst
    mv CHANGELOG.rst.new CHANGELOG.rst
    $EDITOR CHANGELOG.rst

publish:
    git commit -am "Release $(poetry version -s)"
    poetry build
    poetry publish
    git push
    git tag "$(poetry version -s)"
    git push origin "$(poetry version -s)"
