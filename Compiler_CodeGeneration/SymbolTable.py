from collections import namedtuple

Symbol = namedtuple('Symbol', ['type', 'kind', 'index'])

class SymbolTable(object):
	def __init__(self):
		self.classScope = {}
		self.subScope = {}
		self.indexs = {'static': 0, 'field': 0, 'argument': 0, 'local': 0}

	def startSubroutine(self):
		self.subScope.clear()
		self.indexs['argument'] = 0
		self.indexs['local'] = 0

	def define(self, name, type, kind):
		index = self.varCount(kind)
		if kind == 'static' or kind == 'field':
			self.classScope[name] = Symbol(type, kind, index)
		else :
			self.subScope[name] = Symbol(type, kind, index)
		self.indexs[kind] += 1

	def varCount(self, kind):
		return self.indexs[kind]
		
	def kindOf(self, name):
		symbol = self._symbolOfName(name)
		if symbol != None:
			if symbol.kind == 'field':
				return 'this'
			else:
				return symbol.kind
		return None

	def typeOf(self, name):
		symbol = self._symbolOfName(name)
		if symbol != None:
			return symbol.type
		return None

	def indexOf(self, name):
		symbol = self._symbolOfName(name)
		if symbol != None:
			return symbol.index
		return None

	def _symbolOfName(self, name):
		symbol = self.subScope.get(name, None)
		if symbol == None:
			symbol = self.classScope.get(name, None)
		return symbol