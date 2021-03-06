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
		match = re.match(r'([\w_-]+).*', self.instructions[self.index]);
		return match.groups()[0];

	def arg1(self):
		match = re.match(r'[\w_-]+\s+([\w_.-]+).*', self.instructions[self.index]);
		return match.groups()[0];

	def arg2(self):
		match = re.match(r'[\w_-]+\s+[\w_.-]+\s+([\w_-]+)', self.instructions[self.index]);
		return match.groups()[0];

	def parseFile(path, writer):
		parser = Parser(path);
		className = os.path.basename(path).split('.')[0];
		functionName = '';
		while parser.hasMoreCommands():
			command = parser.commandType();
			if(command == 'push' or command == 'pop'):
				writer.writePushPop(command, parser.arg1(), parser.arg2(), className);
			elif(command == 'label'):
				writer.writeLabel(functionName, parser.arg1());
			elif(command == 'if-goto'):
				writer.writeIf(functionName, parser.arg1());
			elif(command == 'goto'):
				writer.writeGoto(functionName, parser.arg1());
			elif(command == 'function'):
				functionName = parser.arg1();
				writer.writeFunction(functionName, parser.arg2());
			elif(command == 'return'):
				writer.writeReturn();
			elif(command == 'call'):
				writer.writeCall(parser.arg1(), parser.arg2());
			else:
				writer.writeArithmetic(command);
			parser.advance();	

if __name__ == '__main__':
	arg = sys.argv[1];
	filename = os.path.basename(arg).split('.')[0];
	if os.path.isfile(arg):
		writer = CodeWriter(os.path.dirname(arg), filename);
		Parser.parseFile(arg, writer);
	else :
		writer = CodeWriter(arg, filename);
		files = [name for name in os.listdir(arg) if name.endswith('.vm')];
		for file in files:
			Parser.parseFile(arg + '/' + file, writer);




