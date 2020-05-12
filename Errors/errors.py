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
                      'ConvertationError']

    def call(self, error_type, node=None):
        pass


class InterpreterConvertationError(Exception):
    pass