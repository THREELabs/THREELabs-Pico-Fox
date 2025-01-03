from machine import Pin, Timer
import utime
import random
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

# Initialize display
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=0)
WIDTH, HEIGHT = display.get_bounds()

# Initialize buttons
button_a = Button(12)  # A button
button_b = Button(13)  # B button
button_x = Button(14)  # X button
button_y = Button(15)  # Y button

# Colors
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
BLUE = display.create_pen(0, 0, 255)
RED = display.create_pen(255, 0, 0)
YELLOW = display.create_pen(255, 255, 0)
GREEN = display.create_pen(0, 255, 0)
ORANGE = display.create_pen(255, 165, 0)
PURPLE = display.create_pen(128, 0, 128)
CYAN = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)

# Game variables
ship_x = WIDTH // 2
ship_y = HEIGHT // 2
ship_speed = 3
obstacles = []  # Each obstacle is a dictionary with x, y, z, size, health, is_boss
obstacle_speed = 0.1  # Increased speed for faster game pace
spawn_rate = 30  # Decreased rate for more frequent spawning
projectiles = []  # Each projectile is a list [x, y, z, color]
power_ups = []  # Each power-up is a list [x, y, z]
explosions = []  # Each explosion is a list [x, y, z, size, color, lifetime, vx, vy]
special_weapon_active = False
special_weapon_duration = 500  # Duration of special weapon in frames
special_weapon_timer = 0
score = 0
game_over = False
last_boss_score = 0

# Starfield variables
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.1, 1.0)] for _ in range(50)]

def reset_game():
    global ship_x, ship_y, obstacles, projectiles, power_ups, explosions, special_weapon_active, special_weapon_timer, score, game_over, last_boss_score
    ship_x = WIDTH // 2
    ship_y = HEIGHT // 2
    obstacles = []
    projectiles = []
    power_ups = []
    explosions = []
    special_weapon_active = False
    special_weapon_timer = 0
    score = 0
    game_over = False
    last_boss_score = 0

