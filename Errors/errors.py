import sys
from SyntaxTree.Tree import TreeNode

class Error_Handler:
    def __init__(self):
        self.type = None
        self.node = None
        self.types = ['UnexpectedError',
                      'RedeclarationError',
                      'UndeclaredError',
                      'IndexError',
                      'InitSizeError',
                      'ConvertationError',
                      'ParametrError',
                      'SumSizeError',
                      'IndexNumError',
                      'ReturnRepeatError',
                      'RecursionError',
                      'ReturnError',
                      'CommandError',
                      'RobotError']

    def call(self, error_type, node=None):
        self.type = error_type
        self.node = node
        sys.stderr.write(f'Error {self.types[int(error_type)]}: ')
        if self.type == 0:
            pass
        elif self.type == 1:
            if isinstance(node.children, list):
                sys.stderr.write(f'Variant "{self.node.children[0].value}" at line {self.node.lineno} is already declared\n')
            else:
                sys.stderr.write(f'Variant "{self.node.children.value}" at line {self.node.lineno} is already declared\n')
        elif self.type == 2:
            if self.node.type == 'assignment':
                sys.stderr.write(f'Variant {self.node.value.value} at line {self.node.lineno} is used before declaration\n')
            else:
                sys.stderr.write(f'Something at line {self.node.lineno} is used before declaration\n')
        elif self.type == 3:
            if node.type == 'declaration':
                if isinstance(node.children, list):
                    sys.stderr.write(f'Variant "{node.children[0].value}" has wrong indexation at line {self.node.lineno}\n')
                else:
                    sys.stderr.write(f'Variant "{node.children.value}" has wrong indexation at line {self.node.lineno}\n')
            elif node.type == 'assignment':
                sys.stderr.write(f'Left-side variant element size doesn\'t match right-side variant at line {self.node.lineno}\n')
            elif node.type == 'expression':
                sys.stderr.write(f'Wrong indexation of right-side variant at line {self.node.lineno}\n')
            elif node.type == 'variant':
                sys.stderr.write(f'Variant "{node.value}" has wrong indexation at line {self.node.lineno}\n')
            elif node.type == 'convert':
                sys.stderr.write(f'Variant "{node.children.value}" has wrong indexation at line {self.node.lineno}\n')
            elif node.type == 'digitize':
                sys.stderr.write(f'Variant "{node.children.value}" has wrong indexation at line {self.node.lineno}\n')
            else:
                sys.stderr.write(f'Wrong indexation\n')
        elif self.type == 4:
            if node.type == 'declaration':
                if isinstance(node.children, list):
                    sys.stderr.write(f'Variant "{node.children[0].value.value}" at line {self.node.lineno} size doesn\'t match initializator size\n')
                else:
                    sys.stderr.write(f'Variant "{node.children.value.value}" at line {self.node.lineno} size doesn\'t match initializator size\n')
        elif self.type == 5:
            sys.stderr.write(f'Can\'t find necessary part of the variant "{node.children.value}" for convertation at line {self.node.lineno}\n')
        elif self.type == 6:
            sys.stderr.write(f'Function parametr using not in function at line {self.node.lineno}\n')
        elif self.type == 7:
            sys.stderr.write(f'Variants sizes doesn\'t match at line {self.node.lineno}\n')
        elif self.type == 8:
            sys.stderr.write(f'Amount of indexes doesn\'t match variant size at line {self.node.lineno}\n')
        elif self.type == 9:
            sys.stderr.write(f'>1 returns in function at line {self.node.lineno}\n')
        elif self.type == 10:
            sys.stderr.write(f'Maximum recursion depth reached\n')
        elif self.type == 11:
            sys.stderr.write(f'Function return expression expected but missing at line {self.node.lineno}\n')
        elif self.type == 12:
            sys.stderr.write(f'Inappropriate word in robot command at line {self.node.lineno}\n')
        elif self.type == 13:
            sys.stderr.write(f'There are no robot to execute this command at line {self.node.lineno}\n')


class InterpreterConvertationError(Exception):
    pass


class InterpreterParametrError(Exception):
    pass


class InterpreterRedeclarationError(Exception):
    pass


class InterpreterUndeclaredError(Exception):
    pass


class InterpreterIndexError(Exception):
    pass


class InterpreterInitSizeError(Exception):
    pass


class InterpreterSumSizeError(Exception):
    pass


class InterpreterIndexNumError(Exception):
    pass


class InterpreterRecursionError(Exception):
    pass
