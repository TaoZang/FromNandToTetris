import re
from collections import namedtuple

WS = r'(?P<ws>\s+)'
COMMENT = r'(?P<comment>//.*\n|/\*.*\*/|/\*\*(.|\n)*?\*/)'
IDENTIFIER = r'(?P<identifier>[a-zA-Z_][\w\d]*)'
SYMBOL = r'(?P<symbol>[\(\)\[\]\{\}\,\.\+\-\*\|\<\>;=/&~])'
CONSTANT_INT = r'(?P<integerConstant>\d+)'
CONSTANT_STR = r'(?P<stringConstant>".*")'

KEYWORDS = ['class', 'constructor', 'method', 'function', 'int', 'boolean', 'char', 'void', 'var', 'static', 
		   'field', 'let', 'do', 'if', 'else', 'while', 'return', 'true', 'false', 'null', 'this']

Token = namedtuple('Token', ['type', 'value'])
def generate_tokens(pattern, text):
	scanner = pattern.scanner(text)
	for m in iter(scanner.match, None):
		yield Token(m.lastgroup, m.group())

class JackTokenizer(object):
	def __init__(self, src):
		self.token = None
		self.tokens = []
		pattern = re.compile('|'.join([COMMENT, IDENTIFIER, SYMBOL, CONSTANT_INT, CONSTANT_STR, WS]))

		with open(src, 'r') as file:
			for token in generate_tokens(pattern, file.read()):
				if token.type != 'comment' and token.type != 'ws':
					self.tokens.append(token)

	def hasMoreToken(self):
		return len(self.tokens) > 0

	def advance(self):
		self.token = self.tokens.pop(0)

	def next(self):
		token = self.tokens[0]
		return (token.type, token.value)

	def tokenType(self):
		if self.token.type == 'identifier' and self.token.value in KEYWORDS:
			return 'keyword'
		else:
			return self.token.type

	def tokenValue(self):
		return self.token.value.strip('"')