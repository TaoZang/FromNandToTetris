#!/usr/bin/env python3

import sys
import re

class CodeWriter(object):
	def __init__(self, filename):
		self.output = open(filename.split('.')[0] + '.asm', 'w');
		self.labels = {'eq': 0, 'gt': 0, 'lt': 0};

	def writeArithmetic(self, command):
		instruction = '';
		if (command == 'add'):
			instruction = '@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nMD=D+M\nD=A+1\n@SP\nM=D\n';
		elif (command == 'sub'):
			instruction = '@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nMD=M-D\nD=A+1\n@SP\nM=D\n';
		elif (command == 'and'):
			instruction = '@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nMD=D&M\nD=A+1\n@SP\nM=D\n';
		elif (command == 'or'):
			instruction = '@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nMD=D|M\nD=A+1\n@SP\nM=D\n';
		elif (command == 'neg'):
			instruction = '@SP\nA=M-1\nM=-M\n';
		elif (command == 'not'):
			instruction = '@SP\nA=M-1\nM=!M\n';
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
				instruction = '@' + index + '\nD=A\n@SP\nA=M\nM=D\nD=A+1\n@SP\nM=D\n';
		elif (command == 'pop'):
			pass;
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