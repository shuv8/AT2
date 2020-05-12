import sys
import re
from Parser.parser import Parser
from SyntaxTree.Tree import TreeNode
from Errors.errors import Error_Handler
from Errors.errors import InterpreterConvertationError
from Errors.errors import InterpreterParametrError
from Errors.errors import InterpreterRedeclarationError
from Errors.errors import InterpreterIndexError


class Variant:
    def __init__(self, first_size=1, second_size=0):
        self.first_size = first_size
        self.second_size = second_size
        self.value = []
        if second_size == 0:
            for i in range(first_size):
                self.value.append({'int': 0, 'bool': False, 'string': ""})
        else:
            for i in range(first_size):
                buf = []
                for j in range(second_size):
                    buf.append({'int': 0, 'bool': False, 'string': ""})
                self.value.append(buf)


class TypeConverter:
    def __init__(self):
        pass

    def convert(self, val, type_to):
        try:
            if type(val) == int:
                if type_to == 'int':
                    return val
                elif type_to == 'bool':
                    return bool(val)
                elif type_to == 'string':
                    return str(val)
            elif type(val) == bool:
                if type_to == 'int':
                    return int(val)
                elif type_to == 'bool':
                    return val
                elif type_to == 'string':
                    return self.bool_to_string(val)
            elif type(val) == str:
                if type_to == 'int':
                    return self.string_to_int(val)
                elif type_to == 'bool':
                    return self.string_to_bool(val)
                elif type_to == 'string':
                    return val
        except InterpreterConvertationError:
            raise InterpreterConvertationError('Bad convertation!')

    @staticmethod
    def bool_to_string(val):
        if val:
            return 'TRUE'
        else:
            return 'FALSE'

    @staticmethod
    def string_to_int(val):
        res = re.findall(r'\d+', val)
        if len(res) != 0:
            return int(res[0])
        else:
            raise InterpreterConvertationError

    @staticmethod
    def string_to_bool(val):
        reg = r'TRUE|FALSE'
        res = re.findall(reg, val)
        if len(res) != 0:
            if res[0] == 'TRUE':
                return True
            else:
                return False
        else:
            raise InterpreterConvertationError


class Interpreter:

    def __init__(self, parser=Parser(), converter=TypeConverter()):
        self.parser = parser
        self.converter = converter
        self.program = None
        self.symbol_table = [dict()]
        self.tree = None
        self.functions = None
        self.scope = 0
        self.error = Error_Handler()
        self.error_types = {'UnexpectedError': 0,
                            'RedeclarationError': 1,
                            'UndeclaredError': 2,
                            'IndexError': 3,
                            'ConvertationError': 4}

    def interpreter(self, program=None):
        self.program = program
        self.symbol_table = [dict()]
        self.tree, _ok, self.functions = self.parser.parse(self.program)
        if _ok:
            self.interpreter_tree(self.tree)
            self.interpreter_node(self.tree)
        else:
            sys.stderr.write(f'Can\'t interpretate this program. Incorrect syntax!\n')

    def interpreter_tree(self, tree):
        print("Program tree:\n")
        tree.print()
        print('\n')

    def interpreter_node(self, node):
        if node is None:
            return
        # unexpected error
        if node.type == 'error':
            self.error.call
        # program
        elif node.type == 'program':
            self.interpreter_node(node.children)
        # program -> statements
        elif node.type == 'statements':
            for child in node.children:
                self.interpreter_node(child)
        elif node.type == 'statement':
            self.interpreter_node(node.children)
        elif node.type == 'declaration':
            declaration_child = node.children
            if isinstance(declaration_child, list):
                pass
            else:
                try:
                    self.declare_variant(declaration_child)
                except InterpreterRedeclarationError:
                    self.error.call(self.error_types['RedeclarationError'], node)
                except InterpreterIndexError:
                    self.error.call(self.error_types['IndexError'], node)
        elif node.type == 'expression':
            return self.interpreter_node(node.children)
        elif node.type == 'const_expression':
            return self.interpreter_node(node.children)
        elif node.type == 'decimal_expression':
            return self.interpreter_node(node.children)
        elif node.type == 'bool_expression':
            return self.interpreter_node(node.children)
        elif node.type == 'string_expression':
            return self.interpreter_node(node.children)
        elif node.type == 'assignment':
            var_name = node.value.value
            index = 0
            if var_name not in self.symbol_table[self.scope].keys():
                self.error.call(self.error_types['UndeclaredError'], node)
            else:
                pass



    def declare_variant(self, variant, init=None):
        if variant.children is not None:
            size = variant.children.children
            if isinstance(size, list):
                first_size = self.interpreter_node(size[0])
                second_size = self.interpreter_node(size[1])
            else:
                first_size = self.interpreter_node(size)
            if first_size < 1 or second_size < 0:
                raise InterpreterIndexError
        else:
            first_size = 1
            second_size = 0
        if init is not None:
            pass
            # initialization = self.makeinitializator(init)
        else:
            initialization = Variant(first_size, second_size)
            initialization = initialization.value
        if variant.value in self.symbol_table[self.scope].keys():
            raise InterpreterRedeclarationError
        else:
            self.symbol_table[self.scope][variant.value] = initialization


data = '''VARIANT a
VARIANT b
VARIANT c
'''

a = Interpreter()
a.interpreter(data)
pass
