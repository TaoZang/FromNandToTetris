#!/usr/bin/env python3

'Parser module'

__author__ = 'Tao Zang'

import sys
import re
from enum import Enum

class Parser(object):
	
	def __init__(self, filename):
		self.codes = [];
		self.symbols = {};
		self.index = 0;
		self.pc = 16;
		self.symbols = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 'SCREEN': 16384, 'KBD': 24576, 
						'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15};
		self.dest = {'M':'001', 'D':'010', 'MD':'011', 'A':'100', 'AM':'101', 'AD':'110', 'AMD':'111'};
		self.jump = {'JGT':'001', 'JEQ':'010', 'JGE':'011', 'JLT':'100', 'JNE':'101', 'JLE':'110', 'JMP':'111'};
		self.comp = {'0':'101010', '1': '111111', '-1': '111010', 'D': '001100', 'A': '110000', '!D': '001101', '!A': '110001', '-D': '01111',
					 '-A': '110011', 'D+1': '011111', 'A+1': '110111', 'D-1': '001110', 'A-1': '110010', 'D+A': '000010', 'D-A': '010011',
					 'A-D': '000111', 'D&A': '000000', 'D|A': '010101'};

		with open(filename, 'r') as source:
			instrument = 0;
			for statement in source.readlines():
				if statement != '\n' and not(statement.startswith('//')):
					#trim blank and comment
					statement = statement.strip() + '\n';
					m = re.match(r'([\w@+-=;]*)\s*//.*', statement);
					if m:
						statement = m.groups()[0] + '\n';
					
					#parse symbol instrument
					m = re.match(r'\((.*)\)', statement);
					if m:
						variable = m.groups()[0];
						if not variable in self.symbols:
							self.symbols[variable] = instrument;
					else:
						self.codes.append(statement);
						instrument += 1;

	def hasMoreCommands(self):
		if self.index < len(self.codes):
			self.statement = self.codes[self.index];
			self.index += 1;
			return True;
		else:
			return False;

	def parse(self):
		if self.statement.startswith('@'):
			m = re.match(r'@(\d\d*)', self.statement);
			if m:
				pc = int(m.groups()[0]);
				return '0{0:015b}\n'.format(pc);
			else:
				m = re.match(r'@(.*)', self.statement);
				variable = m.groups()[0];
				pc = self.symbols.get(variable, -1);
				if pc == -1:
					self.symbols[variable] = self.pc;
					pc = self.pc;
					self.pc += 1;
				return '0{0:015b}\n'.format(pc);
		else:
			comp = self.statement;
			dest = '000';
			jump = '000';
			if comp.find('=') != -1:
				symbols = comp.split('=');
				dest = self.parseDest(symbols[0]);
				comp = symbols[1];

			if comp.find(';') != -1:
				symbols = comp.split(';');
				jump = self.parseJump(symbols[1]);
				comp = symbols[0];

			return '111' + self.parseComp(comp) + dest + jump + '\n';	

	def parseDest(self, dest):
		return self.dest[dest.strip()];

	def parseJump(self, jump):
		return self.jump[jump.strip()];

	def parseComp(self, comp):
		if comp.find('M') != -1:
			comp = comp.replace('M', 'A');
			return '1' + self.comp[comp.strip()];
		else:
			return '0' + self.comp[comp.strip()];


if __name__ == '__main__':
	filename = sys.argv[1];
	parser = Parser(filename);
	output = open(filename.split('.')[0] + '.hack', 'w');
	while(parser.hasMoreCommands()):
		statement = parser.parse();
		output.write(statement);
	output.close();
		