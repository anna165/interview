import pygame
import random
import sqlite3

# Инициализация Pygame
pygame.init()

# Определение цветов
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Определение констант
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
FONT_SIZE = 30

# Создание окна игры
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Игра")

# Открытие файла для записи логов
log_file = open("log.txt", "w")

# Определение базы данных SQLite3
conn = sqlite3.connect("highscores.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS highscores (name text, score integer)")

# Класс для главного персонажа
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        # Обновление положения игрока в зависимости от нажатых клавиш
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_UP]:
            self.rect.y -= 5
        if keys[pygame.K_DOWN]:
            self.rect.y += 5

# Класс для врагов
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([ENEMY_WIDTH, ENEMY_HEIGHT])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
        self.rect.y = -ENEMY_HEIGHT

    def update(self):
        # Обновление положения врага
        self.rect.y += 5

# Класс для текста
class Text(pygame.sprite.Sprite):
    def __init__(self, text, x, y):
        super().__init__()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.image = self.font.render(text, True, WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Запрос имени пользователя
player_name = input("Введите ваш никнейм: ")

# Создание групп спрайтов
all_sprites_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# Создание игрока
player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_HEIGHT)
all_sprites_group.add(player)

# Создание текстовых объектов
score_text = Text("Score: 0", 10, 10)
all_sprites_group.add(score_text)
game_over_text = Text("Game Over", SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2)
you_win_text = Text("You Win!", SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2)

# Инициализация переменных
score = 0
game_over = False
you_win = False

# Основной игровой цикл
clock = pygame.time.Clock()
while not game_over and not you_win:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

    # Создание новых врагов
    if random.randint(1, 100) == 1:
        enemy = Enemy()
        all_sprites_group.add(enemy)
        enemy_group.add(enemy)

    # Обработка столкновений игрока с врагами
    enemy_hits = pygame.sprite.spritecollide(player, enemy_group, False)
    for enemy in enemy_hits:
        game_over = True
        log_file.write(player_name + " проиграл, счет: " + str(score) + "\n")
        c.execute("INSERT INTO highscores VALUES ('" + player_name + "', " + str(score) + ")")
        conn.commit()

    # Обновление спрайтов
    all_sprites_group.update()

    # Удаление врагов, вышедших за экран
    for enemy in enemy_group:
        if enemy.rect.y > SCREEN_HEIGHT:
            enemy.kill()

    # Прибавление очков за уничтоженных врагов
    for enemy in enemy_group:
        if enemy.rect.y > SCREEN_HEIGHT - ENEMY_HEIGHT:
            score += 1
            enemy.kill()
            log_file.write(player_name + " получил 1 очко, счет: " + str(score) + "\n")
            score_text.image = score_text.font.render("Score: " + str(score), True, WHITE)

    # Проверка на победу
    if score >= 10:
        you_win = True
        log_file.write(player_name + " выиграл, счет: " + str(score) + "\n")
        c.execute("INSERT INTO highscores VALUES ('" + player_name + "', " + str(score) + ")")
        conn.commit()

    # Отрисовка спрайтов на экране
    screen.fill(BLACK)
    all_sprites_group.draw(screen)
    if game_over:
        all_sprites_group.add(game_over_text)
        all_sprites_group.remove(score_text)
    if you_win:
        all_sprites_group.add(you_win_text)
        all_sprites_group.remove(score_text)
    pygame.display.flip()

    # Ограничение FPS
    clock.tick(60)

# Закрытие файла для записи логов и базы данных SQLite3
log_file.close()
conn.close()

# Вывод топ-5 игроков
conn = sqlite3.connect("highscores.db")
c = conn.cursor()
c.execute("SELECT * FROM highscores ORDER BY score DESC LIMIT 5")
highscores = c.fetchall()
print("Топ-5 игроков:")
for row in highscores:
    print(row[0], row[1])
conn.close()

# Завершение Pygame
pygame.quit()