# game code goes here
from PIL import Image, ImageDraw
import random


COLORS = {"FOOD": (255, 0, 0), "WALL": (0, 255, 255), "NONE": (0, 0, 0)}


class Game:
    def __init__(self, cols, rows, max_steps):
        self.board = Board(cols, rows)
        self.players = []
        self.max_steps = max_steps

    def setup(self, n):
        self.players = []
        for i in range(n):
            snake = self.spawn_snake()
            self.players.append(SnakePlayer(snake, self.board))
            self.spawn_food()

    def spawn_snake(self):
        x, y = random.randint(0, self.board.getCols() - 1), random.randint(
            0, self.board.getRows() - 1
        )
        while self.board.getCell(x, y) != "NONE":
            x, y = random.randint(0, self.board.getCols() - 1), random.randint(
                0, self.board.getRows() - 1
            )

        self.board.setWall(x, y)
        return Snake(x, y)

    def spawn_food(self):
        x, y = random.randint(0, self.board.getCols() - 1), random.randint(
            0, self.board.getRows() - 1
        )
        while self.board.getCell(x, y) != "NONE":
            x, y = random.randint(0, self.board.getCols() - 1), random.randint(
                0, self.board.getRows() - 1
            )
        self.board.setFood(x, y)

    def run(self):
        for step in range(self.max_steps):
            for player in self.players:
                move = player.make_move()

                # calculate future cell
                x, y = player.snake.get_head()
                if move == "UP":
                    y += 1
                elif move == "DOWN":
                    y -= 1
                elif move == "LEFT":
                    x -= 1
                elif move == "RIGHT":
                    x += 1

                # check if it's an wrap around
                x %= self.board.getCols() - 1
                y %= self.board.getRows() - 1

                if self.board.getCell(x, y) == "FOOD":
                    player.snake.move(x, y, eat=True)
                    self.board.setWall(x, y)
                    self.spawn_food()

                elif self.board.getCell(x, y) == "WALL":
                    for xx, yy in player.snake.body:
                        self.board.setNone(xx, yy)
                    self.players.remove(player)

                elif self.board.getCell(x, y) == "NONE":
                    if player.snake.grow > 0:
                        player.snake.move(x, y, eat=True)
                        self.board.setWall(x, y)
                        player.snake.grow -= 1
                    else:
                        tailx, taily = player.snake.move(x, y)
                        self.board.setWall(x, y)
                        self.board.setNone(tailx, taily)
            yield self.board


class SnakePlayer:
    def __init__(self, snake, board):
        self.snake = snake
        self.board = board
        self.brain_walls = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 16, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 17, 18, 17, 1, 1, 0, 0],
            [0, 0, 1, 17, 19, 200, 19, 17, 1, 0, 0],
            [0, 0, 16, 18, 200, 0, 200, 18, 16, 0, 0],
            [0, 0, 1, 17, 19, 200, 19, 17, 1, 0, 0],
            [0, 0, 1, 1, 17, 18, 17, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 16, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        self.brain_food = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

    def make_move(self):
        options = {"UP": 0, "DOWN": 0, "LEFT": 0, "RIGHT": 0}
        headx, heady = self.snake.get_head()

        for i in range(11):
            for j in range(11):
                mental_x = (headx - 5 + j) % (self.board.getCols() - 1)
                mental_y = (heady + 5 - i) % (self.board.getRows() - 1)

                if self.board.getCell(mental_x, mental_y) == "WALL":
                    if j < 5:
                        options["LEFT"] += self.brain_walls[i][j]
                    if j > 5:
                        options["RIGHT"] += self.brain_walls[i][j]
                    if i > 5:
                        options["DOWN"] += self.brain_walls[i][j]
                    if i < 5:
                        options["UP"] += self.brain_walls[i][j]

                if self.board.getCell(mental_x, mental_y) == "FOOD":
                    if j < 5:
                        options["LEFT"] -= self.brain_food[i][j]
                    if j > 5:
                        options["RIGHT"] -= self.brain_food[i][j]
                    if i > 5:
                        options["DOWN"] -= self.brain_food[i][j]
                    if i < 5:
                        options["UP"] -= self.brain_food[i][j]

        m = options[min(options, key=lambda x: options[x])]
        choices = []
        for each in options:
            if options[each] == m:
                choices.append(each)
        return random.choice(choices)


class Snake:
    def __init__(self, x, y):
        self.body = [(x, y)]
        self.grow = 3

    def move(self, x, y, eat=False):
        self.body.insert(0, (x, y))
        if not eat:
            return self.body.pop()
        return None

    def get_head(self):
        return self.body[0]


# Board class will just keep track of the board
class Board:
    blocks = {"FOOD", "WALL", "NONE"}

    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.grid = [["NONE" for j in range(cols)] for i in range(rows)]

    def getRows(self):
        return self.rows

    def getCols(self):
        return self.cols

    def setWall(self, x, y):
        self.grid[y][x] = "WALL"

    def setFood(self, x, y):
        self.grid[y][x] = "FOOD"

    def setNone(self, x, y):
        self.grid[y][x] = "NONE"

    def getCell(self, x, y):
        return self.grid[y][x]

    def clear(self):
        self.grid = [["NONE" for j in range(self.cols)] for i in range(self.rows)]


# res - resolution: (widthpx, heightpx)
# board - boardObject
# returns image object
def renderBoard(board, res, name=None, gridLine=0):

    width, height = res
    # init all pixels to be black
    pixels = [[(255, 255, 255) for j in range(width)] for i in range(height)]

    rows = board.getRows()
    cols = board.getCols()

    cell_w = (width - (gridLine * cols + gridLine)) // cols
    cell_h = (height - (gridLine * rows + gridLine)) // rows

    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    for row in range(rows):
        for col in range(cols):
            x_coord = col * (cell_w + gridLine) + gridLine
            y_coord = row * (cell_h + gridLine) + gridLine
            draw.rectangle(
                (x_coord + 1, y_coord + 1, x_coord + cell_w - 1, y_coord + cell_h - 1),
                fill=COLORS[board.getCell(col, row)],
            )

    return img


if __name__ == "__main__":

    game = Game(160, 90, 500)

    game.setup(50)
    frames = []
    step = 0
    for board in game.run():
        print(step)
        step += 1
        frames.append(renderBoard(board, (1920, 1080)))

    frames[0].save(
        "images/game.gif",
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=1,
        loop=0,
    )
