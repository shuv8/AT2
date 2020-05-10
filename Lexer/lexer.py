import sys
import ply.lex as lex

reserved = {
    'VARIANT': 'VARIANT',

    #bool
    'TRUE': 'TRUE',
    'FALSE': 'FALSE',

    #convert
    'CONVERT': 'CONVERT',
    'DIGITIZE': 'DIGITIZE',
    'BOOL': 'BOOL',
    'DIGIT': 'DIGIT',
    'STRING': 'STRING',
    'TO': 'TO',

    #cycle
    'WHILE': 'WHILE',
    'ENDW': 'ENDW',
    'UNTIL': 'UNTIL',
    'ENDU': 'ENDU',

    #if
    'IFLESS': 'IFLESS',
    'IFNLESS': 'IFNLESS',
    'IFZERO': 'IFZERO',
    'IFNZERO': 'IFNZERO',
    'IFHIGH': 'IFHIGH',
    'IFNHIGH': 'IFNHIGH',
    'ENDIF': 'ENDIF',

    #robot
    'COMMAND': 'COMMAND',

    #function
    'FUNC': 'FUNC',
    'RETURN': 'RETURN',
    'PARAM': 'PARAM',
    'ENDFUNC': 'ENDFUNC',
    'CALL': 'CALL',
}


class Lexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = ['DECIMAL', 'NAME', 'ASSIGNMENT',
              'PLUS', 'MINUS',
              'LETTERS', 'LBRACE', 'RBRACE',
              'LSQBRACKET', 'RSQBRACKET',
              'COMMA', 'SEMICOLON', 'NEWLINE'
    ] + list(reserved.values())

    t_ASSIGNMENT = r'\='
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LSQBRACKET = r'\['
    t_RSQBRACKET = r'\]'
    t_COMMA = r'\,'
    t_SEMICOLON = r'\;'
    t_ignore =' '

    def t_DECIMAL(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_LETTERS(self, t):
        r'\"[^\"]*\"'
        t.type = reserved.get(t.value, 'LETTERS')
        t.value = str(t.value).strip('\"')
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'NAME')
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t):
        sys.stderr.write(f'Illegal character: {t.value[0]} at line {t.lexer.lineno}\n')
        t.lexer.skip(1)

    def input(self, data):
        return self.lexer.input(data)

    def token(self):
        return self.lexer.token()


# data = '''FUNC function
# VARIANT a = {{12, "zhma", "lol", TRUE;}}
# VARIANT b
# VARIANT c
# IFNHIGH PARAM, 1
# RETURN 1
# ENDIF
# a = PARAM
# b = CALL factorial PARAM + -1
# c = b
# WHILE a + -1
# c = c + b
# a = a + -1
# ENDW
# RETURN c
# ENDFUNC
#
# VARIANT a [2, 1]
# a = CALL factorial 6
# '''
# lexer = Lexer()
# lexer.input(data)
# while True:
#     token = lexer.token()
#     if token is None:
#         break
#     else:
#         print(token)
