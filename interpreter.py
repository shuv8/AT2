import sys
import re
from Parser.parser import Parser
from SyntaxTree.Tree import TreeNode
from Errors.errors import Error_Handler
from Errors.errors import InterpreterConvertationError
from Errors.errors import InterpreterParametrError
from Errors.errors import InterpreterRedeclarationError
from Errors.errors import InterpreterIndexError
from Errors.errors import InterpreterInitSizeError


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
                            'InitSizeError': 4,
                            'ConvertationError': 5,
                            'ParametrError': 6}

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
                initialization = node.children[1]
                try:
                    self.declare_variant(declaration_child[0], initialization)
                except InterpreterRedeclarationError:
                    self.error.call(self.error_types['RedeclarationError'], node)
                except InterpreterIndexError:
                    self.error.call(self.error_types['IndexError'], node)
                except InterpreterInitSizeError:
                    self.error.call(self.error_types['InitSizeError'], node)
            else:
                try:
                    self.declare_variant(declaration_child)
                except InterpreterRedeclarationError:
                    self.error.call(self.error_types['RedeclarationError'], node)
                except InterpreterIndexError:
                    self.error.call(self.error_types['IndexError'], node)
        elif node.type == 'expression':
            return self.interpreter_node(node.children)
        elif node.type == 'const_expressions':
            buf = []
            if isinstance(self.interpreter_node(node.children[0]), list):
                for buf1 in self.interpreter_node(node.children[0]):
                    buf.append(buf1)
            else:
                buf.append(self.interpreter_node(node.children[0]))
            buf.append(self.interpreter_node(node.children[1]))
            return buf
        elif node.type == 'const_expression':
            return self.interpreter_node(node.children)
        elif node.type == 'decimal_const' or node.type == 'bool_const' or node.type == 'string_const':
            return node.value
        elif node.type == 'unar_op':
            return self.unar_minus(node.children)
        elif node.type == 'bin_op':
            return self.bin_plus(node.children[0], node.children[1])
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
                expression = self.interpreter_node(node.children)
                if node.value.children is not None:
                    pass
                else:
                    index = None
                try:
                    self.assign(var_name, expression, index)
                except:
                    pass



    def declare_variant(self, variant, init=None):
        if variant.children is not None:
            size = variant.children.children
            name = variant.value
            if isinstance(size, list):
                first_size = self.interpreter_node(size[0])
                second_size = self.interpreter_node(size[1])
            else:
                first_size = self.interpreter_node(size)
            if first_size < 0 or second_size < 0:
                raise InterpreterIndexError
        elif variant.type == 'init' and variant.value.children is not None:
            size = variant.value.children.children
            name = variant.value.value
            if isinstance(size, list):
                first_size = self.interpreter_node(size[0])
                second_size = self.interpreter_node(size[1])
            else:
                first_size = self.interpreter_node(size)
            if first_size < 0 or second_size < 0:
                raise InterpreterIndexError
        elif variant.type == 'init':
            name = variant.value.value
            first_size = 1
            second_size = 0
        else:
            first_size = 1
            second_size = 0
            name = variant.value
        if init is not None:
            initialization, init_size = self.makeinitializator(init)
        else:
            initialization = Variant(first_size, second_size)
            initialization = initialization.value
            init_size = [first_size, second_size]
        if name in self.symbol_table[self.scope].keys():
            raise InterpreterRedeclarationError
        if init_size[0] != first_size or init_size[1] != second_size:
            raise InterpreterInitSizeError
        else:
            self.symbol_table[self.scope][name] = initialization

    def assign(self, variant, expression, index = None):
        if index is not None:
            pass
            # TODO: assignment for variant element
        else:
            if isinstance(expression, list):
                self.symbol_table[self.scope][variant] = expression
            else:
                if type(expression) == int:
                    expr_type = 'int'
                elif type(expression) == bool:
                    expr_type = 'bool'
                elif type(expression) == str:
                    expr_type = 'string'

                if isinstance(self.symbol_table[self.scope][variant][0], dict):
                    for elem in self.symbol_table[self.scope][variant]:
                        elem[expr_type] = expression
                elif isinstance(self.symbol_table[self.scope][variant][0], list):
                    for elem1 in self.symbol_table[self.scope][variant]:
                        for elem2 in self.symbol_table[self.scope][variant][elem1]:
                            elem2[expr_type] = expression

    def makeinitializator(self, initialization):
        if initialization.type == 'init_lists':
            pass
            # TODO: init lists (size of variant [>1, ...]
        else:
            init_size = [1]
            if initialization.type == 'empty_init_list':
                init_size.append(0)
                init = Variant(init_size[0])
                return init, init_size
            elif initialization.type == 'init_list':
                initializator = initialization.children
            if initializator.type == 'inits':
                second_size = 2
                pass
            # TODO: inits (size of variant [..., >1]
            elif initializator.type == 'const_expression':
                init_size.append(0)
                init = Variant(init_size[0])
                init = init.value
                init1 = self.interpreter_node(initializator.children[0])
                if type(init1) == int:
                    init[0]['int'] = init1
                elif type(init1) == bool:
                    init[0]['bool'] = init1
                elif type(init1) == str:
                    init[0]['string'] = init1
                return init, init_size
            elif initializator.type == 'const_expressions':
                init_size.append(0)
                init = Variant(init_size[0])
                init = init.value
                _init = []
                inits = self.interpreter_node(initializator.children[0])
                if isinstance(self.interpreter_node(initializator.children[0]), list):
                    for init1 in inits:
                        _init.append(init1)
                else:
                    _init.append(self.interpreter_node(initializator.children[0]))
                _init.append(self.interpreter_node(initializator.children[1]))
                for i in _init:
                    if type(i) == int:
                        init[0]['int'] = i
                    elif type(i) == bool:
                        init[0]['bool'] = i
                    elif type(i) == str:
                        init[0]['string'] = i
                return init, init_size




    def un_minus(self, _expression):
        pass
        # TODO: unar minus

    def bin_plus(self, _expression1, _expression2):
        pass
        # TODO: binary plus


data = '''VARIANT a [1, 2] = {{123, TRUE;}}
'''

a = Interpreter()
a.interpreter(data)
pass

# a = Variant(1, 4)
# print(a)
