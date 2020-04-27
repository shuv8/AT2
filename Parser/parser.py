import ply.yacc as yacc
from ply.lex import LexError
import sys
from typing import List, Dict, Tuple, Any

from Lexer.lexer import lexer


class Parser():
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
        #p[0] = node(...)
