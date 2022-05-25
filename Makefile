lint:
	flake8

test:
	pytest --cov=ms_mint --cov-report html
	rm images/coverage.svg
	coverage-badge -o images/coverage.svg

pyinstaller:
	cd specfiles && pyinstaller --onedir --noconfirm Mint__onedir__.spec --additional-hooks-dir=hooks

docs:
	mkdocs build && mkdocs gh-deploy

deploy:
    if [ (ls dist/* | wc -l) -ge 1 ]; then rm dist/* ; fi
	python setup.py sdist bdist_wheel
    python -m twine upload --repository ms-mint dist/ms*mint-*
