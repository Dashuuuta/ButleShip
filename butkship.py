from turtle import color
import pygame
import sys

# Константы
GRID_SIZE = 10
CELL_SIZE = 40
MARGIN = 45
WIDTH = GRID_SIZE * CELL_SIZE * 2 + MARGIN * 6 # Ширина окна (для двух полей)
HEIGHT = GRID_SIZE * CELL_SIZE + MARGIN * 4 + 50  # Высота окна (с кнопками и отступами)
FPS = 30

# Состояния клеток
EMPTY = 0
SHIP = 1
MISS = -1
HIT = 2

# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BUTTON_COLOR = (100, 149, 237)
ORANGE = (255, 140, 0)

class Button:
    def __init__(self, text, x, y, width, height, action=None, color=BUTTON_COLOR):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.font = pygame.font.Font(None, 36)
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        text_surface = self.font.render(self.text, True, WHITE)
        surface.blit(
            text_surface,
            (
                self.rect.centerx - text_surface.get_width() // 2,
                self.rect.centery - text_surface.get_height() // 2,
            ),
        )

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.action:
            self.action()

class Grid:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def draw(self, surface, offset_x, show_ships):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(
                    MARGIN + offset_x + y * CELL_SIZE,
                    MARGIN + x * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                pygame.draw.rect(surface, GRAY, rect, 1)

                if self.grid[x][y] == MISS:
                    pygame.draw.circle(surface, BLUE, rect.center, CELL_SIZE // 4)
                elif self.grid[x][y] == HIT:
                    pygame.draw.circle(surface, RED, rect.center, CELL_SIZE // 4)
                elif show_ships and self.grid[x][y] == SHIP:
                    pygame.draw.rect(surface, (255, 140, 0), rect)

    def place_ship(self, x, y, length, horizontal):
        if horizontal:
            if y + length > GRID_SIZE or any(self.grid[x][y + i] != EMPTY for i in range(length)):
                return False
            for i in range(length):
                self.grid[x][y + i] = SHIP
        else:
            if x + length > GRID_SIZE or any(self.grid[x + i][y] != EMPTY for i in range(length)):
                return False
            for i in range(length):
                self.grid[x + i][y] = SHIP
        return True

    def shoot(self, x, y):
        if self.grid[x][y] == SHIP:
            self.grid[x][y] = HIT
            return True
        elif self.grid[x][y] == EMPTY:
            self.grid[x][y] = MISS
            return False
        return False

    def check_victory(self):
        return all(cell != SHIP for row in self.grid for cell in row)

class BattleshipGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Морской бой")
        self.clock = pygame.time.Clock()

        self.start_button = Button("Начать игру", WIDTH // 2 - 100, HEIGHT - 100, 200, 40, self.start_game, color=(169, 169, 169))  # Темно-серый
        self.exit_button = Button("Выйти из игры", WIDTH // 2 - 100, HEIGHT - 50, 200, 40, self.exit_game, color=(169, 169, 169))  # Темно-серый

        self.reset_button = Button("Заново", WIDTH // 2 - 100, HEIGHT - 50, 200, 40, self.reset_game, color=(139, 69, 19))  # Темно-серый цвет
        self.replay_button = Button("Играть снова", WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 40, self.reset_game, color=(169, 169, 169))  # Темно-серый цвет


        self.running = False
        self.player1_grid = Grid()
        self.player2_grid = Grid()
        self.active_grid = None

        self.placing_phase = False
        self.ships_to_place = []
        self.current_ship = None
        self.horizontal = True
        self.player_turn = 1

        self.game_over = False
        self.winner = None

    def start_game(self):
        self.running = True
        self.reset_game()

    def reset_game(self):
        self.player1_grid = Grid()
        self.player2_grid = Grid()
        self.active_grid = self.player1_grid
        self.placing_phase = True
        self.ships_to_place = [4, 3, 2, 1]
        self.current_ship = self.ships_to_place.pop(0)
        self.player_turn = 1
        self.game_over = False
        self.winner = None

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.horizontal = not self.horizontal
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.game_over:
                    self.replay_button.check_click(pos)
                elif not self.running:
                    self.start_button.check_click(pos)
                    self.exit_button.check_click(pos)
                else:
                    self.reset_button.check_click(pos)

                    mx, my = pos
                    if mx < WIDTH // 2:
                        # Координаты для первого игрока
                        grid_x = (my - MARGIN) // CELL_SIZE
                        grid_y = (mx - MARGIN) // CELL_SIZE
                        if self.placing_phase:
                            if (
                                0 <= grid_x < GRID_SIZE
                                and 0 <= grid_y < GRID_SIZE
                                and self.active_grid.place_ship(grid_x, grid_y, self.current_ship, self.horizontal)
                            ):
                                if self.ships_to_place:
                                    self.current_ship = self.ships_to_place.pop(0)
                                else:
                                    if self.active_grid == self.player1_grid:
                                        self.active_grid = self.player2_grid
                                        self.ships_to_place = [4, 3, 2, 1]
                                        self.current_ship = self.ships_to_place.pop(0)
                                    else:
                                        self.placing_phase = False
                        else:
                            self.process_shot(grid_x, grid_y, mx)
                    else:
                        # Координаты для второго игрока
                        grid_x = (my - MARGIN) // CELL_SIZE
                        grid_y = (mx - (WIDTH // 2 + MARGIN)) // CELL_SIZE
                        if self.placing_phase:
                            if (
                                0 <= grid_x < GRID_SIZE
                                and 0 <= grid_y < GRID_SIZE
                                and self.active_grid.place_ship(grid_x, grid_y, self.current_ship, self.horizontal)
                            ):
                                if self.ships_to_place:
                                    self.current_ship = self.ships_to_place.pop(0)
                                else:
                                    if self.active_grid == self.player1_grid:
                                        self.active_grid = self.player2_grid
                                        self.ships_to_place = [4, 3, 2, 1]
                                        self.current_ship = self.ships_to_place.pop(0)
                                    else:
                                        self.placing_phase = False
                        else:
                            self.process_shot(grid_x, grid_y, mx)  # Логика игры во время матча
    def process_shot(self, grid_x, grid_y, mx):
        if self.player_turn == 1:
            grid_y = (mx - (WIDTH // 2 + MARGIN)) // CELL_SIZE
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                if self.player2_grid.shoot(grid_x, grid_y):
                    if self.player2_grid.check_victory():
                        self.winner = "Игрок 1"
                        self.game_over = True
                        self.player_turn = None
                    # Если попали в корабль, продолжаем ходить
                    else:
                        self.player_turn = 1
                else:
                    self.player_turn = 2
        elif self.player_turn == 2:
            grid_y = (mx - MARGIN) // CELL_SIZE
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                if self.player1_grid.shoot(grid_x, grid_y):
                    if self.player1_grid.check_victory():
                        self.winner = "Игрок 2"
                        self.game_over = True
                        self.player_turn = None
                    # Если попали в корабль, продолжаем ходить
                    else:
                        self.player_turn = 2
                else:
                    self.player_turn = 1

    def draw_menu(self):
        self.screen.fill(WHITE)

        # Отображение названия игры
        font = pygame.font.SysFont("comicsansms", 48)
        title_surface = font.render("Морской бой", True, BLACK)
        self.screen.blit(
            title_surface, 
            (WIDTH // 2 - title_surface.get_width() // 2, HEIGHT // 4)
        )

        self.start_button.draw(self.screen)
        self.exit_button.draw(self.screen)

        pygame.display.flip()

    def draw_game(self):
        self.screen.fill(WHITE)
        if self.game_over:
            font = pygame.font.Font(None, 48)
            text_surface = font.render(f"{self.winner} победил!", True, BLACK)
            self.screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - 50))
            self.replay_button.draw(self.screen)
        else:
            if not self.running:
                self.start_button.draw(self.screen)
                self.exit_button.draw(self.screen)
            else:
                if self.placing_phase:
                    text = f"Игрок {1 if self.active_grid == self.player1_grid else 2}: Размещайте корабль длиной {self.current_ship}"
                else:
                    text = f"Ход игрока {self.player_turn}"

                font = pygame.font.Font(None, 36)
                text_surface = font.render(text, True, BLACK)
                self.screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 10))

                self.player1_grid.draw(self.screen, 0, self.placing_phase or self.player_turn == 1)
                self.player2_grid.draw(self.screen, WIDTH // 2 + MARGIN, self.placing_phase or self.player_turn == 2)

                self.reset_button.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()

            if not self.running:
                self.draw_menu()
            else:
                self.draw_game()

            self.clock.tick(FPS)

if __name__ == "__main__":
    game = BattleshipGame()
    game.run()