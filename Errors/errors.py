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
                      'InitSizeError'
                      'ConvertationError',
                      'ParametrError']

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
        elif self.type == 3:
            if node.type == 'declaration':
                if isinstance(node.children, list):
                    sys.stderr.write(f'Variant "{node.children[0].value}" has wrong indexation at line {self.node.lineno}\n')
                else:
                    sys.stderr.write(f'Variant "{node.children.value}" has wrong indexation at line {self.node.lineno}\n')
        elif self.type == 4:
            if node.type == 'declaration':
                if isinstance(node.children, list):
                    sys.stderr.write(f'Variant "{node.children[0].value.value}" at line {self.node.lineno} size doesn\'t match initializator size\n')
                else:
                    sys.stderr.write(f'Variant "{node.children.value.value}" at line {self.node.lineno} size doesn\'t match initializator size\n')


class InterpreterConvertationError(Exception):
    pass


class InterpreterParametrError(Exception):
    pass


class InterpreterRedeclarationError(Exception):
    pass


class InterpreterIndexError(Exception):
    pass


class InterpreterInitSizeError(Exception):
    pass
