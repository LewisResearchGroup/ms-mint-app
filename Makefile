lint:
	flake8

pyinstaller:
	cd specfiles && pyinstaller --onedir --noconfirm Mint__onedir__.spec --additional-hooks-dir=hooks

docs:
	mkdocs build && mkdocs gh-deploy

devel:
	python scripts/Mint.py --debug --no-browser --data-dir /data/MINT
