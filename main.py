import pygame 
import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configurar pantalla
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego Básico con Pygame")

# Colores
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)

# Jugador (un rectángulo rojo)
jugador = pygame.Rect(100, 100, 50, 50)
velocidad = 5

# Bucle principal del juego
reloj = pygame.time.Clock()
jugando = True

while jugando:
    reloj.tick(60)  # Limita a 60 FPS

    # Manejo de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugando = False

    # Movimiento del jugador
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        jugador.x -= velocidad
    if teclas[pygame.K_RIGHT]:
        jugador.x += velocidad
    if teclas[pygame.K_UP]:
        jugador.y -= velocidad
    if teclas[pygame.K_DOWN]:
        jugador.y += velocidad

    # Dibujar
    pantalla.fill(BLANCO)
    pygame.draw.rect(pantalla, ROJO, jugador)
    pygame.display.flip()

# Salir de pygame
pygame.quit()
sys.exit()