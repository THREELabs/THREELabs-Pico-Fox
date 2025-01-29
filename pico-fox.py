from machine import Pin, Timer
import utime
import random
import math
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
BLUE = display.create_pen(100, 100, 255)  # Lighter blue
RED = display.create_pen(255, 0, 0)
YELLOW = display.create_pen(255, 255, 0)
GREEN = display.create_pen(0, 255, 0)  # Green for the ground
ORANGE = display.create_pen(255, 165, 0)
PURPLE = display.create_pen(128, 0, 128)
CYAN = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
BROWN = display.create_pen(139, 69, 19)
DARK_GRAY = display.create_pen(50, 50, 50)
LIGHT_GRAY = display.create_pen(150, 150, 150)
TAN = display.create_pen(210, 180, 140)  # Tan color
DOOR_COLOR = display.create_pen(139, 69, 19)  # Brown color for doors
SIDE_GRAY = display.create_pen(100, 100, 100)  # Gray for the sides of the buildings
SKY_BLUE = (135, 206, 235)  # Light blue for the sky (RGB tuple)
HORIZON_BLUE = (0, 191, 255)  # Darker blue for the horizon (RGB tuple)

# Game variables
ship_x = WIDTH // 2
ship_y = HEIGHT // 2
ship_speed = 12  # Increased forward speed
up_down_speed = 6  # Slower up/down speed
left_right_speed = 6  # Slower left/right speed
speed_increment = 40  # Amount to increase speed each frame
max_speed = 100  # Maximum speed
ship_rotation = 0  # Track ship rotation angle
smoke_particles = []  # List to store smoke trail particles
explosions = []  # List to store explosion particles
game_over = False

# City background variables
buildings = []  # Each building is a dictionary with x, y, z, width, height, color
building_speed = 0.4  # Speed at which buildings move toward the player

# Ground variables
GROUND_Y = 0  # Ground level in 3D space
GROUND_HEIGHT = 20  # Height of the ground (grass) at the bottom of the screen
fixed_width = 40

# Focal length for perspective projection
focal_length = 10

