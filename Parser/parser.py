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
            return res, self.ok
        except LexError:
            sys.stderr.write(f'Illegal token {t}\n')

    def p_program(self, p):
        """program : statements"""
        p[0] = TreeNode('program', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_statements(self, p):
        """statements : statements statement
                        | statement"""
        if len(p) == 2:
            p[0] = TreeNode('statement', children=p[1])
        else:
            p[0] = TreeNode('statements', children=[p[1], TreeNode('statement', children=p[2])])

    def p_statement(self, p):
        """statement : empty NEWLINE
                        | declaration NEWLINE
                        | assignment NEWLINE
                        | convert NEWLINE
                        | digitize NEWLINE
                        | while NEWLINE
                        | until NEWLINE
                        | if NEWLINE
                        | command NEWLINE
                        | statement_error NEWLINE"""
                        # | function NEWLINE
                        # | function_call NEWLINE
        p[0] = p[1]

    def p_empty(self, p):
        """empty : """
        pass

    def p_declaration(self, p):
        """declaration : VARIANT variant
                        | VARIANT variant ASSIGNMENT initialization"""
        if len(p) == 3:
            p[0] = TreeNode('declaration', value='VARIANT', children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('declaration', value='VARIANT', children=[TreeNode('init', value=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1)), p[4], TreeNode('init_end')], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_variant(self, p):
        """variant : NAME
                    | NAME varsize
                    | PARAM
                    | PARAM varsize"""
        if len(p) == 2 and p[1] == 'PARAM':
            p[0] = TreeNode('func_param', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif p[1] == 'PARAM':
            p[0] = TreeNode('func_param', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif len(p) == 2:
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

    # INITIALIZATION

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
        """init : const_expressions COMMA const_expression SEMICOLON
                    | const_expression SEMICOLON"""
        if len(p) == 3:
            p[0] = TreeNode('expression', children=[p[1]])
        else:
            p[0] = TreeNode('expressions', children=[p[1], p[3]])

    # EXPRESSIONS

    def p_const_expressions(self, p):
        """const_expressions : const_expressions COMMA const_expression
                        | const_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = TreeNode('const_expressions', children=[p[1], p[3]])

    def p_const_expression(self, p):
        """const_expression : const_math_expression
                        | const"""
        p[0] = TreeNode('const_expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

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

    def p_bool_expression(self, p):
        """bool_expression : bool_math_expression
                            | bool_const
                            | variant"""
        p[0] = TreeNode('bool_expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_string_expression(self, p):
        """string_expression : string_math_expression
                            | string_const
                            | variant"""
        p[0] = TreeNode('string_expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    # MATH EXPRESSIONS

    def p_math_expression(self, p):
        """math_expression : expression PLUS expression
                            | MINUS expression"""
        if len(p) == 3:
            p[0] = TreeNode('unar_op', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('bin_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_const_math_expression(self, p):
        """const_math_expression : const_expression PLUS const_expression
                            | MINUS const_expression"""
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
            p[0] = TreeNode('bin_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_bool_math_expression(self, p):
        """bool_math_expression : bool_expression PLUS bool_expression
                                | MINUS bool_expression"""
        if len(p) == 3:
            p[0] = TreeNode('unar_op', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('bin_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_string_math_expression(self, p):
        """string_math_expression : string_expression PLUS string_expression
                                        | MINUS string_expression"""
        if len(p) == 3:
            p[0] = TreeNode('unar_op', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('bin_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    # CONSTANTS

    def p_const(self, p):
        """const : TRUE
                | FALSE
                | DECIMAL
                | LETTERS"""
        p[0] = TreeNode('const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_decimal_const(self, p):
        """decimal_const : DECIMAL"""
        p[0] = TreeNode('decimal_const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_bool_const(self, p):
        """bool_const : TRUE
                        | FALSE"""
        p[0] = TreeNode('bool_const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_string_const(self, p):
        """string_const : LETTERS"""
        p[0] = TreeNode('string_const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    #

    def p_assignment(self, p):
        """assignment : variant ASSIGNMENT expression"""
        p[0] = TreeNode('assignment', value=p[1], children=p[3], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_convert(self, p):
        """convert : CONVERT type TO type variant"""
        p[0] = TreeNode('convert', value=[p[2], p[4]], children=p[5], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_digitize(self, p):
        """digitize : DIGITIZE variant"""
        p[0] = TreeNode('digitize', children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_type(self, p):
        """type : BOOL
                | DIGIT
                | STRING"""
        p[0] = p[1]

    def p_while(self, p):
        """while : WHILE bool_expression NEWLINE statements ENDW"""
        p[0] = TreeNode('while', children={'condition': p[2], 'body': p[4]}, lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_until(self, p):
        """until : UNTIL bool_expression NEWLINE statements ENDU"""
        p[0] = TreeNode('until', children={'condition': p[2], 'body': p[4]}, lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_if(self, p):
        """if : IFLESS decimal_expression COMMA decimal_expression NEWLINE statements ENDIF
              | IFNLESS decimal_expression COMMA decimal_expression NEWLINE statements ENDIF
              | IFZERO decimal_expression NEWLINE statements ENDIF
              | IFNZERO decimal_expression NEWLINE statements ENDIF
              | IFHIGH decimal_expression COMMA decimal_expression NEWLINE statements ENDIF
              | IFNHIGH decimal_expression COMMA decimal_expression NEWLINE statements ENDIF"""
        if len(p) == 6:
            p[0] = TreeNode('if', children={'condition': TreeNode('condition', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1)),
                                        'conditional_expressions': TreeNode('conditional_expressions', children=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2)),
                                            'body': p[4]}, lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('if', children={'condition': TreeNode('condition', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1)),
                                    'conditional_expressions': TreeNode('conditional_expressions', children=[p[2], p[4]], lineno=p.lineno(2), lexpos=p.lexpos(2)),
                                            'body': p[6]}, lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_command(self, p):
        """command : COMMAND string_expression"""
        p[0] = TreeNode('command', children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    # FUNCTIONS

    def p_func_body_statements(self, p):
        """func_body_statements : func_body_statements func_body_statement
                        | func_body_statement"""
        if len(p) == 2:
            p[0] = TreeNode('func_body_statement', children=p[1])
        else:
            p[0] = TreeNode('func_body_statements', children=[p[1], TreeNode('func_body_statement', children=p[2])])

    def p_func_body_statement(self, p):
        """func_body_statement : empty NEWLINE
                        | declaration NEWLINE
                        | assignment NEWLINE
                        | convert NEWLINE
                        | digitize NEWLINE
                        | while NEWLINE
                        | until NEWLINE
                        | if NEWLINE
                        | command NEWLINE
                        | statement_error NEWLINE
                        | function_call NEWLINE
                        | return NEWLINE"""
        p[0] = p[1]

    def p_function(self, p):
        """function : FUNC NAME func_body_statements ENDFUNC"""
        pass

    def p_function_call(self, p):
        pass

    def p_return(self, p):
        pass

    # SYNTAX ERRORS

    def p_decl_error(self, p):
        """declaration : VARIANT error
                        | VARIANT variant ASSIGNMENT error
                        | declaration error"""
        if len(p) == 3:
            p[0] = TreeNode('error', value='Declaration error', lineno=p.lineno(2), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in variant declaration\n')
        else:
            p[0] = TreeNode('error', value='Initialization error', lineno=p.lineno(2), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in variant initialization\n')

    def p_varsize_error(self, p):
        """varsize : LSQBRACKET error RSQBRACKET
                    | LSQBRACKET error COMMA decimal_expression RSQBRACKET
                    | LSQBRACKET decimal_expression COMMA error RSQBRACKET
                    | LSQBRACKET error COMMA error RSQBRACKET
                    | varsize error"""
        p[0] = TreeNode('error', value='Variant size/index error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in variant size/index!\n')

    def p_assignment_error(self, p):
        """assignment : variant ASSIGNMENT error"""
        p[0] = TreeNode('error', value='Assignment error', children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Assignment error!\n')

    def p_convert_error(self, p):
        """convert : CONVERT type TO type error
                    | CONVERT type TO error
                    | CONVERT type error
                    | CONVERT error
                    | convert error"""
        p[0] = TreeNode('error', value='Convertation error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in convertation!\n')

    def p_digitize_error(self, p):
        """digitize : DIGITIZE error
                    | digitize error"""
        p[0] = TreeNode('error', value='Digitize error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in digitize!\n')

    def p_command_error(self, p):
        """command : COMMAND error
                    | command error"""
        p[0] = TreeNode('error', value='Command error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in a command!\n')

    def p_statement_error(self, p):
        """statement_error : error
                            | statement_error error"""
        p[0] = TreeNode('error', value='Very plohaya error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in a whole line!\n')

    def p_error(self, p):
        try:
            sys.stderr.write(f'Error at {p.lineno} line\n')
        except:
            sys.stderr.write(f'Error\n')
        self.ok = False

data = ''' VARIANT param
'''
# lexer = Lexer()
# lexer.input(data)
# while True:
#     token = lexer.token()
#     if token is None:
#         break
#     else:
#         print(token)

parser = Parser()
tree, ok = parser.parse(data)
tree.print()
print(ok)

# a = x + COMMAND "UP DOWN LOOKUP"
# a = a + bcd + 12 + "letters" - что делать