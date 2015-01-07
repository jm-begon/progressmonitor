# -*- coding: utf-8 -*-
import sys

if __name__ == '__main__':
	stream = sys.stdout

	stream.write("\r"+"a"*50+"\n")
	stream.write("\b"*4)
	stream.write("xxxx")
	stream.write("\n")
