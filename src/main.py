import pygame
import os
import random
import sys

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
VISIBLE_CELLS = 8  # Размер видимой области 8x8


class Board:
    def __init__(self, width, height, level_data):
        self.width = width
        self.height = height
        self.level_data = level_data
        self.board = [[0] * width for _ in range(height)]
        self.cell_size = tile_size
        self.board = self.create_board()

    def create_board(self):
        return [[cell for cell in row] for row in self.level_data]

    def render(self, screen, camera):
        start_x = max(0, camera.offset_x)
        start_y = max(0, camera.offset_y)
        end_x = min(self.width, start_x + VISIBLE_CELLS)
        end_y = min(self.height, start_y + VISIBLE_CELLS)

        for row in range(start_y, end_y):
            for col in range(start_x, end_x):
                rect_x = (col - camera.offset_x) * self.cell_size
                rect_y = (row - camera.offset_y) * self.cell_size
                rect = (rect_x, rect_y, self.cell_size, self.cell_size)

                if self.board[row][col] == '#':
                    screen.blit(box_image, rect)
                elif self.board[row][col] == '.':
                    screen.blit(grass_image, rect)

    def is_valid_move(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width and self.board[row][col] == '.'


class Camera:
    def __init__(self, board):
        self.board = board
        self.offset_x = 0
        self.offset_y = 0

    def update(self, player):
        self.offset_x = max(0, min(player.col - VISIBLE_CELLS // 2, self.board.width - VISIBLE_CELLS))
        self.offset_y = max(0, min(player.row - VISIBLE_CELLS // 2, self.board.height - VISIBLE_CELLS))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, board):
        super().__init__()
        self.image = mario_image
        self.rect = self.image.get_rect()
        self.board = board
        self.row = y
        self.col = x
        self.update_rect()
        self.can_move = True

    def update_rect(self):
        screen_x = (self.col - camera.offset_x) * self.board.cell_size
        screen_y = (self.row - camera.offset_y) * self.board.cell_size
        self.rect.x = screen_x + (self.board.cell_size - self.rect.width) // 2
        self.rect.y = screen_y + (self.board.cell_size - self.rect.height) // 2

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
            camera.update(self)


def load_level(filename):
    filename = "data/" + filename
    if not os.path.exists(filename):
        print(f"Файл уровня '{filename}' не найден")
        return None
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        max_width = max(map(len, level_map))
        return [list(row.ljust(max_width, '.')) for row in level_map]
    except Exception:
        print(f"Не удалось обработать файл '{filename}'")
        return None


def find_free_coordinates(level):
    return [(col, row) for row in range(len(level)) for col in range(len(level[row])) if level[row][col] == '.']


while True:
    level_filename = input("Введите имя файла уровня (например, level1.txt): ")
    level_data = load_level(level_filename)
    if level_data:
        break
    print("Неверное имя файла или некорректный формат уровня. Попробуйте еще раз.")

board = Board(len(level_data[0]), len(level_data), level_data)
camera = Camera(board)

free_coordinates = find_free_coordinates(level_data)
player = Player(*random.choice(free_coordinates), board) if free_coordinates else Player(0, 0, board)
camera.update(player)

all_sprites = pygame.sprite.Group(player)

running = True
clock = pygame.time.Clock()
fon_image = pygame.transform.scale(fon_image, (screen_width, screen_height))
game_state = "menu"


def draw_menu():
    screen.blit(fon_image, (0, 0))
    font = pygame.font.Font(None, 74)
    text = font.render("Mario Game", True, white)
    screen.blit(text, text.get_rect(center=(screen_width // 2, screen_height // 3)))

    font = pygame.font.Font(None, 48)
    text = font.render("Press ENTER to start", True, white)
    screen.blit(text, text.get_rect(center=(screen_width // 2, screen_height // 2)))

    pygame.display.flip()


while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_state == "menu":
            if event.key == pygame.K_RETURN:
                game_state = "game"
                player = Player(*random.choice(free_coordinates), board) if free_coordinates else Player(0, 0, board)
                camera.update(player)
                all_sprites.empty()
                all_sprites.add(player)
        if event.type == pygame.KEYUP and player:
            player.can_move = True

    if game_state == "menu":
        draw_menu()
    elif game_state == "game":
        player.update(events)
        screen.blit(fon_image, (0, 0))
        board.render(screen, camera)
        all_sprites.draw(screen)
        pygame.display.flip()

    clock.tick(60)

pygame.quit()
