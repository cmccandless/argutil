.PHONY: init lint test report clean clean-git package publish
init:
	pip install -r requirements.txt
	
lint:
	flake8

test:
	@mkdir ./tmp || rm -rf ./tmp/*
	coverage run -m pytest -v
	@rm -rf ./tmp

report: lint test
	@echo "coverage report"
	@coverage report || (echo "FAIL: Test coverage threshold is too low" && exit 2)

clean:
	rm -rf dist/*

clean-git:
	git stash

package: init clean-git report clean
	python setup.py sdist

publish: package
	twine upload dist/*
