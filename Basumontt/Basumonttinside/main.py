import pygame
import random
import sys
import os

player_lives = 3
selected_character_images = None
pygame.init()
menu_move_sound = pygame.mixer.Sound("Basumontt/Basumonttinside/assets/sfx/bip.wav")
main_levels_song = "Basumontt/Basumonttinside/assets/sfx/song_level.mp3"
final_levels_song = "Basumontt/Basumonttinside/assets/sfx/final_song_level.mp3"
pygame.mixer.music.load("Basumontt/Basumonttinside/assets/sfx/menu_song.mp3")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(-1)
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
level = 1

# Pantalla
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basumontt")

def load_image(path):
    if not os.path.exists(path):
        print(f"[ERROR] Imagen no encontrada: {path}")
        sys.exit()
    return pygame.image.load(path).convert_alpha()

def load_background(lvl):
    return load_image(f"Basumontt/Basumonttinside/levels/level_{lvl}.png")

enemy_final_img = load_image("Basumontt/Basumonttinside/assets/enemymax.png")
player_img = load_image("Basumontt/Basumonttinside/assets/player.png")
enemy_img = load_image("Basumontt/Basumonttinside/assets/enemy.png")
bullet_img = load_image("Basumontt/Basumonttinside/assets/bullet.png")
trash_bullet_img = load_image("Basumontt/Basumonttinside/assets/trash_bullet.png")
powerup_speed_img = load_image("Basumontt/Basumonttinside/assets/powerup_speed.png")
powerup_double_img = load_image("Basumontt/Basumonttinside/assets/powerup_double.png")
main_menu_bg = load_image("Basumontt/Basumonttinside/menus/main_menu.jpg")
victory_bg = load_image("Basumontt/Basumonttinside/menus/victory.png")
game_over_bg = load_image("Basumontt/Basumonttinside/menus/game_over.png")
retro_font = pygame.font.Font("Basumontt/Basumonttinside/assets/fonts/pixel.ttf", 24)


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
class Player:
    def __init__(self, images):
        self.images = [load_image(img) for img in images]  
        self.index = 0
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.speed = PLAYER_SPEED
        self.cooldown = 500
        self.last_shot = pygame.time.get_ticks()
        self.double_shot = False
        self.health = 150
        self.max_health = 150
        self.animation_speed = 0.15

        #Animación de ataque
        self.attacking = False
        self.attack_timer = 0
        self.attack_duration = 200  

    def move(self, keys):
        if self.attacking:
            return

        moving = False
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            moving = True
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            moving = True
        if keys[pygame.K_UP] and self.rect.top > HEIGHT / 2:
            self.rect.y -= self.speed
            moving = True
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
            moving = True

        if moving:
            self.index += self.animation_speed
            if self.index >= len(self.images) - 1:  
                self.index = 0
            self.image = self.images[int(self.index)]

    def shoot(self, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.cooldown:
            self.last_shot = now
            bullets.append(Bullet(self.rect.centerx, self.rect.top))
            if self.double_shot:
                bullets.append(Bullet(self.rect.centerx - 20, self.rect.top))


            self.attacking = True
            self.attack_timer = now
            self.image = self.images[4]  

    def draw(self, win):
        if self.attacking and pygame.time.get_ticks() - self.attack_timer > self.attack_duration:
            self.attacking = False
            self.index = 0 
            self.image = self.images[int(self.index)]

        win.blit(self.image, self.rect)




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
    def __init__(self, level):
        if level == 10:
            self.image = enemy_final_img
        else:
            self.image = enemy_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, 80))
        self.direction = 1
        self.trash_timer = pygame.time.get_ticks()
        self.health = 500
        self.max_health = 500

    def move(self):
        self.rect.x += self.direction * ENEMY_SPEED * DIFFICULTIES[difficulty]
        if self.rect.right > random.randrange(450,750) or self.rect.left < random.randrange(0,200):
            self.direction *= -1

    def shoot_trash(self, trash_bullets):
        if pygame.time.get_ticks() - self.trash_timer > 600:
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

# Menús