def project_3d_to_2d(x, y, z):
    """Convert 3D coordinates to 2D screen coordinates using perspective projection."""
    scale = 1 / z  # Objects farther away are smaller
    screen_x = int(x * scale + WIDTH // 2)
    screen_y = int(y * scale + HEIGHT // 2)
    return screen_x, screen_y

def draw_starfield():
    for star in stars:
        display.set_pen(WHITE)
        screen_x, screen_y = project_3d_to_2d(star[0] - WIDTH // 2, star[1] - HEIGHT // 2, star[2])
        display.circle(screen_x, screen_y, 1)
        star[2] -= 0.01  # Move star toward the player
        if star[2] <= 0.1:  # Reset star when it gets too close
            star[0] = random.randint(0, WIDTH)
            star[1] = random.randint(0, HEIGHT)
            star[2] = random.uniform(0.1, 1.0)

def draw_ship():
    display.set_pen(YELLOW)
    display.triangle(ship_x - 10, ship_y, ship_x + 10, ship_y, ship_x, ship_y - 20)  # Spaceship

def draw_obstacles():
    for obstacle in obstacles:
        if obstacle['is_boss']:
            display.set_pen(PURPLE)
        else:
            display.set_pen(RED)
        screen_x, screen_y = project_3d_to_2d(obstacle['x'] - WIDTH // 2, obstacle['y'] - HEIGHT // 2, obstacle['z'])
        size = int(obstacle['size'] / obstacle['z'])
        display.circle(screen_x, screen_y, size)

def draw_projectiles():
    for projectile in projectiles:
        display.set_pen(projectile[3])  # Use the projectile's color
        screen_x, screen_y = project_3d_to_2d(projectile[0] - WIDTH // 2, projectile[1] - HEIGHT // 2, projectile[2])
        display.circle(screen_x, screen_y, 2)

def draw_power_ups():
    for power_up in power_ups:
        display.set_pen(GREEN)
        screen_x, screen_y = project_3d_to_2d(power_up[0] - WIDTH // 2, power_up[1] - HEIGHT // 2, power_up[2])
        size = int(5 / power_up[2])  # Scale size based on depth
        display.circle(screen_x, screen_y, size)

def draw_explosions():
    for explosion in explosions[:]:
        display.set_pen(explosion[4])
        screen_x, screen_y = project_3d_to_2d(explosion[0] - WIDTH // 2, explosion[1] - HEIGHT // 2, explosion[2])
        size = int(explosion[3] / explosion[2])
        display.circle(screen_x, screen_y, size)
        explosion[0] += explosion[6]  # Update x position based on velocity
        explosion[1] += explosion[7]  # Update y position based on velocity
        explosion[5] -= 1  # Decrease lifetime
        if explosion[5] <= 0:
            explosions.remove(explosion)

def update_obstacles():
    global obstacles, score, last_boss_score  # Declare global variables
    if not game_over:
        # Move obstacles closer
        for obstacle in obstacles:
            obstacle['z'] -= obstacle_speed  # Move along Z-axis
        # Remove off-screen obstacles
        obstacles = [obstacle for obstacle in obstacles if obstacle['z'] > 0.1]
        # Spawn new obstacles
        if random.randint(0, spawn_rate) == 0:
            if score % 100 == 0 and score != last_boss_score:
                x = random.randint(WIDTH // 4, 3 * WIDTH // 4)
                y = random.randint(0, HEIGHT)
                z = random.uniform(10.0, 15.0)
                size = 15  # Larger size for boss
                health = 10
                obstacles.append({'x': x, 'y': y, 'z': z, 'size': size, 'health': health, 'is_boss': True})
                last_boss_score = score
            else:
                side = random.choice(['left', 'right'])
                if side == 'left':
                    x = random.randint(0, WIDTH // 4)
                else:
                    x = random.randint(3 * WIDTH // 4, WIDTH)
                y = random.randint(0, HEIGHT)
                z = random.uniform(10.0, 15.0)
                size = 5
                health = 1
                obstacles.append({'x': x, 'y': y, 'z': z, 'size': size, 'health': health, 'is_boss': False})
        # Check for score
        for obstacle in obstacles:
            if obstacle['z'] <= 1.0:  # Obstacle passed the player
                score += 1

def update_projectiles():
    global projectiles, obstacles, explosions, score  # Declare global variables
    # Move projectiles away from the player
    projectiles = [projectile for projectile in projectiles if projectile[2] < 20.0]
    for projectile in projectiles:
        projectile[2] += 0.2  # Move along Z-axis
    # Check for collisions between projectiles and obstacles
    for projectile in projectiles[:]:
        for obstacle in obstacles[:]:
            distance = ((projectile[0] - obstacle['x']) ** 2 + (projectile[1] - obstacle['y']) ** 2) ** 0.5
            if distance < 10 + obstacle['size'] / obstacle['z']:
                if obstacle['is_boss']:
                    obstacle['health'] -= 1
                    if obstacle['health'] <= 0:
                        obstacles.remove(obstacle)
                        # Create big explosion
                        for _ in range(50):
                            vx = random.uniform(-2, 2)
                            vy = random.uniform(-2, 2)
                            explosions.append([obstacle['x'], obstacle['y'], obstacle['z'], 10, YELLOW, 20, vx, vy])
                        score += 100  # Increase score for defeating boss
                else:
                    obstacles.remove(obstacle)
                    # Create regular explosion
                    for _ in range(10):
                        vx = random.uniform(-1, 1)
                        vy = random.uniform(-1, 1)
                        explosions.append([obstacle['x'], obstacle['y'], obstacle['z'], 5, ORANGE, 10, vx, vy])
                    score += 10
                projectiles.remove(projectile)
                break

def update_power_ups():
    global power_ups, special_weapon_active, special_weapon_timer  # Declare global variables
    for power_up in power_ups:
        power_up[2] -= 0.1  # Move along Z-axis
    # Remove off-screen power-ups
    power_ups = [power_up for power_up in power_ups if power_up[2] > 0.1]
    # Check for power-up collection
    for power_up in power_ups[:]:
        distance = ((ship_x - power_up[0]) ** 2 + (ship_y - power_up[1]) ** 2) ** 0.5
        if distance < 15:  # Collect power-up
            special_weapon_active = True
            special_weapon_timer = special_weapon_duration
            power_ups.remove(power_up)
    # Spawn new power-ups
    if random.randint(0, 200) == 0:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        z = random.uniform(10.0, 15.0)
        power_ups.append([x, y, z])

def check_collision():
    global game_over  # Declare global variable
    if not game_over:
        for obstacle in obstacles:
            if obstacle['z'] <= 1.0:
                distance = ((ship_x - obstacle['x']) ** 2 + (ship_y - obstacle['y']) ** 2) ** 0.5
                if distance < 10 + obstacle['size'] / obstacle['z']:
                    game_over = True

def draw_score():
    display.set_pen(WHITE)
    display.text(f"Score: {score}", 10, 10, scale=2)

def draw_game_over():
    display.set_pen(WHITE)
    display.text("Game Over!", WIDTH // 2 - 50, HEIGHT // 2 - 10, scale=2)
    display.text("Press A to restart", WIDTH // 2 - 70, HEIGHT // 2 + 20, scale=1)

def auto_shoot():
    """Automatically shoot projectiles if the player is in front of an enemy."""
    global projectiles
    for obstacle in obstacles:
        # Check if the player is in front of the enemy (within a certain X range and Z distance)
        if abs(ship_x - obstacle['x']) < 20 and obstacle['z'] < 5:
            projectiles.append([ship_x, ship_y, 1.0, WHITE])  # Shoot a projectile
            break  # Shoot only once per frame

def game_loop():
    global ship_x, ship_y, special_weapon_active, special_weapon_timer, game_over  # Declare global variables
    while True:
        display.set_pen(BLACK)
        display.clear()
        
        # Draw starfield background
        draw_starfield()
        
        if not game_over:
            # Move ship left and right
            if button_a.is_pressed and ship_x > 20:
                ship_x -= ship_speed
            if button_b.is_pressed and ship_x < WIDTH - 20:
                ship_x += ship_speed
            
            # Move ship up and down with X and Y buttons
            if button_x.is_pressed and ship_y > 20:  # Move up
                ship_y -= ship_speed
            if button_y.is_pressed and ship_y < HEIGHT - 20:  # Move down
                ship_y += ship_speed
            
            # Automatically shoot if in front of an enemy
            auto_shoot()
            
            # Update game elements
            update_obstacles()
            update_projectiles()
            update_power_ups()
            
            # Check collision
            check_collision()
            
            # Draw elements
            draw_ship()
            draw_obstacles()
            draw_projectiles()
            draw_power_ups()
            draw_explosions()
            draw_score()
            
            # Update special weapon timer
            if special_weapon_active:
                special_weapon_timer -= 1
                if special_weapon_timer <= 0:
                    special_weapon_active = False
        else:
            draw_game_over()
            if button_a.is_pressed:
                reset_game()
        
        display.update()
        utime.sleep(0.02)

# Start the game
reset_game()
game_loop()
