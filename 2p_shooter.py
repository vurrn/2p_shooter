import pygame
import sys
import random
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2-Player Shooting Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game variables
clock = pygame.time.Clock()
FPS = 60

# Load images
def load_image(name, scale=1):
    try:
        image = pygame.image.load(name)
        if scale != 1:
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] * scale)))
        return image
    except:
        # Create a placeholder if image not found
        surf = pygame.Surface((50, 50))
        surf.fill(RED if "1" in name else BLUE if "2" in name else GREEN if "obstacle" in name else WHITE)
        return surf

background_img = load_image("background.png")
player1_img = load_image("player1.png")
player2_img = load_image("player2.png")
bullet_img = load_image("bullet.png", 0.5)
obstacle_img = load_image("obstacle.png")

# Sound effects
pygame.mixer.init()
fire = pygame.mixer.Sound('fire.ogg')

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, player_num):
        super().__init__()
        self.image = player1_img if player_num == 1 else player2_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.controls = controls  # [up, down, fire]
        self.player_num = player_num
        self.lives = 3
        self.bullets = 10
        self.reload_time = 0
        self.reloading = False
        self.score = 0
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[self.controls[0]] and self.rect.top > 70:
            self.rect.y -= self.speed
        if keys[self.controls[1]] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
            
        # Reloading
        if self.reloading:
            self.reload_time += 1
            if self.reload_time >= 120:  # 2 seconds at 60 FPS
                self.bullets = 10
                self.reloading = False
                self.reload_time = 0
    
    def fire(self):
        if not self.reloading and self.bullets > 0:
            global fire
            fire.play()
            self.bullets -= 1
            if self.bullets <= 0:
                self.reloading = True
            return Bullet(self.rect.right if self.player_num == 1 else self.rect.left - 10, 
                          self.rect.centery, 1 if self.player_num == 1 else -1)
        return None
    
    def draw_lives(self, surface):
        for i in range(self.lives):
            x = 20 + i * 30 if self.player_num == 1 else WIDTH - 20 - i * 30
            pygame.draw.circle(surface, RED if self.player_num == 1 else BLUE, (x, 20), 10)
    
    def draw_ammo(self, surface):
        font = pygame.font.SysFont(None, 24)
        ammo_text = f"Ammo: {self.bullets}/10"
        if self.reloading:
            ammo_text = "Reloading..."
        text = font.render(ammo_text, True, WHITE)
        if self.player_num == 1:
            surface.blit(text, (10, 40))
        else:
            surface.blit(text, (WIDTH - 110, 40))

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 10 * direction
        self.direction = direction
    
    def update(self):
        self.rect.x += self.speed
        # Remove if off screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = obstacle_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(WIDTH//4, WIDTH*3//4 - self.rect.width)
        self.rect.y = random.randint(70, HEIGHT - self.rect.height)
        self.health = 3
    
    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
            return True
        return False

# Button class
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(None, 36)
        self.active = False
    
    def draw(self, surface):
        color = GREEN if self.active else WHITE
        pygame.draw.rect(surface, color, self.rect, 2)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.active = self.rect.collidepoint(pos)
        return self.active
    
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Game function
def game():
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    
    # Create players
    player1 = Player(50, HEIGHT//2 - 25, [pygame.K_w, pygame.K_s, pygame.K_LSHIFT], 1)
    player2 = Player(WIDTH - 100, HEIGHT//2 - 25, [pygame.K_UP, pygame.K_DOWN, pygame.K_RSHIFT], 2)
    all_sprites.add(player1, player2)
    
    # Game variables
    obstacle_timer = 0
    game_over = False
    winner = None
    reset_button = Button(WIDTH//2 - 75, HEIGHT//2 + 50, 150, 50, "Play Again")
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not game_over:
                    if event.key == player1.controls[2]:
                        bullet = player1.fire()
                        if bullet:
                            bullets.add(bullet)
                            all_sprites.add(bullet)
                    if event.key == player2.controls[2]:
                        bullet = player2.fire()
                        if bullet:
                            bullets.add(bullet)
                            all_sprites.add(bullet)
            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                if reset_button.is_clicked(pygame.mouse.get_pos(), True):
                    return True  # Restart game
        
        if not game_over:
            # Spawn obstacles randomly
            obstacle_timer += 1
            if obstacle_timer >= random.randint(120, 360) and len(obstacles) < 3:
                obstacle = Obstacle()
                obstacles.add(obstacle)
                all_sprites.add(obstacle)
                obstacle_timer = 0
            
            # Update
            all_sprites.update()
            
            # Check bullet collisions with players
            for bullet in bullets:
                if bullet.direction == 1:  # Player 1's bullet
                    if pygame.sprite.collide_rect(bullet, player2):
                        player2.lives -= 1
                        bullet.kill()
                        if player2.lives <= 0:
                            game_over = True
                            winner = "Player 1"
                else:  # Player 2's bullet
                    if pygame.sprite.collide_rect(bullet, player1):
                        player1.lives -= 1
                        bullet.kill()
                        if player1.lives <= 0:
                            game_over = True
                            winner = "Player 2"
            
            # Check bullet collisions with obstacles
            for bullet in bullets:
                for obstacle in obstacles:
                    if pygame.sprite.collide_rect(bullet, obstacle):
                        obstacle.hit()
                        bullet.kill()
        
        # Drawing
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        
        # Draw UI
        player1.draw_lives(screen)
        player2.draw_lives(screen)
        player1.draw_ammo(screen)
        player2.draw_ammo(screen)
        
        # Check hover on reset button
        if game_over:
            reset_button.check_hover(pygame.mouse.get_pos())
            
            # Draw game over text
            font = pygame.font.SysFont(None, 72)
            text = font.render(f"{winner} Wins!", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(text, text_rect)
            
            # Draw reset button
            reset_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return False  # Don't restart

# Main loop to handle game restarts
restart = True
while restart:
    restart = game()

pygame.quit()
sys.exit()