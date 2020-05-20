squares = {
    ' ': 'EMPTY',
    'E': 'EXIT',
    'W': 'WALL'
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

    def move(self, direction):
        if direction == 'UP' and self.map[self.y - 1][self.x].type != 'WALL':
            self.y -= 1
            return True
        elif direction == 'DOWN' and self.map[self.y + 1][self.x].type != 'WALL':
            self.y += 1
            return True
        elif direction == 'LEFT' and self.map[self.y][self.x - 1].type != 'WALL':
            self.x -= 1
            return True
        elif direction == 'RIGHT' and self.map[self.y][self.x + 1].type != 'WALL':
            self.x += 1
            return True
        return False

    def exit(self):
        if self.map[self.y][self.x].type == 'EXIT':
            return True
        return False

    def look(self, direction):
        buf = 1
        if direction == 'LOOKUP':
            while self.map[self.y - buf][self.x].type == 'EMPTY':
                buf += 1
            if self.map[self.y - buf][self.x].type == 'WALL':
                return 'WALL', buf
            elif self.map[self.y - buf][self.x].type == 'EXIT':
                return 'EXIT', buf
        elif direction == 'LOOKDOWN':
            while self.map[self.y + buf][self.x].type == 'EMPTY':
                buf += 1
            if self.map[self.y + buf][self.x].type == 'WALL':
                return 'WALL', buf
            elif self.map[self.y + buf][self.x].type == 'EXIT':
                return 'EXIT', buf
        elif direction == 'LOOKLEFT':
            while self.map[self.y][self.x - buf].type == 'EMPTY':
                buf += 1
            if self.map[self.y][self.x - buf].type == 'WALL':
                return 'WALL', buf
            elif self.map[self.y][self.x - buf].type == 'EXIT':
                return 'EXIT', buf
        elif direction == 'LOOKRIGHT':
            while self.map[self.y][self.x + buf].type == 'EMPTY':
                buf += 1
            if self.map[self.y][self.x + buf].type == 'WALL':
                return 'WALL', buf
            elif self.map[self.y][self.x + buf].type == 'EXIT':
                return 'EXIT', buf