import pygame
import os
import random

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mario Level")

black = (0, 0, 0)
white = (255, 255, 255)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        exit()
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


grass_image = load_image("grass.png")
box_image = load_image("box.png")
mario_image = load_image("mar.png", -1)
fon_image = load_image("fon.jpg")

tile_size = grass_image.get_width()


class Board:
    def __init__(self, width, height, level_data):
        self.width = width
        self.height = height
        self.level_data = level_data
        self.board = [[0] * width for _ in range(height)]
        self.left = 0
        self.top = 0
        self.cell_size = tile_size
        self.board = self.create_board()

    def create_board(self):
        board = []
        for row in self.level_data:
            board_row = []
            for cell in row:
                board_row.append(cell)
            board.append(board_row)
        return board

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        x, y = self.left, self.top
        for row_index, row in enumerate(self.board):
            for col_index, cell in enumerate(row):
                rect = (x, y, self.cell_size, self.cell_size)
                if cell == '#':
                    screen.blit(box_image, rect)
                elif cell == '.':
                    screen.blit(grass_image, rect)
                x += self.cell_size
            y += self.cell_size
            x = self.left

    def get_cell(self, mouse_pos):
        if mouse_pos[0] < self.left or mouse_pos[0] > self.left + self.cell_size * len(self.board[0]):
            return None
        if mouse_pos[1] < self.top or mouse_pos[1] > self.top + self.cell_size * len(self.board):
            return None

        x = (mouse_pos[0] - self.left) // self.cell_size
        y = (mouse_pos[1] - self.top) // self.cell_size
        return (x, y)

    def on_click(self, cell_coords):
        pass

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def is_valid_move(self, row, col):
        if 0 <= row < len(self.board) and 0 <= col < len(self.board[0]):
            return self.board[row][col] == '.'
        return False

    def get_cell_coords(self, row, col):
        x = col * self.cell_size + self.left
        y = row * self.cell_size + self.top
        return x, y


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, board):
        super().__init__()
        self.image = mario_image
        self.rect = self.image.get_rect()
        self.board = board
        self.row = y
        self.col = x
        self.update_rect()
        self.inited = True
        self.can_move = True

    def update_rect(self):
        x, y = self.board.get_cell_coords(self.row, self.col)
        self.rect.x = x + (self.board.cell_size - self.rect.width) // 2
        self.rect.y = y + (self.board.cell_size - self.rect.height) // 2

    def update(self, events):
        if self.can_move:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move(1, 0)
                    elif event.key == pygame.K_UP:
                        self.move(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.move(0, 1)

    def move(self, dx, dy):
        new_row = self.row + dy
        new_col = self.col + dx

        if self.board.is_valid_move(new_row, new_col):
            self.row = new_row
            self.col = new_col
            self.update_rect()
            self.can_move = False


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return [list(row.ljust(max_width, '.')) for row in level_map]


def find_free_coordinates(level):
    free_coords = []
    for row_index, row in enumerate(level):
        for col_index, cell in enumerate(row):
            if cell == '.':
                free_coords.append((col_index, row_index))
    return free_coords


level_data = load_level("level.txt")

board = Board(len(level_data[0]), len(level_data), level_data)

free_coordinates = find_free_coordinates(level_data)

player = None
if free_coordinates:
    start_col, start_row = random.choice(free_coordinates)
    player = Player(start_col, start_row, board)
else:
    player = Player(0, 0, board)

all_sprites = pygame.sprite.Group()

if player:
    all_sprites.add(player)

running = True
clock = pygame.time.Clock()

fon_image = pygame.transform.scale(fon_image, (screen_width, screen_height))

game_state = "menu"


def draw_menu():
    screen.blit(fon_image, (0, 0))
    font = pygame.font.Font(None, 74)
    text = font.render("Mario Game", True, white)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(text, text_rect)

    font = pygame.font.Font(None, 48)
    text = font.render("Press ENTER to start", True, white)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text, text_rect)

    pygame.display.flip()


while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_RETURN:
                    game_state = "game"
                    free_coordinates = find_free_coordinates(level_data)
                    if free_coordinates:
                        start_col, start_row = random.choice(free_coordinates)
                        player = Player(start_col, start_row, board)
                        all_sprites.empty()
                        all_sprites.add(player)
                    else:
                        player = Player(0, 0, board)
                        all_sprites.empty()
                        all_sprites.add(player)
        if event.type == pygame.KEYUP:
            if player:
                player.can_move = True

    if game_state == "menu":
        draw_menu()
    elif game_state == "game":
        if player and player.inited:
            player.update(events)
            screen.blit(fon_image, (0, 0))
            board.render(screen)
            all_sprites.draw(screen)
            pygame.display.flip()

    clock.tick(60)

pygame.quit()
