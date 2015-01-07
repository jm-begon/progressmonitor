
all: clean in test

clean:
	python setup.py clean
	find . -name .DS_Store -delete
	rm -rf build

in: inplace

inplace:
	python setup.py build_ext --inplace

doc: inplace
	$(MAKE) -C doc html

clean-doc:
	rm -rf doc/_*

test:
	nosetests progressmonitor -sv --with-coverage

install:inplace
	python setup.py install