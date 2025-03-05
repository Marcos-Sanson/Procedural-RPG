# Procedurally-Generated 2D Role-Playing Game (RPG)

## Overview

A 2D role-playing game (RPG) where players control a customizable character navigating through procedurally-generated terrains filled with interactive objects and water bodies. The game features random encounters, quest-driven gameplay, and combat mechanics involving various creatures and monsters. 

This game was developed as a team project to explore game development using Python and Pygame. The game is designed to be expanded with regular updates and feature enhancements.

## Features

### Current Release:
- Character movement using arrow keys or WASD
- Collision detection with water and objects
- Randomly generated terrain with water bodies
- Randomly generated objects with collision detection
- Randomly generated enemies with health systems and defeat animations
- Proper weapon combat with cooldowns
- Multiple weapon types, damages, and ranges
- Weapon images for each type
- Health bars for enemies

### Planned Features:
- Character customization
- Quest system with objectives and rewards
- Inventory management
- NPC dialogue system
- Day/night cycle affecting gameplay
- More enemy types with unique behaviors
- Boss battles

## Getting Started

### Prerequisites
- Python 3.7+
- Pygame 2.0+

### Installation
1. Clone the repository:
    ```
    git clone https://github.com/yourusername/Procedural-RPG.git
    ```
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Run the game:
    ```
    python main.py
    ```

### Controls
- Move: Arrow keys or WASD
- Attack: Space bar
- Interact: E
- Open inventory: I

## Development

This game was developed using Python and the Pygame library. It follows a waterfall development model, starting with prototyping and iterative development, progressing through testing, and finally delivering the finished product with regular updates.

### Key Technologies:
- **Python**: Primary language for development
- **Pygame**: Game development library used for rendering graphics, managing events, and handling user input
- **Git**: Version control for code management

### Project Structure
- `main.py` - Game entry point
- `player.py` - Player character class and mechanics
- `terrain.py` - Procedural terrain generation
- `enemies.py` - Enemy classes and AI
- `weapons.py` - Weapon system implementation
- `assets/` - Game assets (images, sounds)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments
- Thanks to all team members who contributed to this project
- Pygame community for their excellent documentation and support
