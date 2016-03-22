from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable

TYPE = ['int', 'char', 'boolean', 'identifier']
STATEMENT = ['let', 'do', 'while', 'if', 'return']
TERM = ['identifier', 'integerConstant', 'stringConstant', 'keyword', '(', '-', '~']
OP = ['+', '-', '*', '/', '&', '|', '>', '<', '=']
OP_COMMAND = {'+': 'add', '-': 'sub', '=': 'eq', '>': 'gt', '<': 'lt', '&': 'and', '|': 'or'}

class CompilationEngine(object):
	def __init__(self, src, output):
		self.tokenizer = JackTokenizer(src)
		self.writer = VMWriter(output)
		self.symbolTable = SymbolTable()
		self.labelIndex = 0

	def _acceptNextToken(self, token):
		if self.tokenizer.hasMoreToken():
			self.tokenizer.advance()
			typ = self.tokenizer.tokenType()
			tok = self.tokenizer.tokenValue()
			if type(token) != list:
				token = [token]
			if typ in token or tok in token:
				return tok
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
		self._acceptNextToken('class')
		self.classname = self._acceptNextToken('identifier')
		self._acceptNextToken('{')

		while self._tryNextToken(['static', 'field']):
			self.compileClassVarDec()
		while self._tryNextToken(['constructor', 'function', 'method']):
			self.compileSubroutine()
		self._acceptNextToken('}')

		self.writer.close()

	def compileClassVarDec(self):
		#('static'|'field') type varName (','varName)* ';'
		kind = self._acceptNextToken(['static', 'field'])
		type = self._acceptNextToken(['int', 'char', 'boolean', 'identifier'])
		self.symbolTable.define(self._acceptNextToken('identifier'), type, kind)

		while self._tryNextToken(','):
			self._acceptNextToken(',')
			self.symbolTable.define(self._acceptNextToken('identifier'), type, kind)
		self._acceptNextToken(';')

	def compileSubroutine(self):
		#('constructor'|'function'|'method')
		#('void'|type)subroutineName'('parameterList')'
		#subroutineBody
		self.labelIndex = 0

		self.symbolTable.startSubroutine()
		subroutine = self._acceptNextToken(['constructor', 'function', 'method'])
		self._acceptNextToken(['void', 'int', 'char', 'boolean', 'identifier'])
		functionname = self._acceptNextToken('identifier')

		if subroutine == 'method':
			self.symbolTable.define('this', self.classname, 'argument')

		self._acceptNextToken('(')
		self.compileParameterList()
		self._acceptNextToken(')')
		self._acceptNextToken('{')

		argc = 0
		while self._tryNextToken('var'):
			argc += self.compileVarDec()
		self.writer.writeFunction(self.classname + '.' + functionname, argc)

		if subroutine == 'constructor':
			self.writer.writePush('constant', self.symbolTable.varCount('field'))
			self.writer.writeCall('Memory.alloc', 1)
			self.writer.writePop('pointer', 0)
		elif subroutine == 'method':
			self.writer.writePush('argument', 0)
			self.writer.writePop('pointer', 0)
		while self._tryNextToken(STATEMENT):
			self.compileStatements()
		self._acceptNextToken('}')

	def compileParameterList(self):
		#((type varName)(','type varName)*)?
		if self._tryNextToken(TYPE):
			type = self._acceptNextToken(TYPE)
			self.symbolTable.define(self._acceptNextToken('identifier'), type, 'argument')
			while self._tryNextToken(','):
				self._acceptNextToken(',')
				type = self._acceptNextToken(TYPE)
				self.symbolTable.define(self._acceptNextToken('identifier'), type, 'argument')

	def compileVarDec(self):
		#'var' type varName (',' varName)*';'
		argc = 1
		self._acceptNextToken('var')
		type = self._acceptNextToken(TYPE)
		self.symbolTable.define(self._acceptNextToken('identifier'), type, 'local')

		while self._tryNextToken(','):
			self._acceptNextToken(',')
			argc += 1
			self.symbolTable.define(self._acceptNextToken('identifier'), type, 'local')
		self._acceptNextToken(';')
		return argc

	def compileStatements(self):
		#statement*
		#letStatement|ifStatement|whileStatement|doStatement|returnStatement
		while self._tryNextToken(STATEMENT):
			if self._tryNextToken('let'):
				self.compileLet()
			elif self._tryNextToken('if'):
				self.compileIf()
			elif self._tryNextToken('while'):
				self.compileWhile()
			elif self._tryNextToken('do'):
				self.compileDo()
			elif self._tryNextToken('return'):
				self.compileReturn()

	def compileDo(self):
		#'do' subroutineCall ';'
		#subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
		self._acceptNextToken('do')
		funcname = self._acceptNextToken('identifier')

		argc = 0
		if self._tryNextToken('.'):
			self._acceptNextToken('.')
			type = self.symbolTable.typeOf(funcname)
			if type != None:
				argc += 1
				self.writer.writePush(self.symbolTable.kindOf(funcname), self.symbolTable.indexOf(funcname))
				funcname = type + '.' + self._acceptNextToken('identifier')				#game.run()
			else:
				funcname = funcname + '.' + self._acceptNextToken('identifier')			#Game.run()
		else:
			argc += 1
			funcname = self.classname + '.' + funcname 										#run()
			self.writer.writePush('pointer', 0)
	
		self._acceptNextToken('(')
		argc += self.compileExpressionList()
		self._acceptNextToken(')')
		self._acceptNextToken(';')

		self.writer.writeCall(funcname, argc)
		self.writer.writePop('temp', 0)

	def compileLet(self):
		#'let' varName ('[' expression ']')? '=' expression ';'
		self._acceptNextToken('let')
		varName = self._acceptNextToken('identifier')
		if self._tryNextToken('['):
			self.writer.writePush(self.symbolTable.kindOf(varName), self.symbolTable.indexOf(varName))
			self._acceptNextToken('[')
			self.compileExpression()
			self._acceptNextToken(']')
			self.writer.writeArithmetic('add')
			self._acceptNextToken('=')
			self.compileExpression()
			self._acceptNextToken(';')
			self.writer.writePop('temp', 0)
			self.writer.writePop('pointer', 1)
			self.writer.writePush('temp', 0)
			self.writer.writePop('that', 0)
		else:
			self._acceptNextToken('=')
			self.compileExpression()
			self._acceptNextToken(';')
			self.writer.writePop(self.symbolTable.kindOf(varName), self.symbolTable.indexOf(varName))

	def compileWhile(self):
		#'while' '(' expression ')''{' statements '}'
		index = str(self.labelIndex)
		self.labelIndex += 1

		self.writer.writeLabel('WHILE' + index)
		self._acceptNextToken('while')
		self._acceptNextToken('(')
		self.compileExpression()
		self._acceptNextToken(')')
		self.writer.writeArithmetic('not')

		self.writer.writeIf('WHILE_END' + index)
		self._acceptNextToken('{')
		self.compileStatements()
		self._acceptNextToken('}')
		self.writer.writeGoto('WHILE' + index)
		self.writer.writeLabel('WHILE_END' + index)

	def compileReturn(self):
		#'return' expression? ';'
		self._acceptNextToken('return')

		if self._tryNextToken(';'):
			self._acceptNextToken(';')
			self.writer.writePush('constant', 0)
		else:
			self.compileExpression()
			self._acceptNextToken(';')
		self.writer.writeReturn()

	def compileIf(self):
		#'if' '(' expression ')' '{' statements '}'
		#('else' '{' statements '}')?
		index = str(self.labelIndex);
		self.labelIndex += 1

		self._acceptNextToken('if')
		self._acceptNextToken('(')
		self.compileExpression()
		self._acceptNextToken(')')
		self.writer.writeArithmetic('not')
		self.writer.writeIf('IF_TRUE' + index)

		self._acceptNextToken('{')
		self.compileStatements()
		self._acceptNextToken('}')
		self.writer.writeGoto('IF_FALSE' + index)
		self.writer.writeLabel('IF_TRUE' + index)

		if self._tryNextToken('else'):
			self._acceptNextToken('else')
			self._acceptNextToken('{')
			self.compileStatements()
			self._acceptNextToken('}')
		self.writer.writeLabel('IF_FALSE' + index)

	def compileExpression(self):
		#term(op term)*
		self.compileTerm()
		while self._tryNextToken(OP):
			op = self._acceptNextToken(OP)
			self.compileTerm()
			if op == '*':
				self.writer.writeCall('Math.multiply', 2)
			elif op == '/':
				self.writer.writeCall('Math.divide', 2)
			else:
				self.writer.writeArithmetic(OP_COMMAND[op])

	def compileTerm(self):
		#integerConstant|stringConstant|keywordConstant|varName|
		
		if self._tryNextToken('('):										#'('expression')'
			self._acceptNextToken('(')
			self.compileExpression()
			self._acceptNextToken(')')
		elif self._tryNextToken(['-', '~']):							#unaryOp term
			unaryOp = self._acceptNextToken(['-', '~'])
			self.compileTerm()
			if unaryOp == '-':
				self.writer.writeArithmetic('neg')
			else:
				self.writer.writeArithmetic('not')
		else:
			first_s = self._acceptNextToken(TERM)
			if self._tryNextToken('['):									#varName'['expression']'
				self.writer.writePush(self.symbolTable.kindOf(first_s), self.symbolTable.indexOf(first_s))
				self._acceptNextToken('[')
				self.compileExpression()
				self._acceptNextToken(']')
				self.writer.writeArithmetic('add')
				self.writer.writePop('pointer', 1)
				self.writer.writePush('that', 0)
			elif self._tryNextToken('('):								#subroutineCall run()
				self.writer.writePush('pointer', 0)
				self._acceptNextToken('(')
				argc = self.compileExpressionList() + 1
				self._acceptNextToken(')')
				self.writer.writeCall(self.classname + '.' + first_s, argc)
			elif self._tryNextToken('.'):								#subroutineCall game.run()
				self._acceptNextToken('.')
				idenfitier = self._acceptNextToken('identifier')
				type = self.symbolTable.typeOf(first_s)
				argc = 0
				callname = first_s
				if type != None:
					argc += 1
					callname = type
					self.writer.writePush(self.symbolTable.kindOf(first_s), self.symbolTable.indexOf(first_s))
				self._acceptNextToken('(')
				argc += self.compileExpressionList()
				self._acceptNextToken(')')
				self.writer.writeCall(callname + '.' + idenfitier, argc)
			else:
				tokenType = self.tokenizer.tokenType()
				if tokenType == 'integerConstant':
					self.writer.writePush('constant', int(first_s))
				elif tokenType == 'stringConstant':
					self.writer.writePush('constant', len(first_s))
					self.writer.writeCall('String.new', 1)
					for c in first_s:
						self.writer.writePush('constant', ord(c))
						self.writer.writeCall('String.appendChar', 2)
				elif tokenType == 'identifier':
					self.writer.writePush(self.symbolTable.kindOf(first_s), self.symbolTable.indexOf(first_s))
				else:
					if first_s == 'null' or first_s == 'false':
						self.writer.writePush('constant', 0)
					elif first_s == 'true':
						self.writer.writePush('constant', 1)
						self.writer.writeArithmetic('neg')
					elif first_s == 'this':
						self.writer.writePush('pointer', 0)

	def compileExpressionList(self):
		#(expression(','expression)*))?
		argc = 0
		if self._tryNextToken(TERM):
			self.compileExpression()
			argc += 1
			while self._tryNextToken(','):
				self._acceptNextToken(',')
				self.compileExpression()
				argc += 1
		return argc
