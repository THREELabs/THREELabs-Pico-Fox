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
GREEN = display.create_pen(0, 255, 0)  # Green for the ground
ORANGE = display.create_pen(255, 165, 0)
PURPLE = display.create_pen(128, 0, 128)
CYAN = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
BROWN = display.create_pen(139, 69, 19)
DARK_GRAY = display.create_pen(50, 50, 50)
LIGHT_GRAY = display.create_pen(200, 200, 200)
SKY_BLUE = (135, 206, 235)  # Light blue for the sky (RGB tuple)
HORIZON_BLUE = (0, 191, 255)  # Darker blue for the horizon (RGB tuple)

# Game variables
ship_x = WIDTH // 2
ship_y = HEIGHT // 2
ship_speed = 3
obstacles = []  # Each obstacle is a dictionary with x, y, z, size, health, is_boss
obstacle_speed = 0.1  # Increased speed for faster game pace
spawn_rate = 15  # Decreased rate for even more frequent spawning
projectiles = []  # Each projectile is a list [x, y, z, color]
power_ups = []  # Each power-up is a list [x, y, z]
explosions = []  # Each explosion is a list [x, y, z, size, color, lifetime, vx, vy]
special_weapon_active = False
special_weapon_duration = 500  # Duration of special weapon in frames
special_weapon_timer = 0
score = 0
game_over = False
last_boss_score = 0

# City background variables
buildings = []  # Each building is a dictionary with x, y, z, width, height, color
building_speed = 0.1  # Speed at which buildings move toward the player

# Collision distance threshold
MIN_COLLISION_DISTANCE = 3.0  # Enemies must be within this Z distance to be hit

# Ground variables
GROUND_Y = 0  # Ground level in 3D space
GROUND_HEIGHT = 20  # Height of the ground (grass) at the bottom of the screen

# Focal length for perspective projection
focal_length = 10

# Generate initial city buildings
def generate_city_background():
    global buildings
    buildings = []
    x = 0
    while x < WIDTH:
        width = random.randint(20, 60)
        height = random.randint(50, 150)  # Allow buildings to be taller
        z = random.uniform(10.0, 20.0)  # Start buildings farther away
        color = random.choice([DARK_GRAY, LIGHT_GRAY])
        buildings.append({
            "x": x, 
            "y": GROUND_Y,  # Set y to ground level in 3D space
            "z": z, 
            "width": width, 
            "height": height, 
            "color": color
        })
        x += width + random.randint(10, 30)

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
    generate_city_background()

