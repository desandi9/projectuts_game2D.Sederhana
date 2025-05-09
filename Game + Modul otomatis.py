import subprocess
import sys

# Otomatis install pygame jika belum ada
try:
    import pygame
except ImportError:
    print("pygame belum terpasang. Menginstall pygame...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

import random

# Inisialisasi
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Dodger Adventure")
clock = pygame.time.Clock()

# Font
try:
    FONT = pygame.font.Font("Montserrat-Regular.ttf", 28)
except:
    FONT = pygame.font.SysFont("Arial", 28)

# Warna
SKY_TOP = (10, 15, 80)
SKY_BOTTOM = (25, 40, 120)
MOON = (255, 255, 255)
STAR = (255, 255, 255)
GRASS = (20, 40, 100)
SHADOW = (0, 0, 30)
PLAYER_COLORS = [(255, 255, 0), (255, 0, 0)]
BLOCK_COLORS = [(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)) for _ in range(10)]

# Bulan
moon_y = 450
moon_direction = -0.05

# Player class
class Player:
    def __init__(self, x, y, color, controls):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.color = color
        self.controls = controls
        self.speed = 5
        self.moving = False

    def move(self, keys):
        self.moving = False
        if keys[self.controls['up']]:
            self.rect.y -= self.speed
            self.moving = True
        if keys[self.controls['down']]:
            self.rect.y += self.speed
            self.moving = True
        if keys[self.controls['left']]:
            self.rect.x -= self.speed
            self.moving = True
        if keys[self.controls['right']]:
            self.rect.x += self.speed
            self.moving = True
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self, surface):
        flash_color = (255, 255, 255) if self.moving else self.color
        pygame.draw.ellipse(surface, flash_color, self.rect)

