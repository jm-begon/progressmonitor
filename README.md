Progress monitor
================
Progress monitor is a library for monitoring progress on time intensive tasks.

What, another progress bar toolbox ? Well, yes... and no! Progress monitor aims at giving flexible tools for monitoring progress with the least possible buiseness code invasion.

It features three main functionnlities:

  1. Monitoring progress with iterators/generators
  2. Monitoring functions
  3. Monitoring pieces of code

#### Monitoring iterators/generators can be as easy as: ####

	for x in monitor_with("my_gen_monitor")(xrange(length)):
		do_something(x)

with possible output:

	[>          ] 0.00%  
	[=>         ] 10.00% elapsed time: 1.14s remaining time (estimation): 9.42s 
	...
	[=====>     ] 50.00% elapsed time: 5.69s remaining time (estimation): 6.38s total time (estimation): 12.07s 
	...
	[==========>] 100.00% elapsed time: 10.53s  


Monitoring functions can be as easy as:

	@monitor_with("my_func_monitor")
	function(x):
		#do something
		
	function(x)

with possible output:

	Meta
	====
	Pid: 4663
	Thread: Thread 'MainThread' (id=140735151985408)
	Task name: Task # 0: do_task_monitoring

	Function
	========
	Name: <function do_task at 0x102487d70>
	Args: (<function _mult at 0x1023efa28>, 2, 4, -1)
	Kwargs: {}

	Result
	======
	_mult(2, 4, -1) = -8

	Exception
	=========
	None

	Time
	====
	Started: Fri Jan 16 13:55:46 2015
	Duration : 2.01 s

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