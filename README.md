Progress monitor
================
Progress monitor is a library for monitoring progress on time intensive tasks.

What, another progress bar toolbox ? Well, yes... and no! Progress monitor aims at giving flexible tools for monitoring progress with the least possible buiseness code invasion.

It features three main functionnlities:

	1. Monitoring progress with iterators/generators
	2. Monitoring functions
	3. Monitoring pieces of code

Monitoring iterators/generators can be as easy as:

	for x in monitor_with("my_gen_monitor")(xrange(length)):
		do_something(x)

Monitoring functions can be as easy as:

	@monitor_with("my_func_monitor")
	function(x):
		#do something
		
	function(x)

Monitoring code can be as easy as:

	with monitor_with("my_code_monitor"):
		do_something()

In those examples, data and their destinations are supposed to be specified beforehand in a logger-like fashion (this is usually what you would like). However, it is possible, to do all the configuration in the business code.

See the examples for more illustrations.


Getting the latest code
-----------------------

To get the latest code using git, simply type:


    git clone https://github.com/jm-begon/progressmonitor.git

If you don't have git installed, you can download a zip or tarball of the
latest code: https://github.com/jm-begon/progressmonitor/archive/master.zip



Installing
----------

As with any Python packages, simply do:

    python setup.py install

in the source code directory.


Running the test suite
----------------------

To run the test suite, you need nosetests and the coverage modules.
Run the test suite using::

    nosetests

from the root of the project.


How to contribute?
------------------

To contribute, fork the library, make your improvement and send back a pull request.