def draw_menu(options, title=None, bg_img=main_menu_bg):
    selected = 0
    while True:
        win.blit(bg_img, (0, 0))
        if title:
            title_text = retro_font.render(title, True, (255, 0, 0))
            win.blit(title_text, (40, HEIGHT - 160))

        for i, option in enumerate(options):
            x, y = 40, HEIGHT - 120 + i * 40
            text = retro_font.render(option, True, (255, 255, 255))

            if i == selected:
                if title == "VICTORIA":
                    highlight_surface = pygame.Surface((text.get_width() + 20, text.get_height() + 10), pygame.SRCALPHA)
                    highlight_surface.fill((255, 0, 0, 120))
                    win.blit(highlight_surface, (x - 10, y - 5))

                else:
                    highlight_surface = pygame.Surface((text.get_width() + 20, text.get_height() + 10), pygame.SRCALPHA)
                    highlight_surface.fill((0, 200, 255, 120))
                    win.blit(highlight_surface, (x - 10, y - 5))

            win.blit(text, (x, y))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    menu_move_sound.play()
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    menu_move_sound.play()
                elif event.key == pygame.K_z:
                    menu_move_sound.play()
                    return options[selected]

def show_main_menu():
    pygame.mixer.music.load("Basumontt/Basumonttinside/assets/sfx/menu_song.mp3")
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1)
    choice = draw_menu(["INICIAR", "ELEGIR DIFICULTAD", "SALIR"], bg_img=main_menu_bg)
    if choice == "INICIAR":
        show_character_selector()
        return
    elif choice == "ELEGIR DIFICULTAD":
        show_start_menu()
    elif choice == "SALIR":
        pygame.quit()
        sys.exit()
    show_main_menu()

def show_game_over_menu():
    global level
    pygame.mixer.music.stop()
    pygame.mixer.music.load("Basumontt/Basumonttinside/assets/sfx/losing.mp3")
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(1)
    choice = draw_menu(["REINTENTAR", "MENU", "SALIR"], title="GAME OVER", bg_img=game_over_bg)
    if choice == "REINTENTAR":
        level=1
        game_loop(selected_character_images)
    elif choice == "MENU":
        show_main_menu()
        return
    elif choice == "SALIR":
        pygame.quit()
        sys.exit()

def show_victory_menu():
    global level
    pygame.mixer.music.stop()
    pygame.mixer.music.load("Basumontt/Basumonttinside/assets/sfx/winning.mp3")
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(1)
    choice = draw_menu(["VOLVER A JUGAR", "MENU", "SALIR"], title="VICTORIA", bg_img=victory_bg)
    if choice == "VOLVER A JUGAR":
        level=1
        game_loop(selected_character_images)
    elif choice == "MENU":
        show_main_menu()
        return
    elif choice == "SALIR":
        pygame.quit()
        sys.exit()

# Barras de vida
def draw_health_bars(win, player, enemy):
    pygame.draw.rect(win, (255, 0, 0), (20, 20, 200, 20))
    pygame.draw.rect(win, (0, 255, 0), (20, 20, 200 * player.health / player.max_health, 20))
    pygame.draw.rect(win, (255, 0, 0), (WIDTH - 220, 20, 200, 20))
    pygame.draw.rect(win, (0, 255, 0), (WIDTH - 220, 20, 200 * enemy.health / enemy.max_health, 20))

# Menú de inicio 
def show_start_menu():
    global difficulty, level
    font = retro_font.render
    title_font = pygame.font.SysFont("arial", 48, bold=True)
    options = {
        "Dificultad": ["principiante", "normal", "ingeniero"],
        "Nivel": list(range(1, LEVELS + 1))
    }
    selected = {"Dificultad": 1, "Nivel": 0}
    selecting = True
    selected_row = 0
    while selecting:
        win.fill((30, 30, 30))
        title = retro_font.render("Basumontt", True, (0, 200, 255))
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        ypos = 150
        for idx, (label, choices) in enumerate(options.items()):
            color = (255, 255, 255) if idx != selected_row else (0, 255, 0)
            text = retro_font.render(f"{label}: {choices[selected[label]]}", True, color)
            win.blit(text, (WIDTH // 2 - text.get_width() // 2, ypos))
            ypos += 60
        instructions = retro_font.render("← → para cambiar | ↑ ↓ para mover | Z para jugar", True, (200, 200, 200))
        win.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 100))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_row = (selected_row - 1) % len(options)
                    menu_move_sound.play()
                elif event.key == pygame.K_DOWN:
                    selected_row = (selected_row + 1) % len(options)
                    menu_move_sound.play()
                elif event.key == pygame.K_LEFT:
                    key = list(options.keys())[selected_row]
                    selected[key] = (selected[key] - 1) % len(options[key])
                    menu_move_sound.play()
                elif event.key == pygame.K_RIGHT:
                    key = list(options.keys())[selected_row]
                    selected[key] = (selected[key] + 1) % len(options[key])
                    menu_move_sound.play()
                elif event.key == pygame.K_z:
                    menu_move_sound.play()
                    difficulty = options["Dificultad"][selected["Dificultad"]]
                    level = options["Nivel"][selected["Nivel"]]
                    selecting = False

