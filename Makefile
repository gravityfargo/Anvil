install:
	pip install --editable .
run:
	anvil
clean:
	rm -rf build dist *.egg-info
	find . -name __pycache__ -exec rm -rf {} \;
