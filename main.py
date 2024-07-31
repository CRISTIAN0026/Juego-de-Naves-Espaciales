import pygame
import random
import pickle
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de Naves Espaciales")

player_img = pygame.image.load('assets/nave.png')
player_img = pygame.transform.scale(player_img, (50, 50))

asteroid_img = pygame.image.load('assets/asteroide.png')
asteroid_img = pygame.transform.scale(asteroid_img, (50, 50))

star_img = pygame.image.load('assets/estrella.png')
star_img = pygame.transform.scale(star_img, (30, 30))

powerup_img = pygame.image.load('assets/powerup.png')
powerup_img = pygame.transform.scale(powerup_img, (30, 30))

HIGHSCORE_FILE = "highscores.dat"

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 5, y - 10, 10, 20)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Player:
    def __init__(self):
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_time = 0
        self.bullets = []

    def move(self, dx):
        self.rect.x += dx
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

    def draw(self, screen):
        if self.invulnerable:
            alpha_surf = self.image.copy()
            alpha_surf.set_alpha(128)
            screen.blit(alpha_surf, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        self.bullets.append(bullet)

    def update_invulnerability(self):
        if self.invulnerable:
            self.invulnerable_time -= 1
            if self.invulnerable_time <= 0:
                self.invulnerable = False

    def update_bullets(self, asteroids):
        bullets_to_remove = []
        asteroids_to_remove = []

        for bullet in self.bullets:
            bullet.update()
            if bullet.rect.bottom < 0:
                bullets_to_remove.append(bullet)
            else:
                for asteroid in asteroids:
                    if bullet.rect.colliderect(asteroid.rect):
                        asteroid.take_damage()
                        bullets_to_remove.append(bullet)
                        if asteroid.health <= 0:
                            asteroids_to_remove.append(asteroid)
                        break

        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)

        for asteroid in asteroids_to_remove:
            if asteroid in asteroids:
                asteroids.remove(asteroid)

class Asteroid:
    def __init__(self, speed=5, health=1):
        self.image = asteroid_img
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))
        self.speed = speed
        self.health = health

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def take_damage(self):
        self.health -= 1

class Star:
    def __init__(self):
        self.image = star_img
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))

    def update(self):
        self.rect.y += 5
        if self.rect.top > HEIGHT:
            self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class PowerUp:
    def __init__(self):
        self.image = powerup_img
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))
        self.type = random.choice(['invulnerable', 'extra_life'])

    def update(self):
        self.rect.y += 5
        if self.rect.top > HEIGHT:
            self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'rb') as f:
            return pickle.load(f)
    return []

def save_highscore(score):
    highscores = load_highscores()
    highscores.append(score)
    highscores = sorted(highscores, reverse=True)[:5]
    with open(HIGHSCORE_FILE, 'wb') as f:
        pickle.dump(highscores, f)

def main_menu():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render("Presiona cualquier tecla para iniciar", True, WHITE)
    screen.blit(text, (100, HEIGHT // 2))
    pygame.display.flip()
    wait_for_input()

def wait_for_input():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def game_over(score):
    save_highscore(score)
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, WHITE)
    screen.blit(text, (300, HEIGHT // 2 - 50))
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (300, HEIGHT // 2 + 20))

    font = pygame.font.Font(None, 36)
    highscores = load_highscores()
    y_offset = 150
    for idx, hs in enumerate(highscores, 1):
        hs_text = font.render(f"{idx}. {hs}", True, WHITE)
        screen.blit(hs_text, (300, HEIGHT // 2 + y_offset))
        y_offset += 30

    restart_text = font.render("Presiona 'R' para reiniciar", True, WHITE)
    screen.blit(restart_text, (260, HEIGHT // 2 + 100 + y_offset))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False

def draw_pause_button():
    font = pygame.font.Font(None, 36)
    text = font.render("Pausa (P)", True, WHITE)
    button_rect = text.get_rect(topright=(WIDTH - 10, 10))
    screen.blit(text, button_rect)
    return button_rect

def draw_end_button():
    font = pygame.font.Font(None, 36)
    text = font.render("Terminar Juego", True, BLACK)
    button_rect = text.get_rect(topright=(WIDTH - 10, 50))
    pygame.draw.rect(screen, RED, button_rect)
    screen.blit(text, button_rect)
    return button_rect

def main_game():
    player = Player()
    asteroids = [Asteroid(speed=random.randint(5, 10)) for _ in range(5)]
    stars = []
    powerups = []
    score = 0
    level = 1
    clock = pygame.time.Clock()
    running = True
    paused = False

    MIN_ASTEROIDS = 5
    POWERUP_PROBABILITY = 0.005
    STAR_PROBABILITY = 0.005

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_SPACE and not paused:
                    player.shoot()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if end_button_rect.collidepoint(mouse_pos):
                    running = False

        if paused:
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-5)
        if keys[pygame.K_RIGHT]:
            player.move(5)

        player.update_invulnerability()

        screen.fill(BLACK)

        player.update_bullets(asteroids)
        for bullet in player.bullets:
            bullet.draw(screen)

        for asteroid in asteroids:
            asteroid.update()
            asteroid.draw(screen)
            if asteroid.rect.colliderect(player.rect) and not player.invulnerable:
                player.lives -= 1
                player.invulnerable = True
                player.invulnerable_time = 180
                if player.lives <= 0:
                    running = False
            if asteroid.rect.top > HEIGHT:
                score += 10

        asteroids = [asteroid for asteroid in asteroids if asteroid.health > 0]

        score += 10 * (MIN_ASTEROIDS - len(asteroids))

        while len(asteroids) < MIN_ASTEROIDS:
            asteroids.append(Asteroid(speed=random.randint(5, 10)))

        if random.random() < STAR_PROBABILITY:
            stars.append(Star())

        for star in stars:
            star.update()
            star.draw(screen)
            if star.rect.colliderect(player.rect):
                score += 5
                stars.remove(star)

        if random.random() < POWERUP_PROBABILITY:
            powerups.append(PowerUp())

        for powerup in powerups:
            powerup.update()
            powerup.draw(screen)
            if powerup.rect.colliderect(player.rect):
                if powerup.type == 'extra_life':
                    player.lives += 1
                elif powerup.type == 'invulnerable':
                    player.invulnerable = True
                    player.invulnerable_time = 180
                powerups.remove(powerup)

        player.draw(screen)

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(lives_text, (10, 50))

        pause_button_rect = draw_pause_button()
        end_button_rect = draw_end_button()

        pygame.display.flip()
        clock.tick(FPS)

    game_over(score)

main_menu()
while True:
    main_game()
