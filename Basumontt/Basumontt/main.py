
import pygame
import random
import sys
import os

# Inicializar pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED = 2
LEVELS = 10

# Dificultad
DIFFICULTIES = {
    "principiante": 1,
    "normal": 2,
    "ingeniero": 3
}

# Configuración
difficulty = "ingeniero"
level = 7

# Pantalla
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trashmorph")

# Cargar recursos
def load_image(path):
    return pygame.image.load(path).convert_alpha()

player_img = load_image("Basumontt/Basumontt/assets/player.png")
enemy_img = load_image("Basumontt/Basumontt/assets/enemy.png")
bullet_img = load_image("Basumontt/Basumontt/assets/bullet.png")
trash_bullet_img = load_image("Basumontt/Basumontt/assets/trash_bullet.png")
powerup_speed_img = load_image("Basumontt/Basumontt/assets/powerup_speed.png")
powerup_double_img = load_image("Basumontt/Basumontt/assets/powerup_double.png")

def load_background(lvl):
    return pygame.image.load(f"Basumontt/Basumontt/levels/level_{lvl}.jpg")

# Sonidos

# Clases
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, images, x, y, scale=1.0, health=100):
        super().__init__()
        self.images = [pygame.transform.scale(pygame.image.load(img), (int(64*scale), int(64*scale))) for img in images]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 0.15
        self.health = health
        self.max_health = health

    def update(self):
        self.index += self.animation_speed
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[int(self.index)]

    def draw_health_bar(self, surface, x_offset, y_offset):
        ratio = self.health / self.max_health
        pygame.draw.rect(surface, (255, 0, 0), (x_offset, y_offset, 200, 20))
        pygame.draw.rect(surface, (0, 255, 0), (x_offset, y_offset, 200 * ratio, 20))

class Player:
    def __init__(self):
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.speed = PLAYER_SPEED
        self.cooldown = 500
        self.last_shot = pygame.time.get_ticks()
        self.double_shot = False

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > HEIGHT/2:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def shoot(self, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.cooldown:
            self.last_shot = now
            bullets.append(Bullet(self.rect.centerx, self.rect.top))
            if self.double_shot:
                bullets.append(Bullet(self.rect.centerx - 20, self.rect.top))

    def draw(self, win):
        win.blit(self.image, self.rect)

class Enemy:
    def __init__(self):
        self.image = enemy_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, 80))
        self.direction = 1
        self.trash_timer = pygame.time.get_ticks()

    def move(self):
        self.rect.x += self.direction * ENEMY_SPEED * DIFFICULTIES[difficulty]
        if self.rect.right > random.randrange(200,900) or self.rect.left < random.randrange(0,75):
            self.direction *= -1

    def shoot_trash(self, trash_bullets):
        if pygame.time.get_ticks() - self.trash_timer > 1000:
            self.trash_timer = pygame.time.get_ticks()
            trash_bullets.append(TrashBullet(self.rect.centerx, self.rect.bottom))

    def draw(self, win):
        win.blit(self.image, self.rect)

class Bullet:
    def __init__(self, x, y):
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))

    def move(self):
        self.rect.y -= BULLET_SPEED

    def draw(self, win):
        win.blit(self.image, self.rect)

class TrashBullet:
    def __init__(self, x, y):
        self.image = trash_bullet_img
        self.rect = self.image.get_rect(center=(x, y))

    def move(self):
        self.rect.y += BULLET_SPEED

    def draw(self, win):
        win.blit(self.image, self.rect)

class PowerUp:
    def __init__(self, kind):
        self.kind = kind
        self.image = powerup_speed_img if kind == "speed" else powerup_double_img
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))

    def move(self):
        self.rect.y += 3

    def draw(self, win):
        win.blit(self.image, self.rect)

# Menú
def show_menu(image_path):
    menu = pygame.image.load(image_path)
    win.blit(menu, (0, 0))
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Game Loop
def game_loop():
    global level
    clock = pygame.time.Clock()
    player = Player()
    enemy = Enemy()
    bullets = []
    trash_bullets = []
    powerups = []

    bg = load_background(level)
    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if keys[pygame.K_ESCAPE]:
            show_menu("Basumontt/Basumontt/menus/pause_menu.jpg")

        # Movimiento
        player.move(keys)
        enemy.move()
        enemy.shoot_trash(trash_bullets)

        # Disparos
        if keys[pygame.K_z]:
            player.shoot(bullets)

        # Power-ups
        if random.randint(0, 1000) < 5:
            kind = random.choice(["speed", "double"])
            powerups.append(PowerUp(kind))

        for bullet in bullets:
            bullet.move()
        for trash in trash_bullets:
            trash.move()
        for power in powerups:
            power.move()

        # Colisiones
        bullets = [b for b in bullets if b.rect.bottom > 0]
        trash_bullets = [t for t in trash_bullets if t.rect.top < HEIGHT]

        for trash in trash_bullets:
            if trash.rect.colliderect(player.rect):
                show_menu("Basumontt/Basumontt/menus/game_over.jpg")
                return

        for power in powerups[:]:
            if power.rect.colliderect(player.rect):
                if power.kind == "speed":
                    player.cooldown = 250
                elif power.kind == "double":
                    player.double_shot = True
                powerups.remove(power)

        # Dibujo
        win.blit(bg, (0, 0))
        player.draw(win)
        enemy.draw(win)
        for bullet in bullets:
            bullet.draw(win)
        for trash in trash_bullets:
            trash.draw(win)
        for power in powerups:
            power.draw(win)
        pygame.display.update()

        # Avanzar de nivel
        if random.randint(0, 1000) < 3:
            level += 1
            if level > LEVELS:
                show_menu("Basumontt/Basumontt/menus/victory.jpg")
                return
            bg = load_background(level)

# Iniciar
show_menu("Basumontt/Basumontt/menus/main_menu.jpg")
def show_start_menu():
    global difficulty, level

    font = pygame.font.SysFont("arial", 32)
    title_font = pygame.font.SysFont("arial", 48, bold=True)
    options = {
        "Dificultad": ["principiante", "normal", "ingeniero"],
        "Nivel": list(range(1, LEVELS + 1))
    }
    selected = {
        "Dificultad": 1,  # default: "normal"
        "Nivel": 0        # default: 1
    }
    selecting = True
    selected_row = 0
    while selecting:
        win.fill((30, 30, 30))
        title = title_font.render("Trashmorph", True, (0, 200, 255))
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        ypos = 150
        for idx, (label, choices) in enumerate(options.items()):
            color = (255, 255, 255) if idx != selected_row else (0, 255, 0)
            text = font.render(f"{label}: {choices[selected[label]]}", True, color)
            win.blit(text, (WIDTH // 2 - text.get_width() // 2, ypos))
            ypos += 60

        instructions = font.render("← → para cambiar | ↑ ↓ para mover | Enter para jugar", True, (200, 200, 200))
        win.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 100))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_row = (selected_row - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_row = (selected_row + 1) % len(options)
                elif event.key == pygame.K_LEFT:
                    key = list(options.keys())[selected_row]
                    selected[key] = (selected[key] - 1) % len(options[key])
                elif event.key == pygame.K_RIGHT:
                    key = list(options.keys())[selected_row]
                    selected[key] = (selected[key] + 1) % len(options[key])
                elif event.key == pygame.K_RETURN:
                    difficulty = options["Dificultad"][selected["Dificultad"]]
                    level = options["Nivel"][selected["Nivel"]]
                    selecting = False
game_loop()