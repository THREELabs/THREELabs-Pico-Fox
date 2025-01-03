# Stellar Strike

A space shooter adventure game for the Raspberry Pi Pico featuring a 3D starfield, obstacles, projectiles, and power-ups. Navigate through space, avoid incoming obstacles, and shoot your way through the galaxy!

## Features

- **3D Starfield Background**: Experience a realistic starfield with depth perception.
- **Ship Controls**: Maneuver your ship left and right to avoid obstacles.
- **Shooting Mechanics**: Fire projectiles at obstacles to score points.
- **Power-Ups**: Activate a special weapon to clear multiple obstacles at once.
- **Dynamic Obstacles**: Obstacles move towards you, increasing difficulty over time.
- **Explosions and Effects**: Watch obstacles explode in a burst of color.

## Installation

### Hardware Requirements

- Raspberry Pi Pico
- Pimoroni Pico Display
- Buttons connected to GPIO pins 12, 13, 14, and 15 (A, B, X, Y)
- Necessary cables and power supply

### Software Requirements

- MicroPython installed on the Raspberry Pi Pico
- Pimoroni libraries for Pico Display and buttons

### Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/stellar-strike.git
   ```

2. **Install Dependencies**

   Ensure you have the necessary libraries installed:

   ```bash
   pip install pimoroni-picographics pimoroni-button
   ```

3. **Upload the Code to Pico**

   Use Thonny or another MicroPython IDE to upload the `main.py` file to your Raspberry Pi Pico.

## How to Play

1. **Controls**

   - **A Button**: Move ship left
   - **B Button**: Move ship right
   - **Y Button**: Fire regular projectile
   - **X Button**: Activate special weapon (when available)

2. **Gameplay**

   - Navigate your ship through the starfield while avoiding obstacles.
   - Shoot obstacles to score points and clear the path.
   - Collect power-ups to activate the special weapon.
   - Watch out for incoming obstacles and avoid collisions.

3. **Special Weapon**

   - The special weapon clears multiple obstacles at once.
   - Use it wisely by pressing the X button when activated.

4. **Game Over**

   - If your ship collides with an obstacle, the game ends.
   - Press the A button to restart the game.

## Screenshots

![Stellar Strike Screenshot](screenshots/screenshot1.png)

## Scoring

- **Obstacle Avoidance**: +1 point per obstacle passed.
- **Obstacle Destruction**: +10 points per obstacle shot.
- **Power-Up Collection**: Activates the special weapon.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For inquiries, reach out to [your.email@example.com](mailto:your.email@example.com).

---

**Enjoy the adventure in Stellar Strike!** 🚀
