import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Initialize Pygame Mixer for sound
pygame.mixer.init()

# Define screen dimensions and colors
WIDTH, HEIGHT = 400, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
Creator_Dhananjay_Ladole = (128, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Load images
bird_img = pygame.image.load('bird.png')  
bird_img = pygame.transform.scale(bird_img, (40, 30))  

background_img = pygame.image.load('background.png')  
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))  

pipe_top_img = pygame.image.load('pipe_top.png') 
pipe_bottom_img = pygame.image.load('pipe_bottom.png')  

# Load main menu background image
main_menu_bg_img = pygame.image.load('main_menu_background.png')  
main_menu_bg_img = pygame.transform.scale(main_menu_bg_img, (600, 650))  

# Adjust pipe size
pipe_width = 65
pipe_height = 320
pipe_gap = 150

# Resize pipe images if necessary
pipe_top_img = pygame.transform.scale(pipe_top_img, (pipe_width, pipe_height))
pipe_bottom_img = pygame.transform.scale(pipe_bottom_img, (pipe_width, pipe_height))

# Load sound files
try:
    jump_sound = pygame.mixer.Sound('jump.wav')
    game_over_sound = pygame.mixer.Sound('game_over.wav')
except FileNotFoundError as e:
    print(f"Error loading sound files: {e}")
    # Use default sound if the file is missing
    jump_sound = pygame.mixer.Sound(pygame.mixer.Sound.get_default_sound())
    game_over_sound = pygame.mixer.Sound(pygame.mixer.Sound.get_default_sound())

pygame.mixer.music.load('background_music.mp3')

# Load sticker image
sticker_img = pygame.image.load('sticker.png') 
sticker_img = pygame.transform.scale(sticker_img, (100, 100))  

# Game variables
pipe_speed = 5
pipe_frequency = 1500  

# Scrolling background variables
bg_x1 = 0
bg_x2 = WIDTH

# High Score file
high_score_file = "high_score.txt"


def read_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as file:
            return int(file.read().strip())
    return 0

def write_high_score(score):
    with open(high_score_file, "w") as file:
        file.write(str(score))

def reset_game():
    global bird_x, bird_y, bird_speed, pipes, score, last_pipe, running
    bird_x, bird_y = WIDTH // 4, HEIGHT // 2
    bird_speed = 0
    pipes = []
    score = 0
    last_pipe = pygame.time.get_ticks() - pipe_frequency
    running = True

def display_message(message, size, color, position):
    font = pygame.font.Font(None, size)
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)

def update_background():
    global bg_x1, bg_x2
    bg_x1 -= 2  # Adjust speed for background scrolling
    bg_x2 -= 2
    if bg_x1 <= -WIDTH:
        bg_x1 = WIDTH
    if bg_x2 <= -WIDTH:
        bg_x2 = WIDTH
    screen.blit(background_img, (bg_x1, 0))
    screen.blit(background_img, (bg_x2, 0))

def game_loop():
    global running, bird_x, bird_y, bird_speed, pipes, score, last_pipe

    reset_game()
    pygame.mixer.music.play(-1)  # Play background music on loop

    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_speed = -10
                    jump_sound.play()  
            if event.type == pygame.MOUSEBUTTONDOWN:
                bird_speed = -10
                jump_sound.play()  

        # Bird movement
        bird_speed += 0.5  # gravity
        bird_y += bird_speed

        # Generate pipes
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe > pipe_frequency:
            pipe_height = random.randint(100, HEIGHT - pipe_gap - 100)
            pipes.append({'x': WIDTH, 'height': pipe_height, 'passed': False})
            last_pipe = current_time

        # Move pipes
        for pipe in pipes:
            pipe['x'] -= pipe_speed

        # Remove off-screen pipes
        pipes = [pipe for pipe in pipes if pipe['x'] > -pipe_width]

        # Check collisions
        bird_rect = pygame.Rect(bird_x, bird_y, 40, 30)
        for pipe in pipes:
            top_pipe_rect = pygame.Rect(pipe['x'], 0, pipe_width, pipe['height'])
            bottom_pipe_rect = pygame.Rect(pipe['x'], pipe['height'] + pipe_gap, pipe_width, HEIGHT)
            if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
                running = False

        # Check if bird hits the ground or ceiling
        if bird_y > HEIGHT - 30 or bird_y < 0:
            running = False

        # Update score
        for pipe in pipes:
            if not pipe['passed'] and pipe['x'] + pipe_width < bird_x:
                score += 1
                pipe['passed'] = True

        # Drawing
        update_background() 
        screen.blit(bird_img, (bird_x, bird_y))
        for pipe in pipes:
            screen.blit(pipe_top_img, (pipe['x'], 0), pygame.Rect(0, 0, pipe_width, pipe['height']))
            screen.blit(pipe_bottom_img, (pipe['x'], pipe['height'] + pipe_gap))

        # Draw score
        display_message(f"Score: {score}", 36, BLACK, (WIDTH // 2, 30))
        display_message(f"High Score: {high_score}", 36, BLACK, (WIDTH // 2, 60))

        # Update display
        pygame.display.flip()
        clock.tick(30)

def game_over_screen():
    global high_score

    screen.fill(WHITE)
    display_message(f"Game Over! Score: {score}", 48, BLACK, (WIDTH // 2, HEIGHT // 3))
    display_message(f"High Score: {high_score}", 36, BLACK, (WIDTH // 2, HEIGHT // 2))
    display_message("Click to Restart", 36, BLACK, (WIDTH // 2, HEIGHT // 1.5))
    pygame.display.flip()

    # Stop background music and play game over sound
    pygame.mixer.music.stop()
    game_over_sound.play()

    # Update high score
    if score > high_score:
        high_score = score
        write_high_score(high_score)

    # Wait for a mouse click to restart
    waiting_for_restart = True
    while waiting_for_restart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return  # Exit the function to restart the game

def main_menu():
    screen.blit(main_menu_bg_img, (0, 0))  # Draw the background image

    # Display main menu text
    display_message("Flappy Bird", 72, BLACK, (WIDTH // 2, HEIGHT // 3))
    display_message("Click to Start", 30, BLACK, (WIDTH // 2, HEIGHT // 2.3))
    display_message("Creator: Dhananjay_Ladole", 20, Creator_Dhananjay_Ladole, (WIDTH // 2, HEIGHT // 1.02))

    pygame.display.flip()

    # Wait for a mouse click to start the game
    waiting_for_start = True
    while waiting_for_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return  # Exit the function to start the game


# Get high score
high_score = read_high_score()

# Main game loop
while True:
    main_menu()
    game_loop()
    game_over_screen()
