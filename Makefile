install:
	pip install --editable .
run:
	anvil gui
clean:
	rm -rf build dist *.egg-info