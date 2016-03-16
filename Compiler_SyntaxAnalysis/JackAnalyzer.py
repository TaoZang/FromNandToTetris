#!/usr/bin/env python3

__author__ = 'Tao Zang'

import sys
import os
from CompilationEngine import CompilationEngine

if __name__ == '__main__':
	arg = sys.argv[1];
	filename = os.path.basename(arg).split('.')[0];
	if os.path.isfile(arg):
		input = open(arg, 'r')
		output = open(arg.split('.')[0] + '.xml', 'w')
		engine = CompilationEngine(input.read(), output)
		output.close()
	else :
		files = [name for name in os.listdir(arg) if name.endswith('.jack')];
		for file in files:
			input = open(arg + '/' + file, 'r')
			output = open(arg + '/' + file.split('.')[0] + '.xml', 'w')
			engine = CompilationEngine(input.read(), output)
			output.close()