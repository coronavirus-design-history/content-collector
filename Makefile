setup:
	pip install -r requirements.txt

collect: setup
	python -m collector.collect run