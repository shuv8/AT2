squares = {
    ' ': 'EMPTY',
    'e': 'EXIT',
    'w': 'WALL'
}

look = {
    '0': 'up',
    '1': 'down',
    '2': 'left',
    '3': 'right'
}

class Square:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return f'{self.type}'


class Robot:
    def __init__(self, x, y, map):
        self.x = x
        self.y = y
        self.map = map

    def __repr__(self):
        return f'X = {self.x}, Y = {self.y}\n'

    def show(self):
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if i == self.x and j == self.x:
                    print('ROBOT', end='  ')
                else:
                    print(self.map[i][j].type, end='  ')
            print()