def play_level_music(level):
    if level < 10:
        pygame.mixer.music.load(main_levels_song)
    else:
        pygame.mixer.music.load(final_levels_song)
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1)

def show_character_selector():
    
    global selected_character_images
    clock = pygame.time.Clock()
    selected = 0

    character_sets = [
        ["Basumontt/Basumonttinside/assets/player_1/move_0.png", "Basumontt/Basumonttinside/assets/player_1/move_1.png", "Basumontt/Basumonttinside/assets/player_1/move_4.png"],
        ["Basumontt/Basumonttinside/assets/player_2/move_0.png", "Basumontt/Basumonttinside/assets/player_2/move_1.png", "Basumontt/Basumonttinside/assets/player_2/move_2.png", "Basumontt/Basumonttinside/assets/player_2/move_4.png"]
    ]

    character_previews = [
        load_image("Basumontt/Basumonttinside/assets/player_1/move_5.png"),
        load_image("Basumontt/Basumonttinside/assets/player_2/move_5.png")
    ]

    selecting = True
    while selecting:
        clock.tick(FPS)
        win.fill((20, 20, 20))

        title = retro_font.render("ELEGIR PERSONAJE", True, (0, 200, 255))
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        for i, img in enumerate(character_previews):
            x = WIDTH // 2 - img.get_width() - 60 if i == 0 else WIDTH // 2 + 60
            y = HEIGHT // 2 - img.get_height() // 2
            rect = pygame.Rect(x - 10, y - 10, img.get_width() + 20, img.get_height() + 20)

            border_color = (0, 200, 255) if i == selected else (100, 100, 100)
            pygame.draw.rect(win, border_color, rect, border_radius=10)
            win.blit(img, (x, y))

        instructions = retro_font.render("← → para elegir | Z para confirmar", True, (200, 200, 200))
        win.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 80))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(character_sets)
                elif event.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(character_sets)
                elif event.key == pygame.K_z:
                    selected_character_images = character_sets[selected]  
                    game_loop(selected_character_images)
                    selecting = False
                    return



def game_loop(player_images=None):
    global level
    clock = pygame.time.Clock()
    if not player_images:
        player_images = ["Basumontt/Basumonttinside/assets/player_1/move_0.png", "Basumontt/Basumonttinside/assets/player_1/move_1.png", "Basumontt/Basumonttinside/assets/player_1/move_2.png"]
    player = Player(player_images)
    enemy = Enemy(level)
    bullets = []
    trash_bullets = []
    powerups = []
    bg = load_background(level)
    pygame.mixer.music.stop()
    play_level_music(level)
    hit_timer = 0
    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if keys[pygame.K_ESCAPE]:
            show_main_menu()
        player.move(keys)
        enemy.move()
        enemy.shoot_trash(trash_bullets)
        if keys[pygame.K_z]:
            player.shoot(bullets)
        if random.randint(0, 1000) < 5:
            kind = random.choice(["speed", "double"])
            powerups.append(PowerUp(kind))
        for bullet in bullets:
            bullet.move()
        for trash in trash_bullets:
            trash.move()
        for power in powerups:
            power.move()
        bullets = [b for b in bullets if b.rect.bottom > 0]
        trash_bullets = [t for t in trash_bullets if t.rect.top < HEIGHT]
        for trash in trash_bullets:
            if trash.rect.colliderect(player.rect):
                trash_bullets.remove(trash)
                player.health -=50
                if player.health <=0:
                    show_game_over_menu()
                    return
        for power in powerups[:]:
            if power.rect.colliderect(player.rect):
                if power.kind == "speed":
                    player.cooldown = 250
                elif power.kind == "double":
                    player.double_shot = True
                powerups.remove(power)
        for bullet in bullets[:]:
            if bullet.rect.colliderect(enemy.rect):
                bullets.remove(bullet)
                enemy.health -= 10
                hit_timer = pygame.time.get_ticks()
                if enemy.health <= 0:
                    level += 1
                    if level > LEVELS:
                    
                        show_victory_menu()
                        return
                    bg = load_background(level)
                    
                    enemy = Enemy(level)
                    pygame.mixer.music.stop()
                    play_level_music(level) 
        win.blit(bg, (0, 0))
        player.draw(win)
        enemy.draw(win)
        for bullet in bullets:
            bullet.draw(win)
        for trash in trash_bullets:
            trash.draw(win)
        for power in powerups:
            power.draw(win)
        if pygame.time.get_ticks() - hit_timer < 100:
            pass
        draw_health_bars(win, player, enemy)
        pygame.display.update()

show_main_menu()