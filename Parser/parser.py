import ply.yacc as yacc
from ply.lex import LexError
import sys
from typing import List, Dict, Tuple, Any

from Lexer.lexer import Lexer
from SyntaxTree.Tree import TreeNode


class Parser(object):
    tokens = Lexer.tokens

    def __init__(self):
        self.ok = True
        self.lexer = Lexer()
        self.parser = yacc.yacc(module=self)
        self._functions = dict()

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
            p[0] = p[1]
        else:
            p[0] = TreeNode('statements', children=[p[1], p[2]])

    def p_statement(self, p):
        """statement : declaration NEWLINE
                        | assignment NEWLINE"""
                        # | convert NEWLINE
                        # | while NEWLINE
                        # | until NEWLINE
                        # | if NEWLINE
                        # | command NEWLINE
                        # | function NEWLINE
                        # | function_call NEWLINE"""
        p[0] = p[1]

    def p_declaration(self, p):
        """declaration : VARIANT variant
                        | VARIANT variant ASSIGNMENT initialization"""
        if len(p) == 3:
            p[0] = TreeNode('declaration', value='VARIANT', children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('declaration', value='VARIANT', children=[TreeNode('init', value=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1)), p[4], TreeNode('init_end')], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_variant(self, p):
        """variant : NAME
                    | NAME varsize"""
        if len(p) == 2:
            p[0] = TreeNode('variant', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('variant', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_varsize(self, p):
        """varsize : LSQBRACKET decimal_expression RSQBRACKET
                    | LSQBRACKET decimal_expression COMMA decimal_expression RSQBRACKET"""
        if len(p) == 4:
            p[0] = TreeNode('varsize', children=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2))
        else:
            p[0] = TreeNode('varsize', children=[p[2], p[4]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_initialization(self, p):
        """initialization : LBRACE init_lists RBRACE"""
        p[0] = p[2]

    def p_init_lists(self, p):
        """init_lists : init_lists init_list
                        | init_list"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = TreeNode('init_lists', children=[p[1], p[2]])

    def p_init_list(self, p):
        """init_list : LBRACE inits RBRACE
                        | LBRACE RBRACE"""
        if len(p) == 4:
            p[0] = TreeNode('init_list', children=p[2])
        else:
            p[0] = TreeNode('empty init list', lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_inits(self, p):
        """inits : inits init
                    | init"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = TreeNode('inits', children=[p[1], p[2]])

    def p_init(self, p):
        """init : expressions COMMA expression SEMICOLON
                    | expression SEMICOLON"""
        if len(p) == 3:
            p[0] = TreeNode('expression', children=[p[1]])
        else:
            p[0] = TreeNode('expressions', children=[p[1], p[3]])

    def p_expressions(self, p):
        """expressions : expressions COMMA expression
                        | expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = TreeNode('expressions', children=[p[1], p[3]])

    def p_expression(self, p):
        """expression : math_expression
                        | const
                        | variant"""
        p[0] = TreeNode('expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_decimal_expression(self, p):
        """decimal_expression : dec_math_expression
                                | decimal_const
                                | variant"""
        p[0] = TreeNode('decimal_expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_math_expression(self, p):
        """math_expression : expression PLUS expression
                            | MINUS expression"""
        if len(p) == 3:
            p[0] = TreeNode('unar_op', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('bin_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_dec_math_expression(self, p):
        """dec_math_expression : decimal_expression PLUS decimal_expression
                                | MINUS decimal_expression"""
        if len(p) == 3:
            p[0] = TreeNode('unar_op', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            print(p[2])
            p[0] = TreeNode('bin_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_const(self, p):
        """const : TRUE
                | FALSE
                | DECIMAL
                | LETTERS"""
        p[0] = TreeNode('const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_decimal_const(self, p):
        """decimal_const : DECIMAL"""
        p[0] = TreeNode('decimal_const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_assignment(self, p):
        """assignment : variant ASSIGNMENT expression"""
        p[0] = TreeNode('assignment', value=p[1], children=p[3], lineno=p.lineno(2), lexpos=p.lexpos(2))

    # def p_convert(self, p):
    #     """convert : """






data = '''VARIANT b [12 + -123]
a = 1234
a = "odin" + "dva"
'''
lexer = Lexer()
lexer.input(data)
while True:
    token = lexer.token()
    if token is None:
        break
    else:
        print(token)

parser = Parser()
tree = parser.parse(data)
tree.print()