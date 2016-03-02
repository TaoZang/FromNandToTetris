#!/usr/bin/env python3
__author__ = 'Tao Zang'

import sys
import re
import os

class CodeWriter(object):
	def __init__(self, path, name):
		self.prefix = name;
		self.output = open(path + '/' + name + '.asm', 'w');
		self.labels = {'eq': 0, 'gt': 0, 'lt': 0};
		self.symbols = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT', 'add': '+', 'sub': '-', 'and': '&', 'or': '|', 'neg': '-', 'not': '!'};
		self.snaps = {'PUSH_D': '@SP\nA=M\nM=D\n@SP\nM=M+1\n',
					  'POP_R13': '@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n'};

	def writeArithmetic(self, command):
		instruction = '';
		if (command == 'add' or command == 'and' or command == 'or'):
			instruction = '@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nMD=D' + self.symbols[command] + 'M\nD=A+1\n@SP\nM=D\n';
		elif (command == 'sub'):
			instruction = '@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nMD=M-D\nD=A+1\n@SP\nM=D\n';
		elif (command == 'neg' or command == 'not'):
			instruction = '@SP\nA=M-1\nM=' + self.symbols[command] + 'M\n';
		else:
			index = str(self.labels[command]);
			if (command == 'eq'):
				instruction = '@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n@EQ' + index + '\nD;JEQ\n@SP\nA=M\nM=0\n@EQ' + index + '_END\n0;JMP\n(EQ' + index + ')\n@SP\nA=M\nM=-1\n(EQ' + index + '_END)\n@SP\nM=M+1\n';
			elif (command == 'gt'):
				instruction = '@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n@GT' + index + '\nD;JGT\n@SP\nA=M\nM=0\n@GT' + index + '_END\n0;JMP\n(GT' + index + ')\n@SP\nA=M\nM=-1\n(GT' + index + '_END)\n@SP\nM=M+1\n';
			elif (command == 'lt'):
				instruction = '@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n@LT' + index + '\nD;JLT\n@SP\nA=M\nM=0\n@LT' + index + '_END\n0;JMP\n(LT' + index + ')\n@SP\nA=M\nM=-1\n(LT' + index + '_END)\n@SP\nM=M+1\n';
			self.labels[command] += 1;

		self.output.write(instruction);

	def writePushPop(self, command, segment, index):
		instruction = '';
		if (command == 'push'):
			if (segment == 'constant'):
				instruction = '@' + index + '\nD=A\n' + self.snaps['PUSH_D'];
			elif (segment == 'temp'):
				instruction = '@' + index + '\nD=A\n@R5\nA=D+A\nD=M\n' + self.snaps['PUSH_D'];
			elif (segment == 'pointer'):
				instruction = '@' + index + '\nD=A\n@R3\nA=D+A\nD=M\n' + self.snaps['PUSH_D'];
			elif (segment == 'static'):
				instruction = '@' + self.prefix + '.' + index + '\nD=M\n' + self.snaps['PUSH_D'];
			elif (segment == 'local' or segment == 'argument' or segment == 'this' or segment == 'that'):
				instruction = '@' + index + '\nD=A\n@' + self.symbols[segment] + '\nA=D+M\nD=M\n' + self.snaps['PUSH_D'];
		elif (command == 'pop'):
			if (segment == 'temp'):
				instruction = '@' + index + '\nD=A\n@R5\nD=D+A\n@R13\nM=D\n' + self.snaps['POP_R13'];
			elif (segment == 'pointer'):
				instruction = '@' + index + '\nD=A\n@R3\nD=D+A\n@R13\nM=D\n' + self.snaps['POP_R13'];
			elif (segment == 'static'):
				instruction = '@' + self.prefix + '.' + index + '\nD=A\n@R13\nM=D\n' + self.snaps['POP_R13'];
			elif (segment == 'local' or segment == 'argument' or segment == 'this' or segment == 'that'):
				instruction = '@' + index + '\nD=A\n@' + self.symbols[segment] +'\nD=D+M\n@R13\nM=D\n' + self.snaps['POP_R13'];

		self.output.write(instruction);

	def writeInit(self):
		pass;

	def writeLabel(self, label):
		pass;

	def writeGoto(self, label):
		pass;

	def writeIf(self, label):
		pass;

	def writeCall(self, function, args):
		pass;

	def writeReturn(self):
		pass;

	def writeFunction(self, function, locals):
		pass;

	def close(self):
		self.output.close();