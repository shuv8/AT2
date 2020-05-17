import sys
import re
import copy
from Parser.parser import Parser
from SyntaxTree.Tree import TreeNode
from Errors.errors import Error_Handler
from Errors.errors import InterpreterConvertationError
from Errors.errors import InterpreterParametrError
from Errors.errors import InterpreterRedeclarationError
from Errors.errors import InterpreterIndexError
from Errors.errors import InterpreterInitSizeError
from Errors.errors import InterpreterUndeclaredError
from Errors.errors import InterpreterSumSizeError
from Errors.errors import InterpreterIndexNumError

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
                            'ParametrError': 6,
                            'SumSizeError': 7,
                            'IndexNumError': 8}

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
        elif node.type == 'variant':
            if node.children is not None:
                index = node.children.children
                _index = []
                if isinstance(index, list):
                    _index.append(self.interpreter_node(index[0]))
                    _index.append(self.interpreter_node(index[1]))
                else:
                    _index.append(self.interpreter_node(index))
            else:
                _index = None
            try:
                buf = self.get_variant_value(node, index=_index)
            except InterpreterIndexNumError:
                self.error.call(self.error_types['IndexNumError'], node)
                buf = 0
            return buf

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
            try:
                res = self.bin_plus(node.children[0], node.children[1])
            except InterpreterSumSizeError:
                self.error.call(self.error_types['SumSizeError'], node)
                res = 0
            return res
        elif node.type == 'decimal_expression':
            buf = self.interpreter_node(node.children)
            if isinstance(buf, list):
                return buf[0]['int']
            elif isinstance(buf, dict):
                return buf['int']
            elif type(buf) == int:
                return buf
        elif node.type == 'bool_expression':
            return self.interpreter_node(node.children)
        elif node.type == 'string_expression':
            return self.interpreter_node(node.children)
        elif node.type == 'assignment':
            var_name = node.value.value
            if var_name not in self.symbol_table[self.scope].keys():
                self.error.call(self.error_types['UndeclaredError'], node)
            else:
                er = 0
                try:
                    expression = self.interpreter_node(node.children)
                except InterpreterUndeclaredError:
                    self.error.call(self.error_types['UndeclaredError'], node.children)
                    er = 1
                except InterpreterIndexError:
                    self.error.call(self.error_types['IndexError'], node.children.children)
                    er = 1
                if node.value.children is not None:
                    _index = node.value.children.children
                    index = []
                    if isinstance(_index, list):
                        index.append(self.interpreter_node(_index[0]))
                        index.append(self.interpreter_node(_index[1]))
                        if index[0] < 0 or index[1] < 0:
                            self.error.call(self.error_types['IndexError'], node.children)
                            er = 1
                    else:
                        index.append(self.interpreter_node(_index))
                        if index[0] < 0:
                            self.error.call(self.error_types['IndexError'], node.children)
                            er = 1
                else:
                    index = None
                if er == 0:
                    try:
                        self.assign(var_name, expression, index)
                    except InterpreterIndexError:
                        self.error.call(self.error_types['IndexError'], node)
                    except InterpreterIndexNumError:
                        self.error.call(self.error_types['IndexNumError'], node)



    def declare_variant(self, variant, init=None):
        if variant.children is not None:
            size = variant.children.children
            name = variant.value
            if isinstance(size, list):
                first_size = self.interpreter_node(size[0])
                second_size = self.interpreter_node(size[1])
            else:
                first_size = self.interpreter_node(size)
                second_size = 0
            if first_size < 1 or second_size < 0:
                raise InterpreterIndexError
        elif variant.type == 'init' and variant.value.children is not None:
            size = variant.value.children.children
            name = variant.value.value
            if isinstance(size, list):
                first_size = self.interpreter_node(size[0])
                second_size = self.interpreter_node(size[1])
            else:
                first_size = self.interpreter_node(size)
            if first_size < 1 or second_size < 0:
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
            try:
                initialization, init_size = self.initialize(init, first_size, second_size)
            except InterpreterInitSizeError:
                raise InterpreterInitSizeError
        else:
            initialization = Variant(first_size, second_size)
            initialization = initialization.value
            init_size = [first_size, second_size]
        if name in self.symbol_table[self.scope].keys():
            raise InterpreterRedeclarationError
        if init_size[1] == 1:
            init_size[1] = 0
        if init_size[0] != first_size or init_size[1] != second_size:
            raise InterpreterInitSizeError
        else:
            self.symbol_table[self.scope][name] = initialization

    def assign(self, variant, expression, index = None):
        if index is not None:
            new_size = []
            if index[0]>0:
                new_size.append(index[0] + 1)
            else:
                new_size.append(0)
            if len(index) > 1 and index[1] > 0:
                new_size.append(index[1] + 1)
            else:
                if len(index) > 1 and index[1] == 0 and isinstance(expression, list) and len(expression) > 1:
                    raise InterpreterIndexError
                elif isinstance(expression, list) and len(expression) > 1:
                    new_size.append(len(expression))
                else:
                    new_size.append(0)
            self.extend(variant, new_size)
            if len(index) == 2:
                if isinstance(expression, list) and len(expression) == 1 and isinstance(expression[0], dict):
                    self.symbol_table[self.scope][variant][index[0]][index[1]] = expression[0]
                elif type(expression) == int:
                    self.symbol_table[self.scope][variant][index[0]][index[1]]['int'] = expression
                elif type(expression) == bool:
                    self.symbol_table[self.scope][variant][index[0]][index[1]]['bool'] = expression
                elif type(expression) == str:
                    self.symbol_table[self.scope][variant][index[0]][index[1]]['string'] = expression
                else:
                    raise InterpreterIndexError
            else:
                if isinstance(self.symbol_table[self.scope][variant][index[0]], list):
                    raise InterpreterIndexNumError
                if isinstance(expression, list) and len(expression) == 1 and isinstance(expression[0], dict):
                    self.symbol_table[self.scope][variant][index[0]] = expression[0]
                elif isinstance(expression, dict):
                        self.symbol_table[self.scope][variant][index[0]] = expression
                elif type(expression) == int:
                    self.symbol_table[self.scope][variant][index[0]]['int'] = expression
                elif type(expression) == bool:
                    self.symbol_table[self.scope][variant][index[0]]['bool'] = expression
                elif type(expression) == str:
                    self.symbol_table[self.scope][variant][index[0]]['string'] = expression
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
                    for elem1 in range(len(self.symbol_table[self.scope][variant])):
                        for elem2 in self.symbol_table[self.scope][variant][elem1]:
                            elem2[expr_type] = expression

    def extend(self, variant, new_size):
        if len(self.symbol_table[self.scope][variant]) < new_size[0]:
            buf = Variant(new_size[0] - len(self.symbol_table[self.scope][variant]), 0).value
            if isinstance(self.symbol_table[self.scope][variant][0], dict) and (len(new_size) == 2 and new_size[1]>0):
                self.symbol_table[self.scope][variant] = [self.symbol_table[self.scope][variant]]
                for elem in buf:
                    self.symbol_table[self.scope][variant].append([elem])
            elif isinstance(self.symbol_table[self.scope][variant][0], list):
                for elem in buf:
                    self.symbol_table[self.scope][variant].append([elem])
            else:
                for elem in buf:
                    self.symbol_table[self.scope][variant].append(elem)

        if len(new_size) == 2:
            for element in self.symbol_table[self.scope][variant]:
                if len(element) > new_size[1]:
                    new_size[1] = len(element)
                sec_size = new_size[1] - len(element)
                if sec_size == 0:
                    sec_size = -1
                if sec_size == 1:
                    sec_size = 0
                if sec_size > -1:
                    buf = Variant(1, sec_size).value
                    if isinstance(buf[0], list):
                        buf = buf[0]
                    for el in buf:
                        element.append(el)

    def get_variant_value(self, variant, index = None):
        if variant.value not in self.symbol_table[self.scope].keys():
            raise InterpreterUndeclaredError
        else:
            if index is not None:
                if index[0] > 1 and type(self.symbol_table[self.scope][variant.value][0]) == list and len(
                        self.symbol_table[self.scope][variant.value]) - 1 < index[0]:
                    raise InterpreterIndexError
                elif index[0] > 1 and len(index) == 2 and index[1] > 0 and type(self.symbol_table[self.scope][variant.value][0]) == dict:
                    raise InterpreterIndexNumError
                if len(index) == 1:
                    if type(self.symbol_table[self.scope][variant.value][index[0]]) == list:
                        raise InterpreterIndexNumError
                    return copy.deepcopy(self.symbol_table[self.scope][variant.value][index[0]])
                else:
                    if len(self.symbol_table[self.scope][variant.value][index[0]]) < index[1]:
                        raise InterpreterIndexError
                    else:
                        return copy.deepcopy([self.symbol_table[self.scope][variant.value][index[0]][index[1]]])
            else:
                return copy.deepcopy(self.symbol_table[self.scope][variant.value])

    def initialize(self, initialization, first_size=1, second_size=0):
        _init = self.makeinitializator(initialization)
        init_size = []
        init_size.append(len(_init))
        if init_size[0] > first_size:
            return _init, init_size
        if type(_init[0]) == list:
            sec_size = len(_init[0])
        else:
            sec_size = 0
        for elem in _init:
            if type(elem) == list:
                if len(elem) != sec_size:
                    raise InterpreterInitSizeError
            else:
                if sec_size != 0:
                    raise InterpreterInitSizeError

        init_size.append(sec_size)
        return _init, init_size

    def makeinitializator(self, initialization):
        if initialization.type == 'init_lists':
            init = []
            first = self.makeinitializator(initialization.children[0])
            if type(first[0]) == list or len(first) == 1:
                for first_init in first:
                    init.append(first_init)
            else:
                init.append(first)
            last = self.makeinitializator(initialization.children[1])
            if len(last) == 1:
                init.append(last[0])
            else:
                init.append(last)
            return init
        else:
            if initialization.type == 'empty_init_list':
                init = Variant(1)
                return init
            elif initialization.type == 'init_list':
                initialization = initialization.children
            if initialization.type == 'inits':
                init = []
                first = self.makeinitializator(initialization.children[0])
                for init1 in first:
                    init.append(init1)
                last = self.makeinitializator(initialization.children[1])
                init.append(last[0])
                return init
            elif initialization.type == 'const_expression':
                init = Variant(1)
                init = init.value
                init1 = self.interpreter_node(initialization.children[0])
                if type(init1) == int:
                    init[0]['int'] = init1
                elif type(init1) == bool:
                    init[0]['bool'] = init1
                elif type(init1) == str:
                    init[0]['string'] = init1
                return init
            elif initialization.type == 'const_expressions':
                init = Variant(1)
                init = init.value
                _init = []
                inits = self.interpreter_node(initialization.children[0])
                if isinstance(self.interpreter_node(initialization.children[0]), list):
                    for init1 in inits:
                        _init.append(init1)
                else:
                    _init.append(self.interpreter_node(initialization.children[0]))
                _init.append(self.interpreter_node(initialization.children[1]))
                for i in _init:
                    if type(i) == int:
                        init[0]['int'] = i
                    elif type(i) == bool:
                        init[0]['bool'] = i
                    elif type(i) == str:
                        init[0]['string'] = i
                return init




    def unar_minus(self, _expression):
        value = self.interpreter_node(_expression)
        if type(value) == int:
            value = - value
        elif type(value) == bool:
            if value:
                value = False
            else:
                value = True
        elif type(value) == str:
            pass
            # TODO: minus for strings(robot commands)
        elif type(value) == dict:
            value['int'] = -value['int']
            if value['bool']:
                value['bool'] = False
            else:
                value['bool'] = True
        elif type(value) == list:
            for elem in value:
                if isinstance(elem, list):
                    for elem1 in elem:
                        elem1['int'] = -elem1['int']
                        if elem1['bool']:
                            elem1['bool'] = False
                        else:
                            elem1['bool'] = True
                else:
                    elem['int'] = -elem['int']
                    if elem['bool']:
                        elem['bool'] = False
                    else:
                        elem['bool'] = True
        return value

    def bin_plus(self, _expression1, _expression2):
        value1 = self.interpreter_node(_expression1)
        value2 = self.interpreter_node(_expression2)
        if type(value1) == list and type(value2) == list:
            if type(value1) == type(value2) and len(value1) != len(value2):
                raise InterpreterSumSizeError
        if type(value1) == int and type(value2) == int:
            return value1 + value2
        elif type(value1) == bool and type(value2) == bool:
            return value1 or value2
        elif type(value1) == str and type(value2) == str:
            return value1 + value2
        elif type(value1) == list and len(value1) == 1:
            value1 = value1[0]
        if type(value1) == dict:
            if type(value2) == int:
                value1['int'] += value2
                return [value1]
            elif type(value2) == bool:
                value1['bool'] = value1['bool'] or value2
                return [value1]
            elif type(value2) == str:
                value1['string'] += value2
                return [value1]
        if type(value2) == list and len(value2) == 1:
            value2 = value2[0]
        if type(value2) == dict:
            if type(value1) == int:
                value2['int'] += value1
                return [value2]
            elif type(value2) == bool:
                value2['bool'] = value2['bool'] or value1
                return [value2]
            elif type(value2) == str:
                value2['string'] += value1
                return [value2]
        if type(value1) == dict and type(value2) == dict:
            value = [{'int':0, 'bool':False, 'string':""}]
            value[0]['int'] = value1['int'] + value2['int']
            value[0]['int'] = value1['bool'] or value2['bool']
            value[0]['string'] = value1['string'] + value2['string']
            return value
        # elif type(value1) == list:
        #     for elem in value:
        #         if isinstance(elem, list):
        #             for elem1 in elem:
        #                 elem1['int'] = -elem1['int']
        #                 if elem1['bool']:
        #                     elem1['bool'] = False
        #                 else:
        #                     elem1['bool'] = True
        #         else:
        #             elem['int'] = -elem['int']
        #             if elem['bool']:
        #                 elem['bool'] = False
        #             else:
        #                 elem['bool'] = True
        # TODO: addition for variants with different sizes or const + variant


data = '''VARIANT a [3, 2] = {{123, TRUE; "NRNU";}{2;}}
VARIANT b [1, 5]
b [2] = TRUE
'''
data1 ='''VARIANT b [2,2]
VARIANT a [2,2]
a = 123
b [1, 0] = a[1, 0] + a[0,1]
'''
a = Interpreter()
a.interpreter(data1)
pass

# a = Variant(1, 4)
# print(a)
