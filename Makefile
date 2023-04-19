lint:
	flake8

pyinstaller:
	cd specfiles && pyinstaller --noconfirm Mint.spec ../scripts/Mint.py

docs:
	mkdocs build && mkdocs gh-deploy

devel:
	python scripts/Mint.py --debug --no-browser --data-dir /data/MINT