def project_3d_to_2d(x, y, z):
    """Convert 3D coordinates to 2D screen coordinates using perspective projection."""
    if z == 0:
        z = 0.1  # Prevent division by zero
    screen_x = int(x / z * focal_length + WIDTH // 2)
    screen_y = int(-y / z * focal_length + HEIGHT - GROUND_HEIGHT)
    return screen_x, screen_y

def draw_sky_and_horizon():
    """Draw a gradient sky and horizon."""
    for y in range(HEIGHT - GROUND_HEIGHT):  # Stop before the ground
        # Interpolate between SKY_BLUE and HORIZON_BLUE based on the y position
        ratio = y / (HEIGHT - GROUND_HEIGHT)
        r = int(SKY_BLUE[0] * (1 - ratio) + HORIZON_BLUE[0] * ratio)
        g = int(SKY_BLUE[1] * (1 - ratio) + HORIZON_BLUE[1] * ratio)
        b = int(SKY_BLUE[2] * (1 - ratio) + HORIZON_BLUE[2] * ratio)
        color = display.create_pen(r, g, b)
        display.set_pen(color)
        display.line(0, y, WIDTH, y)

def draw_ground():
    """Draw the ground (grass) at the bottom of the screen."""
    display.set_pen(GREEN)
    display.rectangle(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)

def draw_city_background():
    """Draw the city background with moving buildings."""
    global buildings
    
    # Remove buildings that are too close to the player
    buildings = [building for building in buildings if building["z"] > 7.0]
    
    # Limit the number of buildings to 2
    visible_buildings = buildings[:2]
    
    for building in visible_buildings:
        # Update building position (move closer to the player)
        building["z"] -= building_speed
        
        # Only draw buildings that are far enough (z > 9.0)
        if building["z"] > 9.0:
            # Project base and top coordinates to 2D
            screen_x_base, screen_y_base = project_3d_to_2d(building["x"] - WIDTH // 2, building["y"], building["z"])
            screen_x_top, screen_y_top = project_3d_to_2d(building["x"] - WIDTH // 2, building["y"] + building["height"], building["z"])
            
            # Scale width based on depth
            width = int(building["width"] / building["z"] * focal_length)
            
            # Calculate height based on the difference in y coordinates
            height = screen_y_base - screen_y_top
            
            # Ensure height is positive
            if height < 0:
                height = 0
                
            # Clamp screen coordinates to screen boundaries
            screen_x = max(0, min(WIDTH, screen_x_base - width // 2))
            screen_y = max(0, min(HEIGHT, screen_y_top))
            screen_width = max(0, min(WIDTH - screen_x, width))
            screen_height = max(0, min(HEIGHT - screen_y, height))
            
            # Adjust screen_y to be slightly into the ground
            ground_overlap = 10
            screen_y += ground_overlap
            
            # Draw a white border around the building
            border_size = 2
            display.set_pen(WHITE)
            display.rectangle(screen_x - border_size, screen_y - border_size - ground_overlap, screen_width + 2 * border_size, screen_height + 2 * border_size)
            
            # Draw the building
            display.set_pen(building["color"])
            display.rectangle(screen_x, screen_y - ground_overlap, screen_width, screen_height)
            
            # Draw a doorway on the building (fixed position from bottom)
            door_width = 10
            door_height = 20
            door_x = screen_x + screen_width // 2 - door_width // 2
            door_y = screen_y + screen_height - door_height - screen_height // 3  # Position door 1/3 from bottom
            display.set_pen(BROWN)
            display.rectangle(door_x, door_y, door_width, door_height)
    
    # Only spawn new buildings if there are fewer than 2
    if len(buildings) < 2 and random.randint(0, 10) == 0:
        x = random.randint(0, WIDTH)
        z = random.uniform(15.0, 20.0)  # Start buildings further away
        width = random.randint(20, 60)
        height = random.randint(50, 150)
        color = random.choice([DARK_GRAY, LIGHT_GRAY])
        buildings.append({
            "x": x,
            "y": GROUND_Y,
            "z": z,
            "width": width,
            "height": height,
            "color": color
        })

def draw_ship():
    display.set_pen(YELLOW)
    display.triangle(ship_x - 10, ship_y, ship_x + 10, ship_y, ship_x, ship_y - 20)  # Spaceship

def draw_obstacles():
    for obstacle in obstacles:
        # Project coordinates
        screen_x, screen_y = project_3d_to_2d(obstacle['x'] - WIDTH // 2, obstacle['y'] - HEIGHT // 2, obstacle['z'])
        size = int(obstacle['size'] / obstacle['z'])
        
        if obstacle['is_boss']:
            # Draw boss monster (larger with wings and horns)
            display.set_pen(PURPLE)
            # Body
            display.circle(screen_x, screen_y, size)
            # Wings
            display.triangle(screen_x - size * 2, screen_y, screen_x, screen_y - size, screen_x, screen_y + size)  # Left wing
            display.triangle(screen_x + size * 2, screen_y, screen_x, screen_y - size, screen_x, screen_y + size)  # Right wing
            # Horns
            display.triangle(screen_x - size//2, screen_y - size, screen_x - size//4, screen_y - size * 1.5, screen_x, screen_y - size)
            display.triangle(screen_x + size//2, screen_y - size, screen_x + size//4, screen_y - size * 1.5, screen_x, screen_y - size)
            # Eyes
            display.set_pen(RED)
            display.circle(screen_x - size//3, screen_y - size//3, size//4)
            display.circle(screen_x + size//3, screen_y - size//3, size//4)
        else:
            # Draw regular flying monster
            display.set_pen(RED)
            # Body
            display.circle(screen_x, screen_y, size//2)
            # Wings
            display.triangle(screen_x - size, screen_y, screen_x, screen_y - size//2, screen_x, screen_y + size//2)  # Left wing
            display.triangle(screen_x + size, screen_y, screen_x, screen_y - size//2, screen_x, screen_y + size//2)  # Right wing
            # Eye
            display.set_pen(YELLOW)
            display.circle(screen_x, screen_y - size//4, size//4)

def draw_projectiles():
    for projectile in projectiles:
        display.set_pen(projectile[3])  # Use the projectile's color
        screen_x, screen_y = project_3d_to_2d(projectile[0] - WIDTH // 2, projectile[1], projectile[2])
        display.circle(screen_x, screen_y, 2)

def draw_power_ups():
    for power_up in power_ups:
        display.set_pen(GREEN)
        screen_x, screen_y = project_3d_to_2d(power_up[0] - WIDTH // 2, power_up[1], power_up[2])
        size = int(5 / power_up[2] * focal_length)
        display.circle(screen_x, screen_y, size)

def draw_explosions():
    for explosion in explosions[:]:
        display.set_pen(explosion[4])
        screen_x, screen_y = project_3d_to_2d(explosion[0] - WIDTH // 2, explosion[1], explosion[2])
        size = int(explosion[3] / explosion[2] * focal_length)
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
            # Only check for collisions if the obstacle is within the minimum distance
            if obstacle['z'] <= MIN_COLLISION_DISTANCE:
                distance = ((projectile[0] - obstacle['x']) ** 2 + (projectile[1] - obstacle['y']) ** 2) ** 0.5
                if distance < 10 + obstacle['size'] / obstacle['z'] * focal_length:
                    if obstacle['is_boss']:
                        obstacle['health'] -= 1
                        if obstacle['health'] <= 0:
                            obstacles.remove(obstacle)
                            # Create bigger, more dramatic boss explosion
                            for _ in range(100):  # More particles
                                vx = random.uniform(-3, 3)  # Faster particle speed
                                vy = random.uniform(-3, 3)
                                color = random.choice([YELLOW, ORANGE, RED])  # Multiple colors
                                explosions.append([obstacle['x'], obstacle['y'], obstacle['z'], 15, color, 30, vx, vy])
                            score += 100  # Increase score for defeating boss
                    else:
                        obstacles.remove(obstacle)
                        # Create more dramatic regular explosion
                        for _ in range(20):  # More particles
                            vx = random.uniform(-2, 2)  # Faster particle speed
                            vy = random.uniform(-2, 2)
                            color = random.choice([ORANGE, RED])  # Multiple colors
                            explosions.append([obstacle['x'], obstacle['y'], obstacle['z'], 8, color, 15, vx, vy])
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
                if distance < 10 + obstacle['size'] / obstacle['z'] * focal_length:
                    game_over = True

def draw_score():
    display.set_pen(WHITE)
    display.text(f"Score: {score}", 10, 10, scale=2)

def draw_game_over():
    display.set_pen(WHITE)
    display.text("Game Over!", WIDTH // 2 - 50, HEIGHT // 2 - 10, scale=2)
    display.text("Press A to restart", WIDTH // 2 - 70, HEIGHT // 2 + 20, scale=1)

# Shooting cooldown variables
last_shot_time = 0
SHOT_COOLDOWN = 1.0  # Time in seconds between shots

def auto_shoot():
    """Automatically shoot projectiles if near an enemy."""
    global projectiles, last_shot_time
    current_time = utime.time()
    
    # Check if enough time has passed since last shot
    if current_time - last_shot_time >= SHOT_COOLDOWN:
        for obstacle in obstacles:
            # Check if the player is near the enemy (within a certain range and Z distance)
            if abs(ship_x - obstacle['x']) < 30 and obstacle['z'] < 6:
                # Single projectile instead of spread
                projectiles.append([ship_x, ship_y, 1.0, WHITE])
                last_shot_time = current_time
                break  # Only shoot at one enemy at a time

def game_loop():
    global ship_x, ship_y, special_weapon_active, special_weapon_timer, game_over  # Declare global variables
    while True:
        # Draw sky and horizon
        draw_sky_and_horizon()
        
        # Draw ground
        draw_ground()
        
        # Draw obstacles (flying monsters) before buildings so they're visible
        draw_obstacles()
        
        # Draw city background
        draw_city_background()
        
        if not game_over:
            # Move ship up and down with A and X buttons
            if button_a.is_pressed and ship_y > 20:  # Move up
                ship_y -= ship_speed
            if button_x.is_pressed and ship_y < HEIGHT - 20:  # Move down
                ship_y += ship_speed
            
            # Move ship left and right with B and Y buttons
            if button_b.is_pressed and ship_x > 20:  # Move left
                ship_x -= ship_speed
            if button_y.is_pressed and ship_x < WIDTH - 20:  # Move right
                ship_x += ship_speed
            
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
