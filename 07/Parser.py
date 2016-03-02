#!/usr/bin/env python3
__author__ = 'Tao Zang'

import sys
import re
import os
from CodeWriter import CodeWriter

class Parser(object):
	def __init__(self, filename):
		self.instructions = [];
		with open(filename, 'r') as sources:
			for statement in sources.readlines():
				if(statement == '\n'):
					pass; #ignore blank line
				elif(statement.startswith('//')):
					pass; #ignore comment line
				else:
					instruction = statement.strip();
					match = re.match(r'([\w\s]*\w)\s*//.*', instruction);
					if match:
						instruction = match.groups()[0];
					self.instructions.append(instruction);
		self.index = 0;

	def hasMoreCommands(self):
		return self.index < len(self.instructions);

	def advance(self):
		self.index = self.index + 1;

	def commandType(self):
		match = re.match(r'(\w+).*', self.instructions[self.index]);
		return match.groups()[0];

	def arg1(self):
		match = re.match(r'\w+\s+(\w+).*', self.instructions[self.index]);
		return match.groups()[0];

	def arg2(self):
		match = re.match(r'\w+\s+\w+\s+(\w+)', self.instructions[self.index]);
		return match.groups()[0];

if __name__ == '__main__':
	path = os.path.dirname(sys.argv[1]);
	filename = os.path.basename(sys.argv[1]);
	parser = Parser(path + '/' + filename);
	writer = CodeWriter(path, filename.split('.')[0]);
	while parser.hasMoreCommands():
		command = parser.commandType();
		if(command == 'push' or command == 'pop'):
			writer.writePushPop(command, parser.arg1(), parser.arg2());
		else:
			writer.writeArithmetic(command);
		parser.advance();
	writer.close();