init:
	pip install -r requirements.txt
	
lint:
	flake8

test:
	coverage run -m pytest -v

clean:
	rm -rf dist/*

clean-git:
	git stash

package: init clean-git lint test clean
	python setup.py sdist

publish: package
	twine upload dist/*
