#!/usr/bin/env python3
__author__ = 'Tao Zang'

import sys
import re
import os

class CodeWriter(object):
	def __init__(self, path, name):
		self.output = open(path + '/' + name + '.asm', 'w');
		self.labels = {'eq': 0, 'gt': 0, 'lt': 0, 'ret_return': 0};
		self.symbols = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT', 'add': '+', 'sub': '-', 'and': '&', 'or': '|', 'neg': '-', 'not': '!'};
		self.snaps = {'PUSH_D': '@SP\nA=M\nM=D\n@SP\nM=M+1\n',
					  'POP_R13': '@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n'};
		self.writeInit();

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

	def writePushPop(self, command, segment, index, prefix):
		instruction = '';
		if (command == 'push'):
			if (segment == 'constant'):
				instruction = '@' + index + '\nD=A\n' + self.snaps['PUSH_D'];
			elif (segment == 'temp'):
				instruction = '@' + index + '\nD=A\n@R5\nA=D+A\nD=M\n' + self.snaps['PUSH_D'];
			elif (segment == 'pointer'):
				instruction = '@' + index + '\nD=A\n@R3\nA=D+A\nD=M\n' + self.snaps['PUSH_D'];
			elif (segment == 'static'):
				instruction = '@' + prefix + '.' + index + '\nD=M\n' + self.snaps['PUSH_D'];
			elif (segment == 'local' or segment == 'argument' or segment == 'this' or segment == 'that'):
				instruction = '@' + index + '\nD=A\n@' + self.symbols[segment] + '\nA=D+M\nD=M\n' + self.snaps['PUSH_D'];
		elif (command == 'pop'):
			if (segment == 'temp'):
				instruction = '@' + index + '\nD=A\n@R5\nD=D+A\n@R13\nM=D\n' + self.snaps['POP_R13'];
			elif (segment == 'pointer'):
				instruction = '@' + index + '\nD=A\n@R3\nD=D+A\n@R13\nM=D\n' + self.snaps['POP_R13'];
			elif (segment == 'static'):
				instruction = '@' + prefix + '.' + index + '\nD=A\n@R13\nM=D\n' + self.snaps['POP_R13'];
			elif (segment == 'local' or segment == 'argument' or segment == 'this' or segment == 'that'):
				instruction = '@' + index + '\nD=A\n@' + self.symbols[segment] +'\nD=D+M\n@R13\nM=D\n' + self.snaps['POP_R13'];
		self.output.write(instruction);

	def writeLabel(self, functionName, label):
		self.output.write('(' + functionName + '$' + label + ')\n');

	def writeIf(self, functionName, label):
		self.output.write('@SP\nAM=M-1\nD=M\n@' + functionName + '$' + label + '\nD;JNE\n');

	def writeGoto(self, functionName, label):
		self.output.write('@' + functionName + '$' + label + '\n0;JMP\n');

	def writeFunction(self, functionName, numlocals):
		self.output.write('(' + functionName + ')\n');
		n = 0;
		while(n < int(numlocals)):
			n += 1;
			self.writePushPop('push', 'constant', '0', '');

	def writeReturn(self):
		self.output.write('@LCL\nD=M\n@R13\nM=D\n'); #hold LCL value
		self.output.write('@5\nD=A\n@R13\nA=M-D\nD=M\n@R14\nM=D\n'); #hold return value
		self.output.write('@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n'); #*ARG = pop()
		self.output.write('D=A+1\n@SP\nM=D\n') #restore SP
		self.output.write('@R13\nAM=M-1\nD=M\n@THAT\nM=D\n'); #restore THAT
		self.output.write('@R13\nAM=M-1\nD=M\n@THIS\nM=D\n'); #restore THIS
		self.output.write('@R13\nAM=M-1\nD=M\n@ARG\nM=D\n'); #restore ARG
		self.output.write('@R13\nAM=M-1\nD=M\n@LCL\nM=D\n'); #restore LCL
		self.output.write('@R14\nA=M\n0;JMP\n'); #return

	def writeCall(self, functionName, args):
		retAddress = 'RET_ADDRESS_CALL' + str(self.labels['ret_return']);
		self.labels['ret_return'] += 1;
		self.output.write('@' + retAddress + '\nD=A\n' + self.snaps['PUSH_D']);
		self.output.write('@LCL\nD=M\n' + self.snaps['PUSH_D']);
		self.output.write('@ARG\nD=M\n' + self.snaps['PUSH_D']);
		self.output.write('@THIS\nD=M\n' + self.snaps['PUSH_D']);
		self.output.write('@THAT\nD=M\n' + self.snaps['PUSH_D']);
		self.output.write('@SP\nD=M\n@' + args + '\nD=D-A\n@5\nD=D-A\n@ARG\nM=D\n');
		self.output.write('@SP\nD=M\n@LCL\nM=D\n');
		self.output.write('@' + functionName + '\n0;JMP\n(' + retAddress + ')\n');

	def writeInit(self):
		self.output.write('@256\nD=A\n@SP\nM=D\n');
		self.writeCall('Sys.init', '0');

	def close(self):
		self.output.close();