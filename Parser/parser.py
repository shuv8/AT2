import ply.yacc as yacc
from ply.lex import LexError
import sys
from typing import List, Dict, Tuple, Any

from Lexer.lexer import lexer
from SyntaxTree.Tree import TreeNode


class Parser(object):
    tokens = lexer.tokens

    def __init__(self):
        self.ok = True
        self.lexer = lexer()
        self.parses = yacc.yacc(module=self, optimize=1, debug=False, write_tables=False)
        #self._functions: Dict[str] = dict()

    def parse(self, t):
        try:
            res = self.parser.parse(t)
            return res
        except LexError:
            sys.stderr.write(f'Illegal token {t}\n')

    def p_program(self, p):
        """program : statements"""
        p[0] = TreeNode('program', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_statements(self, p):
        """statements : statements statement
                        | statement"""
        if len(p) == 2:
            p[0] = TreeNode('statements', children=[p[1]])
        else:
            p[0] = TreeNode('statements', children=[p[1], p[2]])

    def p_statement(self, p):
        """statement : declaration NEWLINE
                        | assignment NEWLINE
                        | convert NEWLINE
                        | while NEWLINE
                        | until NEWLINE
                        | if NEWLINE
                        | command NEWLINE
                        | function NEWLINE
                        | Function_call NEWLINE"""
        p[0] = p[1]


