import pygame
import sys
import random
import serial
import time

# Initialize serial communication
SERIAL_PORT = 'COM3'  # Adjust this to your serial port
BAUD_RATE = 9600

# Attempt to initialize serial communication
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    time.sleep(2)  # Wait for the serial connection to initialize
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    ser = None  # Serial communication will be disabled

# Initialize Pygame
pygame.init()

# Window size
frame_size_x = 720
frame_size_y = 480

# Initialize game window
pygame.display.set_caption('Snake Eater')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))

# Load apple image
apple_img = pygame.image.load("apple.gif")
apple_img = pygame.transform.scale(apple_img, (20, 20))


black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
green = pygame.Color(0, 255, 0)

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

# Game variables
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_size = 20
direction = 'RIGHT'
change_to = direction
score = 0

# Food position
food_pos = [random.randrange(1, (frame_size_x // snake_size)) * snake_size,
            random.randrange(1, (frame_size_y // snake_size)) * snake_size]
food_spawn = True

# Game Over function
def game_over():
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, pygame.Color(255, 0, 0))
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (frame_size_x / 2, frame_size_y / 4)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(0, pygame.Color(255, 0, 0), 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    if ser:
        ser.close()
    sys.exit()

# Score function
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x / 10, 15)
    else:
        score_rect.midtop = (frame_size_x / 2, frame_size_y / 1.25)
    game_window.blit(score_surface, score_rect)

# Main logic
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != 'DOWN':
                change_to = 'UP'
            if event.key == pygame.K_DOWN and direction != 'UP':
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT and direction != 'RIGHT':
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT and direction != 'LEFT':
                change_to = 'RIGHT'

    # Read joystick data from Arduino
    if ser and ser.in_waiting > 0:
        try:
            data = ser.readline().decode().strip()
            x_dir, y_dir = map(int, data.split(','))
            
            if x_dir == -1 and direction != 'RIGHT':
                change_to = 'LEFT'
            elif x_dir == 1 and direction != 'LEFT':
                change_to = 'RIGHT'
            elif y_dir == -1 and direction != 'DOWN':
                change_to = 'UP'
            elif y_dir == 1 and direction != 'UP':
                change_to = 'DOWN'
        except (ValueError, serial.SerialException) as e:
            print(f"Error reading from serial port: {e}")

    # Making sure the snake cannot move in the opposite direction instantaneously
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # Moving the snake
    if direction == 'UP':
        snake_pos[1] -= snake_size
    if direction == 'DOWN':
        snake_pos[1] += snake_size
    if direction == 'LEFT':
        snake_pos[0] -= snake_size
    if direction == 'RIGHT':
        snake_pos[0] += snake_size

    # Snake body growing mechanism
    snake_body.insert(0, list(snake_pos))

    # Check if the snake has eaten the food
    if pygame.Rect(snake_pos[0], snake_pos[1], snake_size, snake_size).colliderect(
            pygame.Rect(food_pos[0], food_pos[1], snake_size, snake_size)):
        score += 1
        food_spawn = False
    else:
        snake_body.pop()

    # Spawning food on the screen
    if not food_spawn:
        food_pos = [random.randrange(1, (frame_size_x // snake_size)) * snake_size,
                    random.randrange(1, (frame_size_y // snake_size)) * snake_size]
    food_spawn = True

    # GFX
    game_window.fill(black)
    for pos in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], snake_size, snake_size))

    # Snake food
    game_window.blit(apple_img, (food_pos[0], food_pos[1]))

    # Game Over conditions
    if snake_pos[0] < 0 or snake_pos[0] > frame_size_x - snake_size:
        game_over()
    if snake_pos[1] < 0 or snake_pos[1] > frame_size_y - snake_size:
        game_over()
    for block in snake_body[1:]:
        if snake_pos == block:
            game_over()

    show_score(1, white, 'consolas', 20)
    pygame.display.update()
    fps_controller.tick(10)
