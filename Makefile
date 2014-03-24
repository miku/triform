clean:
	find . -name "*.pyc" -exec rm -rf {} \;
	rm -rf build/ dist/ triform.egg-info/

coverage:
	nosetests --with-coverage --cover-package=triform