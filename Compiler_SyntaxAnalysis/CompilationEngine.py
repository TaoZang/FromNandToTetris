import re
from JackTokenizer import JackTokenizer

TYPE = ['int', 'char', 'boolean', 'identifier']
STATEMENT = ['let', 'do', 'while', 'if', 'return']
TERM = ['identifier', 'integerConstant', 'stringConstant', 'keyword', '(', '-', '~']
OP = ['+', '-', '*', '/', '&', '|', '>', '<', '=']

class CompilationEngine(object):
	def __init__(self, text, output):
		self.tokenizer = JackTokenizer(text)
		output.write(self.compileClass())

	def _acceptNextToken(self, token):
		if self.tokenizer.hasMoreToken():
			self.tokenizer.advance()
			typ = self.tokenizer.tokenType()
			tok = self.tokenizer.tokenValue()
			if type(token) != list:
				token = [token]
			if typ in token or tok in token:
				if tok == '<':
					tok = '&lt;'
				elif tok == '>':
					tok = '&gt;'
				elif tok == '&':
					tok = '&amp;'
				return '<' + typ + '>' + tok + '</' + typ + '>\n'
		raise SyntaxError('Parse Error')

	def _tryNextToken(self, token):
		if self.tokenizer.hasMoreToken():
			typ, tok = self.tokenizer.next()
			if type(token) != list:
				token = [token]
			if typ in token or tok in token:
				return True
		return False

	def compileClass(self):
		#'class' className '{' classVarDec* subroutineDec* '}'
		compileval = '<class>\n'
		compileval += self._acceptNextToken('class')
		compileval += self._acceptNextToken('identifier')
		compileval += self._acceptNextToken('{')

		while self._tryNextToken(['static', 'field']):
			compileval += self.compileClassVarDec()
		while self._tryNextToken(['constructor', 'function', 'method']):
			compileval += self.compileSubroutine()

		compileval += self._acceptNextToken('}')	
		return compileval + '</class>\n'

	def compileClassVarDec(self):
		#('static'|'field') type varName (','varName)* ';'
		compileval = '<classVarDec>\n'
		compileval += self._acceptNextToken(['static', 'field'])
		compileval += self._acceptNextToken(['int', 'char', 'boolean', 'identifier'])
		compileval += self._acceptNextToken('identifier')

		while self._tryNextToken(','):
			compileval += self._acceptNextToken(',')
			compileval += self._acceptNextToken('identifier')

		compileval += self._acceptNextToken(';')
		return compileval + '</classVarDec>\n'

	def compileSubroutine(self):
		#('constructor'|'function'|'method')
		#('void'|type)subroutineName'('parameterList')'
		#subroutineBody
		compileval = '<subroutineDec>\n'
		compileval += self._acceptNextToken(['constructor', 'function', 'method'])
		compileval += self._acceptNextToken(['void', 'int', 'char', 'boolean', 'identifier'])
		compileval += self._acceptNextToken('identifier')
		compileval += self._acceptNextToken('(')
		compileval += self.compileParameterList()
		compileval += self._acceptNextToken(')')

		compileval += '<subroutineBody>\n'
		compileval += self._acceptNextToken('{')
		while self._tryNextToken('var'):
			compileval += self.compileVarDec()
		while self._tryNextToken(STATEMENT):
			compileval += self.compileStatements()
		compileval += self._acceptNextToken('}')
		compileval += '</subroutineBody>\n'
	
		return compileval + '</subroutineDec>\n'

	def compileParameterList(self):
		#((type varName)(','type varName)*)?
		compileval = '<parameterList>\n'

		if self._tryNextToken(TYPE):
			compileval += self._acceptNextToken(TYPE)
			compileval += self._acceptNextToken('identifier')
			while self._tryNextToken(','):
				compileval += self._acceptNextToken(',')
				compileval += self._acceptNextToken(TYPE)
				compileval += self._acceptNextToken('identifier')
		
		return compileval + '</parameterList>\n'

	def compileVarDec(self):
		#'var' type varName (',' varName)*';'
		compileval = '<varDec>\n'
		compileval += self._acceptNextToken('var')
		compileval += self._acceptNextToken(TYPE)
		compileval += self._acceptNextToken('identifier')

		while self._tryNextToken(','):
			compileval += self._acceptNextToken(',')
			compileval += self._acceptNextToken('identifier')
		compileval += self._acceptNextToken(';')

		return compileval + '</varDec>\n'

	def compileStatements(self):
		#statement*
		#letStatement|ifStatement|whileStatement|doStatement|returnStatement
		compileval = '<statements>\n'

		while self._tryNextToken(STATEMENT):
			if self._tryNextToken('let'):
				compileval += self.compileLet()
			elif self._tryNextToken('if'):
				compileval += self.compileIf()
			elif self._tryNextToken('while'):
				compileval += self.compileWhile()
			elif self._tryNextToken('do'):
				compileval += self.compileDo()
			elif self._tryNextToken('return'):
				compileval += self.compileReturn()

		return compileval + '</statements>\n'

	def compileDo(self):
		#'do' subroutineCall ';'
		#subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
		compileval = '<doStatement>\n'

		compileval += self._acceptNextToken('do')
		compileval += self._acceptNextToken('identifier')
		if self._tryNextToken('.'):
			compileval += self._acceptNextToken('.')
			compileval += self._acceptNextToken('identifier')
		
		compileval += self._acceptNextToken('(')
		compileval += self.compileExpressionList()
		compileval += self._acceptNextToken(')')

		compileval += self._acceptNextToken(';')

		return compileval + '</doStatement>\n'

	def compileLet(self):
		#'let' varName ('[' expression ']')? '=' expression ';'
		compileval = '<letStatement>\n'

		compileval += self._acceptNextToken('let')
		compileval += self._acceptNextToken('identifier')
		if self._tryNextToken('['):
			compileval += self._acceptNextToken('[')
			compileval += self.compileExpression()
			compileval += self._acceptNextToken(']')
		compileval += self._acceptNextToken('=')
		compileval += self.compileExpression()
		compileval += self._acceptNextToken(';')

		return compileval + '</letStatement>\n'

	def compileWhile(self):
		#'while' '(' expression ')''{' statements '}'
		compileval = '<whileStatement>\n'

		compileval += self._acceptNextToken('while')
		compileval += self._acceptNextToken('(')
		compileval += self.compileExpression()
		compileval += self._acceptNextToken(')')
		compileval += self._acceptNextToken('{')
		compileval += self.compileStatements()
		compileval += self._acceptNextToken('}')

		return compileval + '</whileStatement>\n'

	def compileReturn(self):
		#'return' expression? ';'
		compileval = '<returnStatement>\n'

		compileval += self._acceptNextToken('return')
		if not self._tryNextToken(';'):
			compileval += self.compileExpression()
		compileval += self._acceptNextToken(';')

		return compileval + '</returnStatement>\n'

	def compileIf(self):
		#'if' '(' expression ')' '{' statements '}'
		#('else' '{' statements '}')?
		compileval = '<ifStatement>\n'

		compileval += self._acceptNextToken('if')
		compileval += self._acceptNextToken('(')
		compileval += self.compileExpression()
		compileval += self._acceptNextToken(')')
		compileval += self._acceptNextToken('{')
		compileval += self.compileStatements()
		compileval += self._acceptNextToken('}')

		if self._tryNextToken('else'):
			compileval += self._acceptNextToken('else')
			compileval += self._acceptNextToken('{')
			compileval += self.compileStatements()
			compileval += self._acceptNextToken('}')

		return compileval + '</ifStatement>\n'

	def compileExpression(self):
		#term(op term)*
		compileval = '<expression>\n'

		compileval += self.compileTerm()
		while self._tryNextToken(OP):
			compileval += self._acceptNextToken(OP)
			compileval += self.compileTerm()

		return compileval + '</expression>\n'

	def compileTerm(self):
		#integerConstant|stringConstant|keywordConstant|varName|varName'['expression']'|subroutineCall|'('expression')'|unaryOp term
		compileval = '<term>\n'

		if self._tryNextToken('('):
			compileval += self._acceptNextToken('(')
			compileval += self.compileExpression()
			compileval += self._acceptNextToken(')')
		elif self._tryNextToken(['-', '~']):
			compileval += self._acceptNextToken(['-', '~'])
			compileval += self.compileTerm()
		else:
			compileval += self._acceptNextToken(TERM)
			if self._tryNextToken('['):
				compileval += self._acceptNextToken('[')
				compileval += self.compileExpression()
				compileval += self._acceptNextToken(']')
			elif self._tryNextToken('('):
				compileval += self._acceptNextToken('(')
				compileval += self.compileExpressionList()
				compileval += self._acceptNextToken(')')
			elif self._tryNextToken('.'):
				compileval += self._acceptNextToken('.')
				compileval += self._acceptNextToken('identifier')
				compileval += self._acceptNextToken('(')
				compileval += self.compileExpressionList()
				compileval += self._acceptNextToken(')')

		return compileval + '</term>\n'

	def compileExpressionList(self):
		#(expression(','expression)*))?
		compileval = '<expressionList>\n'

		if self._tryNextToken(TERM):
			compileval += self.compileExpression()
			while self._tryNextToken(','):
				compileval += self._acceptNextToken(',')
				compileval += self.compileExpression()

		return compileval + '</expressionList>\n'