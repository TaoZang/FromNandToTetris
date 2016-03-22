#!/usr/bin/env python3

__author__ = 'Tao Zang'

import sys
import os
from CompilationEngine import CompilationEngine

if __name__ == '__main__':
	arg = sys.argv[1];
	filename = os.path.basename(arg).split('.')[0];
	if os.path.isfile(arg):
		output = arg.split('.')[0] + '.vm'
		engine = CompilationEngine(arg, output)
		engine.compileClass()
	else :
		files = [name for name in os.listdir(arg) if name.endswith('.jack')];
		for file in files:
			engine = CompilationEngine(arg + '/' + file, arg + '/' + file.split('.')[0] + '.vm')
			engine.compileClass()