# Generate initial city buildings
def generate_city_background():
    global buildings
    buildings = []
    x = 0
    while x < WIDTH:
        width = fixed_width
        height = random.randint(50, 150)  # Allow buildings to be taller
        z = random.uniform(10.0, 20.0)  # Start buildings farther away
        color = random.choice([LIGHT_GRAY, TAN])
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
    global ship_x, ship_y, game_over, explosions, ship_explosion_particles
    ship_x = WIDTH // 2
    ship_y = HEIGHT // 2
    game_over = False
    explosions = []  # Clear explosions
    ship_explosion_particles = []  # Clear ship explosion particles
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
    """Draw the ground (grass) at the bottom of the screen with fine animated speckles."""
    # Base grass color
    display.set_pen(GREEN)
    display.rectangle(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
    
    # Create more contrasting darker and lighter green colors for speckles
    dark_green = display.create_pen(0, 180, 0)  # Darker green for better visibility
    light_green = display.create_pen(20, 220, 20)  # Less bright light green
    
    # Add more numerous, finer speckles for subtle movement effect
    for _ in range(100):  # Increased number of speckles
        x = random.randint(0, WIDTH)
        y = random.randint(HEIGHT - GROUND_HEIGHT, HEIGHT)
        # Always use size 1 for finer detail
        display.set_pen(dark_green if random.random() < 0.5 else light_green)
        display.circle(x, y, 1)

def draw_city_background():
    """Draw the city background with moving buildings."""

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
            # Scale width based on depth
            
            # Calculate height based on the difference in y coordinates
            height = screen_y_base - screen_y_top
            
            # Ensure height is positive
            if height < 0:
                height = 0
                
            # Clamp screen coordinates to screen boundaries
            screen_x = max(0, min(WIDTH, screen_x_base - building["width"] // 2))
            screen_y = max(0, min(HEIGHT, screen_y_top))
            screen_width = max(0, min(WIDTH - screen_x, building["width"]))
            screen_height = max(0, min(HEIGHT - screen_y, height))
            
            # Adjust screen_y to be slightly into the ground
            ground_overlap = 10
            screen_y += ground_overlap
            
            # Draw the front of the building
            display.set_pen(building["color"])
            display.rectangle(screen_x, screen_y - ground_overlap, screen_width, screen_height)
            
            # Draw the side of the building
            display.set_pen(SIDE_GRAY)
            side_width = screen_width // 4  # Adjust the width of the side
            display.rectangle(screen_x + screen_width, screen_y - ground_overlap + side_width, side_width, screen_height - side_width)
    
    # Only spawn new buildings if there are fewer than 2
    if len(buildings) < 2 and random.randint(0, 10) == 0:
        x = random.randint(0, WIDTH)
        z = random.uniform(15.0, 20.0)  # Start buildings further away
        width = random.randint(30, 80)  # Increased variation in building width
        height = random.randint(60, 200)  # Increased variation in building height
        color = random.choice([DARK_GRAY, LIGHT_GRAY])
        buildings.append({
            "x": x,
            "y": GROUND_Y,
            "z": z,
            "width": width,
            "height": height,
            "color": color
        })

def update_smoke_particles():
    """Update and remove old smoke particles"""
    global smoke_particles
    for particle in smoke_particles[:]:
        particle[3] -= 1  # Decrease lifetime
        particle[0] += particle[4]  # Move x based on velocity
        particle[1] += particle[5]  # Move y based on velocity
        particle[6] = max(0, particle[6] - 2) # Decrease alpha (fade out)
        if particle[3] <= 0 or particle[6] <= 0:
            smoke_particles.remove(particle)

def create_smoke_particle(x, y, side):
    """Create a new smoke particle"""
    vx = random.uniform(-1, 1)
    vy = random.uniform(-0.5, 0.5)
    if side == 'left':
        vx += 1  # Drift right when tilting left
    else:
        vx -= 1  # Drift left when tilting right
    size = random.randint(2, 4)
    lifetime = random.randint(10, 20)
    alpha = 255 # Initial alpha value
    smoke_particles.append([x, y, size, lifetime, vx, vy, alpha])

def draw_ship():
    global ship_rotation
    
    # Update rotation based on movement
    if button_b.is_pressed:  # Left tilt
        ship_rotation = 30
        create_smoke_particle(ship_x - 20, ship_y + 10, 'left')
    elif button_y.is_pressed:  # Right tilt
        ship_rotation = -30    
    else:  # Return to center
        ship_rotation = 0
        
    # Create smoke particles continuously
    create_smoke_particle(ship_x, ship_y + 10, 'center')
    
    # Draw smoke particles with varying alpha
    for particle in smoke_particles:
        display.set_pen(display.create_pen(particle[6], particle[6], particle[6]))
        display.circle(int(particle[0]), int(particle[1]), particle[2])
    
    # Draw jet engine effects
    display.set_pen(ORANGE)
    for _ in range(3):
        flame_x = ship_x + random.randint(-3, 3)
        flame_y = ship_y + 12 + random.randint(0, 5)  # Moved flames closer to jet
        flame_size = random.randint(2, 4)
        display.circle(int(flame_x), int(flame_y), int(flame_size))
    
    # Create smoke particles when tilting
    if button_b.is_pressed:  # Left tilt
        create_smoke_particle(int(ship_x) - 20, int(ship_y) + 10, 'left')
    elif button_y.is_pressed:  # Right tilt
        create_smoke_particle(int(ship_x) + 20, int(ship_y) + 10, 'right')
    
    display.set_pen(BLUE)
    
    # Draw jet body
    if ship_rotation == 0:  # No tilt
        display.triangle(int(ship_x) - 15, int(ship_y) + 10, int(ship_x) + 15, int(ship_y) + 10, int(ship_x), int(ship_y) - 15)  # Main body
        # Wings
        display.triangle(int(ship_x) - 25, int(ship_y) + 5, int(ship_x) - 5, int(ship_y) + 5, int(ship_x) - 15, int(ship_y) - 5)  # Left wing
        display.triangle(int(ship_x) + 5, int(ship_y) + 5, int(ship_x) + 25, int(ship_y) + 5, int(ship_x) + 15, int(ship_y) - 5)  # Right wing
    elif ship_rotation > 0:  # Left tilt
        display.triangle(int(ship_x) - 10, int(ship_y) + 15, int(ship_x) + 20, int(ship_y) + 5, int(ship_x) + 5, int(ship_y) - 15)  # Main body
        # Wings
        display.triangle(int(ship_x) - 20, int(ship_y) + 10, int(ship_x), int(ship_y) + 10, int(ship_x) - 5, int(ship_y))  # Left wing
        display.triangle(int(ship_x) + 10, int(ship_y), int(ship_x) + 30, int(ship_y), int(ship_x) + 20, int(ship_y) - 10)  # Right wing
    else:  # Right tilt
        display.triangle(int(ship_x) - 20, int(ship_y) + 5, int(ship_x) + 10, int(ship_y) + 15, int(ship_x) - 5, int(ship_y) - 15)  # Main body
        # Wings
        display.triangle(int(ship_x) - 30, int(ship_y), int(ship_x) - 10, int(ship_y), int(ship_x) - 20, int(ship_y) - 10)  # Left wing
        display.triangle(int(ship_x), int(ship_y) + 10, int(ship_x) + 20, int(ship_y) + 10, int(ship_x) + 5, int(ship_y))  # Right wing

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

obstacle_speed = 0.2  # Add this line to control obstacle speed

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
                            for _ in range(150):  # Increased particle count
                                vx = random.uniform(-4, 4)  # Faster spread
                                vy = random.uniform(-4, 4)
                                color = display.create_pen(255, 140, 0)  # Single orange color
                                explosions.append([obstacle['x'], obstacle['y'], obstacle['z'], 10, color, 20, vx, vy])
                            score += 100  # Increase score for defeating boss
                    else:
                        obstacles.remove(obstacle)
                        # Create more dramatic regular explosion
                        for _ in range(50):  # Increased particle count
                            vx = random.uniform(-3, 3)  # Slower spread
                            vy = random.uniform(-3, 3)
                            color = display.create_pen(255, 69, 0)  # Single red-orange color
                            fragment_width = 3
                            fragment_height = 2
                            explosions.append([obstacle['x'], obstacle['y'], obstacle['z'], 6, color, 15, vx, vy, fragment_width, fragment_height])
                        score += 10
                    projectiles.remove(projectile)
                    break

def draw_explosions():
    """Draw explosion particles as circles with varying sizes and colors."""
    for particle in explosions:
        x, y, z, size, color, lifetime, vx, vy, _, _ = particle  # Ignore fragment_width and fragment_height
        # Project 3D coordinates to 2D screen coordinates
        screen_x, screen_y = project_3d_to_2d(x - WIDTH // 2, y, z)
        # Draw circles with some randomness in size
        display.set_pen(color)
        radius = random.randint(1, int(size))
        display.circle(int(screen_x + vx), int(screen_y + vy), radius)

def update_explosions():
    """Update explosion particles with culling and optimization."""
    global explosions
    new_explosions = []
    for particle in explosions:
        x, y, z, size, color, lifetime, vx, vy, fragment_width, fragment_height = particle
        
        # Cull particles that are off-screen
        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            continue
        
        # Reduce alpha value (fading effect)
        alpha = color.r
        if alpha > 5:
            alpha -= 5
            # Introduce some color variation
            if random.random() < 0.5:
                color = display.create_pen(alpha, max(0, color.g - 10), color.b)
            else:
                color = display.create_pen(alpha, color.g, min(255, color.b + 10))
        else:
            color = display.create_pen(0, color.g, color.b)
        
        # Update particle position and properties
        x += int(vx) * 2
        y += int(vy) * 2
        size = max(0, size - 0.05)
        lifetime -= 0.5
        
        # Add the particle to the new list if it has not expired
        if lifetime > 0 and size > 0:
            new_explosions.append([x, y, z, size, color, lifetime, vx, vy, fragment_width, fragment_height])
    explosions = new_explosions

def update_power_ups():
    global power_ups, special_weapon_active, special_weapon_timer
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

ship_explosion_particles = []

def check_collision():
    global game_over, explosions, ship_explosion_particles
    if not game_over:
        # Check collision with buildings
        for building in buildings:
            if 7.0 < building["z"] < 9.0:  # Only check buildings in front of player
                # Project building coordinates
                screen_x_base, screen_y_base = project_3d_to_2d(building["x"] - WIDTH // 2, building["y"], building["z"])
                screen_x_top, screen_y_top = project_3d_to_2d(building["x"] - WIDTH // 2, building["y"] + building["height"], building["z"])
                width = int(building["width"] / building["z"] * focal_length)
                height = screen_y_base - screen_y_top  # Calculate height
                
                # Check if ship is within building bounds
                if (screen_x_base - width // 2 < ship_x < screen_x_base + width // 2 and
                        screen_y_top < ship_y < screen_y_base):
                    game_over = True
                    # Create optimized ship explosion
                    for _ in range(300):  # Increased particle count for larger explosion
                        vx = random.uniform(-8, 8)  # Faster spread for larger explosion
                        vy = random.uniform(-8, 8)
                        size = random.randint(4, 12)  # Increased particle size for larger explosion
                        lifetime = random.randint(30, 70)  # Longer lifetime for fizzling effect
                        color = display.create_pen(255, 255, 0)  # Yellow color for explosion
                        angle = random.uniform(0, 2 * math.pi)
                        fragment_width = size * math.cos(angle)
                        fragment_height = size * math.sin(angle)
                        ship_explosion_particles.append([ship_x, ship_y, 1.0, size, color, lifetime, vx, vy, fragment_width, fragment_height])

                    # Create optimized building explosion
                    for _ in range(200):  # Increased particle count
                        vx = random.uniform(-5, 5)
                        vy = random.uniform(-5, 5)
                        size = random.randint(4, 10)  # Vary particle size
                        lifetime = random.randint(20, 50)
                        color = random.choice([display.create_pen(255, 69, 0), display.create_pen(255, 165, 0)])  # Vary color
                        angle = random.uniform(0, 2 * math.pi)
                        fragment_width = size * math.cos(angle)
                        fragment_height = size * math.sin(angle)
                        explosions.append([ship_x, ship_y, building["z"], size, color, lifetime, vx, vy, fragment_width, fragment_height])

def update_ship_explosion_particles():
    """Update ship explosion particles with culling."""
    global ship_explosion_particles
    new_particles = []
    for particle in ship_explosion_particles:
        x, y, z, size, color, lifetime, vx, vy = particle

        # Cull particles that are off-screen
        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            continue

        # Reduce alpha value (fading effect)
        alpha = color.r
        if alpha > 10:
            alpha -= 10
            color = display.create_pen(alpha, color.g, color.b)
        else:
            color = display.create_pen(0, color.g, color.b)

        # Update particle position and properties
        x += vx * 2  # Increased velocity
        y += vy * 2  # Increased velocity
        size = max(0, size - 0.2)  # Faster size reduction
        lifetime -= 1  # Faster expiration

        # Add the particle to the new list if it has not expired
        if lifetime > 0 and size > 0:
            # Rotate the fragment
            angle = random.uniform(0, 2 * math.pi)
            fragment_width = size * math.cos(angle)
            fragment_height = size * math.sin(angle)
            new_particles.append([x, y, z, size, color, lifetime, vx, vy, fragment_width, fragment_height])
    ship_explosion_particles = new_particles

def draw_ship_explosion():
    """Draw ship explosion particles."""
    for particle in ship_explosion_particles:
        x, y, z, size, color, lifetime, vx, vy, fragment_width, fragment_height = particle
        # Project 3D coordinates to 2D screen coordinates
        screen_x, screen_y = project_3d_to_2d(x - WIDTH // 2, y, z)
        # Draw the fragment
        display.set_pen(color)
        display.rectangle(int(screen_x - fragment_width / 2), int(screen_y - fragment_height / 2), int(fragment_width), int(fragment_height))

def draw_game_over():
    display.set_pen(WHITE)
    display.text("Game Over!", WIDTH // 2 - 50, HEIGHT // 2 - 10, scale=2)
    display.text("Press A to restart", WIDTH // 2 - 70, HEIGHT // 2 + 20, scale=1)

def game_loop():
    global ship_x, ship_y, game_over, ship_speed, max_speed
    
    while True:
        # Draw sky and horizon
        draw_sky_and_horizon()
        
        # Draw ground
        draw_ground()
        
        if not game_over:
            # Increase ship speed over time
            if ship_speed < max_speed:
                ship_speed += speed_increment
            
            # Move ship up and down with A and X buttons
            if button_a.is_pressed and ship_y > 20:  # Move up
                ship_y -= up_down_speed
            if button_x.is_pressed and ship_y < HEIGHT - 20:  # Move down
                ship_y += up_down_speed
            
            # Move ship left and right with B and Y buttons
            if button_b.is_pressed and ship_x > 20:  # Move left
                ship_x -= left_right_speed
            if button_y.is_pressed and ship_x < WIDTH - 20:  # Move right
                ship_x += left_right_speed
            
            # Update smoke particles
            update_smoke_particles()
            
            # Update obstacle explosions
            update_explosions()
            
            # Update ship explosion particles
            update_ship_explosion_particles()
            
            # Check collision
            check_collision()
        
        # Draw city background
        draw_city_background()
        
        # Draw elements
        if not game_over:
            draw_ship()
        
        # Draw explosions
        draw_explosions()
        
        # Draw ship explosion
        draw_ship_explosion()
        
        if game_over:
            draw_game_over()
            if button_a.is_pressed:
                reset_game()
        
        display.update()
        utime.sleep(0.02)

# Start the game
reset_game()
game_loop()