# Objek jatuh
class FallingShape:
    def __init__(self, speed):
        self.x = random.randint(20, WIDTH - 20)
        self.y = -50
        self.size = random.randint(20, 40)
        self.shape = random.choice(["circle", "rect", "triangle"])
        self.color = random.choice(BLOCK_COLORS)
        self.speed = speed

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        if self.shape == "circle":
            pygame.draw.circle(surface, self.color, (self.x, self.y), self.size // 2)
        elif self.shape == "rect":
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))
        elif self.shape == "triangle":
            points = [
                (self.x, self.y),
                (self.x - self.size // 2, self.y + self.size),
                (self.x + self.size // 2, self.y + self.size),
            ]
            pygame.draw.polygon(surface, self.color, points)

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y, self.size, self.size)

# Background
def draw_background():
    global moon_y
    for i in range(HEIGHT):
        ratio = i / HEIGHT
        r = SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio
        g = SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio
        b = SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio
        pygame.draw.line(screen, (int(r), int(g), int(b)), (0, i), (WIDTH, i))

    # Bulan tenggelam
    pygame.draw.circle(screen, MOON, (WIDTH // 2, int(moon_y)), 60)
    moon_y += moon_direction
    if moon_y < HEIGHT - 90:
        moon_y = HEIGHT - 90

    # Bintang
    for _ in range(40):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT // 2)
        pygame.draw.circle(screen, STAR, (x, y), 1)

    # Bukit
    pygame.draw.ellipse(screen, GRASS, (-200, 400, 800, 300))
    pygame.draw.ellipse(screen, GRASS, (200, 430, 800, 300))

    # Pohon
    for x in [150, 300, 650]:
        pygame.draw.polygon(screen, SHADOW, [(x+20, 500), (x+40, 460), (x+60, 500)])
        pygame.draw.polygon(screen, (30, 30, 60), [(x, 500), (x+20, 440), (x+40, 500)])

# Teks
def draw_text(text, size, color, x, y, center=True):
    try:
        font = pygame.font.Font("Montserrat-Regular.ttf", size)
    except:
        font = pygame.font.SysFont("Arial", size)
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y) if center else (x, y))
    screen.blit(surface, rect)

# Game utama
def game_loop(num_players):
    global moon_y
    moon_y = 450

    players = [
        Player(200, 500, PLAYER_COLORS[0], {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d})
    ]
    if num_players == 2:
        players.append(Player(500, 500, PLAYER_COLORS[1], {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}))

    shapes = []
    speed = 4
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    start_time = pygame.time.get_ticks()

    while True:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT:
                shapes.append(FallingShape(speed))

        elapsed = (pygame.time.get_ticks() - start_time) // 1000
        if elapsed % 10 == 0 and elapsed > 0:
            speed += 0.02

        draw_background()
        for shape in shapes:
            shape.move()
            shape.draw(screen)

        for player in players:
            player.move(keys)
            player.draw(screen)

        for player in players:
            for shape in shapes:
                if player.rect.colliderect(shape.get_rect()):
                    return

        pygame.display.flip()
        clock.tick(60)

# Menu utama
def menu():
    selected_option = 0
    pygame.key.set_repeat(200, 100)

    while True:
        draw_background()

        draw_text("Block Dodger Adventure", 48, MOON, WIDTH // 2, 120)

        # Desain tombol mirip gambar
        button_width, button_height = 180, 100
        spacing = 60
        x1 = WIDTH // 2 - button_width - spacing // 2
        x2 = WIDTH // 2 + spacing // 2
        y = 250

        one_color = (255, 70, 70) if selected_option == 0 else (100, 100, 150)
        two_color = (70, 200, 255) if selected_option == 1 else (100, 100, 150)

        pygame.draw.rect(screen, one_color, (x1, y, button_width, button_height), border_radius=15)
        draw_text("1", 40, (255, 255, 255), x1 + button_width // 2, y + 30)
        draw_text("PLAYER", 22, (255, 255, 255), x1 + button_width // 2, y + 70)

        pygame.draw.rect(screen, two_color, (x2, y, button_width, button_height), border_radius=15)
        draw_text("2", 40, (255, 255, 255), x2 + button_width // 2, y + 30)
        draw_text("PLAYERS", 22, (255, 255, 255), x2 + button_width // 2, y + 70)

        draw_text("Gunakan ↑ ↓ untuk memilih, Enter untuk mulai", 24, MOON, WIDTH // 2, 400)
        draw_text("ESC untuk keluar", 20, MOON, WIDTH // 2, 440)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_LEFT]:
                    selected_option = (selected_option - 1) % 2
                elif event.key in [pygame.K_DOWN, pygame.K_RIGHT]:
                    selected_option = (selected_option + 1) % 2
                elif event.key == pygame.K_RETURN:
                    game_loop(selected_option + 1)
                    game_over()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        about_button = pygame.Rect(WIDTH - 110, HEIGHT - 50, 90, 35)
        pygame.draw.rect(screen, (200, 200, 200), about_button, border_radius=8)
        draw_text("about", 20, (0, 0, 0), WIDTH - 65, HEIGHT - 32)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if about_button.collidepoint(event.pos):
                show_about()

        pygame.display.flip()
        clock.tick(60)

# Game over
def game_over():
    while True:
        draw_background()
        draw_text("Game Over!", 50, MOON, WIDTH//2, 200)
        draw_text("Spasi untuk Main Lagi", 30, MOON, WIDTH//2, 300)
        draw_text("Backspace untuk Keluar Game", 30, MOON, WIDTH//2, 350)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    menu()
                elif event.key == pygame.K_BACKSPACE:
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)

# About
def show_about():
    about_running = True
    while about_running:
        screen.fill((240, 240, 240))

        draw_text("PROJECT UTS SQUARE 2D GAME SEDERHANA", 26, (0, 0, 0), WIDTH // 2, 80)
        draw_text("Nama dan NPM :", 22, (0, 0, 0), WIDTH // 2, 120)
        draw_text("1. Desandi Herdiansyah (24072123050)", 22, (0, 0, 0), WIDTH // 2, 150)
        draw_text("2. Moch Rifqi Putra W.R (24072123055)", 22, (0, 0, 0), WIDTH // 2, 180)
        draw_text("3. Pungki Sopian (24072123057)", 22, (0, 0, 0), WIDTH // 2, 210)

        draw_text("Pengembang ide Game : Desandi, Rifqi, Pungki", 22, (0, 0, 0), WIDTH // 2, 260)
        draw_text("Sumber Code : ChatGPT", 22, (0, 0, 0), WIDTH // 2, 290)
        draw_text("Editor Code : Desandi", 22, (0, 0, 0), WIDTH // 2, 320)
        draw_text("Laporan : Desandi, Rifqi, Pungki", 22, (0, 0, 0), WIDTH // 2, 350)

        draw_text("Tekan ESC untuk kembali", 20, (80, 80, 80), WIDTH // 2, 420)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                about_running = False

        pygame.display.flip()
        clock.tick(60)

# Jalankan
menu()
