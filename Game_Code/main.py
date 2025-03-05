"""
CIS 350 - Introduction to Software Engineering  
Winter 2024 Semester Project  

Procedurally-Generated 2D Role-Playing Game  

Authors:  
- Marcos Sanson  
- Jerod Muilenburg  
- William Krol  
- Brendon Do  
- Ely Miller  

Project Overview:  
This project is a procedurally-generated 2D RPG game where players  
navigate a dynamic environment with interactive elements. The game  
features terrain generation, combat mechanics, and an inventory  
system, all built using Python and Pygame.  

Features:  
- Character movement using Arrow Keys / WASD  
- Collision detection for water, objects, and enemies  
- Procedurally-generated terrain with lakes, forests, and obstacles  
- Combat system with melee attacks and health management  
- Dynamic weapon inventory with multiple weapon types  
- Room transitions and map regeneration using the Enter key
- Optimized performance for smooth gameplay  

Development Credits:  
- Original sprite movement code: Dr. Byron DeVries  
- Artwork & Sprites: Game Endeavor's Mystic Woods asset pack (Free Version)  
  https://game-endeavor.itch.io/mystic-woods  

Date: February 6, 2024
"""
import pygame
import asyncio
import random
import time

class Player:
    """
    A class representing the player character in the game.

    The player is the main controllable character that can move around the world,
    equip weapons, manage inventory, and interact with enemies.

    Attributes:
        inventory (list): List of weapons the player can carry
        HP (int): Player's current health points
        tool (Weapon): Currently equipped weapon
        damage (int): Current attack damage value
        range (int): Current attack range
        x (int): Player's x coordinate position
        y (int): Player's y coordinate position
    """
    def __init__(self, HP, x, y):
        """
        Initializes player attributes and inventory system.

        The player starts with empty inventory and no equipped weapon. Initial position 
        and health points are set based on input parameters.

        Args:
            HP (int): Player's starting health points/hit points
            x (int): Player's initial x-coordinate position on the game map
            y (int): Player's initial y-coordinate position on the game map

        Returns:
            None

        Example:
            player = Player(100, 50, 50)  # Creates player with 100 HP at position (50,50)
        """
        self.inventory = []
        self.HP = HP
        self.tool = None
        self.damage = 0
        self.range = 0
        self.x = x
        self.y = y

    def get_inventory(self):
        """
        Gets the player's inventory.

        Returns:
            list: Player's inventory.
        """
        return self.inventory
    
    def add_inventory(self, item):
        """
        Adds a weapon to the player's inventory.

        Args:
            item (Weapon): Weapon to add.
        """
        self.inventory.append(item)
    
    def set_tool(self, num):
        """
        Equips a weapon from inventory.

        Args:
            num (int): Index of the weapon.
        """
        self.tool = self.inventory[num]
        self.set_damage()
    
    def get_tool(self):
        """
        Gets the equipped weapon.

        Returns:
            Weapon: Equipped weapon.
        """
        return self.tool
    
    def get_inventory_size(self):
        """
        Gets the number of items in inventory.

        Returns:
            int: Inventory size.
        """
        return len(self.inventory)
    
    def set_damage(self):
        """
        Sets the player's damage based on equipped weapon.
        """
        if self.tool:
            self.damage = self.tool.get_damage()
    
    def get_damage(self):
        """
        Gets the player's damage value.

        Returns:
            int: Damage stat.
        """
        return self.damage
    
    def get_cooldown(self):
        """
        Gets the cooldown time of the equipped weapon.

        Returns:
            int: Cooldown duration.
        """
        return self.tool.get_cooldown()
    
    def get_range(self):
        """
        Gets the attack range of the equipped weapon.

        Returns:
            int: Weapon range.
        """
        return self.tool.get_range()


class Enemy:
    """
    Represents an enemy character in the game world.

    The Enemy class defines attributes and behaviors for hostile entities that can
    interact with the player. Enemies have health points and position coordinates.

    Attributes:
        HP (int): Current health points of the enemy
        x (int): X-coordinate position on the game map
        y (int): Y-coordinate position on the game map
    """
    def __init__(self, HP, x, y):
        """
        Initializes enemy attributes.

        Args:
            HP (int): Enemy's health points.
            x (int): Enemy's horizontal position.
            y (int): Enemy's vertical position.
        """
        self.HP = HP
        self.x = x
        self.y = y


class Weapon:
    """
    Represents a weapon that can be equipped and used by the player for combat.

    A weapon has properties like damage, cooldown time, and attack range that affect
    how it performs in combat. Each weapon also has an associated image and scale
    for rendering purposes.

    Attributes:
        name: The name/type of the weapon
        damage: Amount of damage dealt to enemies per hit
        cooldown: Time delay between attacks in frames
        reach: Maximum distance the weapon can hit enemies from
        img: File path to the weapon's sprite image
        scale: Size multiplier for rendering the weapon sprite
    """
    def __init__(self, name, damage, cooldown, reach, img, scale):
        """
        Holds information for the weapons in the game.

        Args:
            name (string): Name of the weapon.
            damage (int): How much damage the weapon deals to enemies.
            cooldown (int): Amount of time before the
            weapon can be swung again.
            reach (int): How far the player can be to attack the enemy.
            img (string): The image of the weapon.
            scale (int): How to scale the weapon to the player model.
        """
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.reach = reach
        self.img = img
        self.scale = scale

    def get_damage(self):
        """
        Gets the weapon's damage stat.

        Returns:
            int: Damage value.
        """
        return self.damage
    
    def get_cooldown(self):
        """
        Gets the weapon's cooldown duration.

        Returns:
            int: Cooldown time.
        """
        return self.cooldown
    
    def get_range(self):
        """
        Gets the weapon's attack range.

        Returns:
            int: Range value.
        """
        return self.reach
    
    def get_img(self):
        """
        Gets the file path of the weapon image.

        Returns:
            str: Image file path.
        """
        return self.img
    
    def get_scale(self):
        """
        Gets the scaling factor of the weapon.

        Returns:
            int: Scale factor.
        """
        return self.scale


async def main(seed):
    """
    Main function to run the game loop.

    This function initializes the game world, handles player input, manages rendering,
    collision detection, enemy behaviors and all game state updates. It runs in an
    asynchronous loop using asyncio.

    Args:
        seed (int): Random seed used for procedural generation of terrain, enemy
            placement, and object placement. The same seed will generate identical
            worlds.

    Returns:
        None

    Raises:
        pygame.error: If game initialization or resource loading fails
        
    Example:
        asyncio.run(main(seed=42))  # Starts game with seed 42
    """
    pygame.init()  # Initialize Pygame

    # Generate a unique, short seed if none is provided
    if seed is None:
        seed = int(str(int(time.time() * 10000))[-5:])

    # Print game introduction and controls
    print("\n===== Welcome to the Procedurally-Generated Role-Playing Game! =====")
    print("You wake up in a mysterious land, surrounded by unknown dangers.")
    print("Explore the world, find weapons and treasure, and fight enemies to survive!\n")
    print("======== Controls ========")
    print("Move: Arrow Keys or WASD")
    print("Attack: Z or Spacebar")
    print("Switch Weapon: 1-4")
    print("New Map: Enter")
    print("Quit: Q\n")
    print(f"Current World Seed: {seed}")
    print("==========================\n")

    # Set the window title dynamically with the seed
    pygame.display.set_caption(f"Procedural Role-Playing Game (Seed: {seed})")
    
    p1 = Player(100, 50, 50)

    """
    Initialize weapon objects with their properties.

    Each weapon is defined with specific attributes:
        - Name - String identifier of the weapon type
        - Damage - Integer value representing hit points of damage dealt
        - Cooldown - Integer frames between allowed attacks (60fps)
        - Range - Integer pixels for attack reach from player position 
        - Image - String file path for weapon sprite
        - Scale - Integer size multiplier for sprite rendering
    """
    # Balanced starting weapon: Medium damage, speed and range
    # name="Sword", damage=1, cooldown=25 frames, range=60 pixels
    sword = Weapon("Sword", 1, 25, 60, 'sword.png', 50)  
    
    # Heavy weapon: High damage but slow attack speed and short range
    # name="Mace", damage=3, cooldown=60 frames, range=25 pixels  
    mace = Weapon("Mace", 3, 60, 25, 'mace.png', 50)  
    
    # Long-range weapon: Moderate damage and attack speed with extended reach
    # name="Spear", damage=2, cooldown=40 frames, range=100 pixels
    spear = Weapon("Spear", 2, 40, 100, 'spear.png', 60)  
    
    # Quick weapon: Fast attack speed but low damage
    # name="Knife", damage=0.75, cooldown=17 frames, range=50 pixels
    knife = Weapon("Knife", .75, 17, 50, 'knife.png', 50)  

    # Adding weapons to player's inventory
    p1.add_inventory(sword)
    p1.add_inventory(mace)
    p1.add_inventory(spear)
    p1.add_inventory(knife)
    # Setting the default weapon to the first item (in this case the sword)
    p1.set_tool(0)

    random.seed(seed)  # Set the random seed

    clock = pygame.time.Clock()
    # Make the window resizable
    screen = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)
    delta = 5
    x = y = 0

    # Load character image
    character_img = pygame.image.load('Assets/character.png').convert_alpha()
    
    # Scale character image for better visibility
    character_img = pygame.transform.scale(character_img, (60, 80))
    character_rect = character_img.get_rect()

    # Function to load weapon image based on the currently equipped tool
    def load_weapon():
        """
        Loads and scales the image of the currently equipped weapon.

        Retrieves the weapon image path from the currently equipped tool,
        loads the image file, and scales it according to the weapon's 
        defined scale factor.

        Returns:
            tuple:
            - weapon_img (pygame.Surface): The scaled weapon sprite surface
            - weapon_rect (pygame.Rect): The rectangular bounds of the weapon sprite
            
        Raises:
            pygame.error: If weapon image file cannot be loaded
        """
        scale = p1.get_tool().get_scale()  # Retrieve weapon scale
        weapon_img = pygame.image.load(f'Assets/{p1.get_tool().get_img()}').convert_alpha()
        weapon_img = pygame.transform.scale(weapon_img, (scale, scale))
        weapon_rect = weapon_img.get_rect()
        return weapon_img, weapon_rect

    # Load weapon slash effect images
    weapon_slash_imgs = [
        pygame.transform.scale(pygame.image.load('Assets/slash.png').convert_alpha(), (40, 40)),
        pygame.transform.scale(pygame.image.load('Assets/slash.png').convert_alpha(), (30, 30))
    ]

    # Load enemy images
    enemy_img1 = pygame.image.load('Assets/enemy1.png').convert_alpha()
    enemy_img1 = pygame.transform.scale(enemy_img1, (60, 60))  # Resize for consistency

    enemy_img2 = pygame.image.load('Assets/enemy2.png').convert_alpha()
    enemy_img2 = pygame.transform.scale(enemy_img2, (60, 60))  # Resize for consistency

    # Load enemy death animation frames
    enemy_death_imgs = [
        pygame.transform.scale(pygame.image.load('Assets/enemy_death1.png').convert_alpha(), (180, 240)),
        pygame.transform.scale(pygame.image.load('Assets/enemy_death2.png').convert_alpha(), (180, 240))
    ]
    
    enemy_hp = []  # Initialize enemy health tracking list

    # Load object images
    object_img = pygame.image.load('Assets/object.png').convert_alpha()
    object_img = pygame.transform.scale(object_img, (50, 50))  # Scale for consistency

    object_collision_img = pygame.image.load('Assets/object_collision.png').convert_alpha()
    object_collision_img = pygame.transform.scale(object_collision_img, (50, 50))  # Scale for consistency

    # Load terrain images
    grass_img = pygame.image.load('Assets/grass.png').convert_alpha()
    water_img = pygame.image.load('Assets/water.png').convert_alpha()
    
    tile_size = (32, 32)  # Define tile size for terrain rendering

    # Load custom water outline image for better visibility of water edges
    water_outline_img = pygame.image.load('Assets/water_outline.png').convert_alpha()
    water_outline_img = pygame.transform.scale(water_outline_img, tile_size)

    # Generate random terrain grid based on seed with clusters of water
    terrain_grid = [[grass_img for _ in range(25)] for _ in range(20)]
    num_clusters = random.randint(3, 5)  # Random number of clusters
    for _ in range(num_clusters):
        cluster_size = random.randint(2, 7)  # Random size for each cluster
        # Random x position for the cluster
        cluster_x = random.randint(0, len(terrain_grid[0]) - cluster_size)
        # Random y position for the cluster
        cluster_y = random.randint(0, len(terrain_grid) - cluster_size)
        for i in range(cluster_y, cluster_y + cluster_size):
            for j in range(cluster_x, cluster_x + cluster_size):
                terrain_grid[i][j] = water_img

    # Add outline markers around water tiles for collision detection.
    # This creates a visual and functional border around water bodies by marking adjacent grass tiles.
    # Original implementation inspired by Marcus Møller's tilemap engine
    # See: https://github.com/marcusmoller/pyweek17-miner/blob/master/miner/engine.py#L202-L220
    for i in range(len(terrain_grid)):
        for j in range(len(terrain_grid[0])):
            if terrain_grid[i][j] == water_img:
                # Check each cardinal direction (N,S,E,W) around water tiles
                # Mark grass tiles adjacent to water as "outline" for collision detection
                
                # Check tile above (North)
                if i > 0 and terrain_grid[i - 1][j] == grass_img:
                    terrain_grid[i - 1][j] = "outline"
                    
                # Check tile below (South)    
                if i < len(terrain_grid) - 1 and terrain_grid[i + 1][j] == grass_img:
                    terrain_grid[i + 1][j] = "outline"
                    
                # Check tile to left (West)
                if j > 0 and terrain_grid[i][j - 1] == grass_img:
                    terrain_grid[i][j - 1] = "outline"
                    
                # Check tile to right (East)
                if j < len(terrain_grid[0]) - 1 and terrain_grid[i][j + 1] == grass_img:
                    terrain_grid[i][j + 1] = "outline"

    # Generate random positions for objects that will be placed in the game world
    num_objects = random.randint(1, 4)  # Generate 1-4 random objects on the map
    object_positions = []  # List to store (x,y) coordinates of each object
    object_collided = []  # Boolean list tracking if objects have been collided with
    
    # Create and position each object
    for _ in range(num_objects):
        # Calculate random grid positions and convert to pixel coordinates
        object_x = random.randint(0, len(terrain_grid[0]) - 1) * tile_size[0]  
        object_y = random.randint(0, len(terrain_grid) - 1) * tile_size[1]
        
        # Add the object's position tuple to the list
        object_positions.append((object_x, object_y))
        
        # Initialize collision state as False for the new object
        object_collided.append(False)  # Will be set to True when player collides

    # Generate random enemy positions and initialize tracking lists
    num_enemies = random.randint(1, 3)  # Generate 1-3 enemies 
    enemy_positions = []  # List to store (x,y) coordinates of each enemy
    enemy_collided = []  # Tracks if each enemy has been hit by player
    for _ in range(num_enemies):
        # Calculate random grid positions and convert to pixel coordinates
        enemy_x = random.randint(0, len(terrain_grid[0]) - 1) * tile_size[0]
        enemy_y = random.randint(0, len(terrain_grid) - 1) * tile_size[1]
        enemy_positions.append((enemy_x, enemy_y))  # Store position tuple
        enemy_hp.append(10)  # Set initial health points
        enemy_collided.append(False)  # Initialize collision state

    def attack_animation():
        """
        Renders weapon slash animation during player attacks.
        
        Uses system time to cycle through slash animation frames.
        Scales and blits the current animation frame to screen.
        """
        # Get current animation frame based on time
        attack_index = (pygame.time.get_ticks() // 200) % len(weapon_slash_imgs)
        print("'slash'")  # Debug output for attack
        # Scale current slash frame
        slash_imgs = pygame.transform.scale(weapon_slash_imgs[attack_index],
                                         (60, 60))
        # Draw slash effect
        screen.blit(slash_imgs, r)

    # Initialize combat system variables
    cooldown = True  # Track if weapon can be used
    timer = 0  # Countdown between attacks
    w, r = load_weapon()  # Load initial weapon graphics
    forward = True  # Track player facing direction

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            # Regenerate map when ENTER is pressed (without restarting the game)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                new_seed = int(str(int(time.time() * 10000))[-5:])  # Extracts last 5 digits for a more readable seed
                print(f"Regenerating map with new seed: {new_seed}")  
                random.seed(new_seed)  # Apply new seed
                pygame.display.set_caption(f"Procedural Role-Playing Game (Seed: {new_seed})")  # Update window title

                # Regenerate terrain with improved water generation
                terrain_grid = [[grass_img for _ in range(25)] for _ in range(20)]

                num_clusters = random.randint(3, 5)  # Number of water bodies

                for _ in range(num_clusters):
                    cluster_size = random.randint(3, 7)  # Random size for each water body
                    cluster_x = random.randint(0, len(terrain_grid[0]) - cluster_size)
                    cluster_y = random.randint(0, len(terrain_grid) - cluster_size)

                    # Decide if this will be a circular lake or a rectangular pool
                    if random.random() < 0.5:  # 50% chance of circular lake
                        radius = cluster_size // 2
                        center_x = cluster_x + radius
                        center_y = cluster_y + radius

                        for i in range(len(terrain_grid)):
                            for j in range(len(terrain_grid[0])):
                                # Circle formula: (x - cx)^2 + (y - cy)^2 < r^2
                                if (i - center_y) ** 2 + (j - center_x) ** 2 < radius ** 2:
                                    terrain_grid[i][j] = water_img

                    else:  # Otherwise, make an irregular pool (blocky but distorted)
                        for i in range(cluster_y, cluster_y + cluster_size):
                            for j in range(cluster_x, cluster_x + cluster_size):
                                if random.random() > 0.2:  # Add some randomness to edges
                                    terrain_grid[i][j] = water_img

                # Add outline to water tiles for collision detection
                for i in range(len(terrain_grid)):
                    for j in range(len(terrain_grid[0])):
                        if terrain_grid[i][j] == water_img:
                            # Check neighbors for grass tiles directly adjacent to water
                            if i > 0 and terrain_grid[i - 1][j] == grass_img:
                                terrain_grid[i - 1][j] = "outline"
                            if i < len(terrain_grid) - 1 and terrain_grid[i + 1][j] == grass_img:
                                terrain_grid[i + 1][j] = "outline"
                            if j > 0 and terrain_grid[i][j - 1] == grass_img:
                                terrain_grid[i][j - 1] = "outline"
                            if j < len(terrain_grid[0]) - 1 and terrain_grid[i][j + 1] == grass_img:
                                terrain_grid[i][j + 1] = "outline"
                
                # Regenerate objects on map reset
                num_objects = random.randint(1, 4)  # Random number of objects between 1-4
                object_positions = []  # List to store (x,y) coordinates of objects
                object_collided = []   # Tracks collision state for each object
                for _ in range(num_objects):
                    # Calculate random grid positions and convert to pixel coordinates
                    object_x = random.randint(0, len(terrain_grid[0]) - 1) * tile_size[0]
                    object_y = random.randint(0, len(terrain_grid) - 1) * tile_size[1]
                    object_positions.append((object_x, object_y))  # Add position tuple
                    object_collided.append(False)  # Initialize collision state as False

                # Regenerate enemies on map reset 
                num_enemies = random.randint(1, 3)  # Random number of enemies between 1-3
                enemy_positions = []    # List to store (x,y) coordinates of enemies
                enemy_hp = []          # List to track enemy health points
                for _ in range(num_enemies):
                    # Calculate random grid positions and convert to pixel coordinates
                    enemy_x = random.randint(0, len(terrain_grid[0]) - 1) * tile_size[0]
                    enemy_y = random.randint(0, len(terrain_grid) - 1) * tile_size[1]
                    enemy_positions.append((enemy_x, enemy_y))  # Add position tuple
                    enemy_hp.append(10)  # Set initial enemy HP to 10

        # Get the attack range of currently equipped weapon
        reach = p1.get_range()

        # Get current keyboard state
        keys = pygame.key.get_pressed()
        
        # Store potential new position, will be validated before applying
        new_x, new_y = x, y

        # Handle movement inputs (WASD and arrow keys)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= delta  # Move left
            forward = False # Face left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += delta  # Move right  
            forward = True  # Face right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= delta  # Move up
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += delta  # Move down

        # Quit game if Q is pressed
        if keys[pygame.K_q]:
            return

        # Handle attack inputs (Z or Spacebar)
        if keys[pygame.K_z] or keys[pygame.K_SPACE]:
            # Check each enemy position
            for index, (i, j) in enumerate(enemy_positions):
            # If enemy is in weapon range and weapon isn't on cooldown
                if x - reach < i < x + reach and y - reach < j < y + reach and cooldown:
                    enemy_hp[index] -= p1.get_damage()  # Apply damage
                    cooldown = False  # Start weapon cooldown
                    timer = p1.get_cooldown()  # Set cooldown duration

        # Handle weapon cooldown timer
        if not cooldown:
            timer -= 1  # Decrement the cooldown timer each frame
            if timer <= 0:
                cooldown = True  # Reset cooldown when timer expires

        # Weapon selection system - number keys 1-4 switch between weapons in inventory
        if keys[pygame.K_1]:
            p1.set_tool(0)  # Select first weapon (sword)
            w, r = load_weapon()  # Reload weapon graphics for the new selection
        if keys[pygame.K_2]:
            if p1.get_inventory_size() < 2:
                print("No item present")  # Prevent selecting non-existent inventory items
            else:
                p1.set_tool(1)  # Select second weapon (mace)
                w, r = load_weapon()  # Update weapon graphics
        if keys[pygame.K_3]:
            if p1.get_inventory_size() < 3:
                print("No item present")  # Error handling for inventory bounds
            else:
                p1.set_tool(2)  # Select third weapon (spear)
                w, r = load_weapon()  # Reload weapon sprite and hitbox
        if keys[pygame.K_4]:
            if p1.get_inventory_size() < 4:
                print("No item present")  # Inventory access validation
            else:
                p1.set_tool(3)  # Select fourth weapon (knife)
                w, r = load_weapon()  # Update weapon display

        # Check for out-of-bounds movement
        new_x = max(0, min(new_x, screen.get_width() - character_rect.width))
        new_y = max(0, min(new_y, screen.get_height() - character_rect.height))

        # Improved water collision detection
        collision_with_water = False
        scaled_tile_size = (screen.get_width() / len(terrain_grid[0]),
                            screen.get_height() / len(terrain_grid))

        # Create a slightly smaller collision box for the character
        character_collision_box = pygame.Rect(
            new_x + 15,  # Increased offset from left edge
            new_y + 60,  # Increased offset from top edge 
            character_rect.width - 30,  # Further reduce width
            character_rect.height - 70  # Further reduce height
        )

        # Track how many water tiles are actually colliding
        water_collision_count = 0
        max_allowed_water_collisions = 2  # Allow minimal water tile contacts

        # Iterate through each row in the terrain grid
        for i in range(len(terrain_grid)):
            # Iterate through each column in the current row
            for j in range(len(terrain_grid[0])):
                # Only check collision for water tiles, not outline markers
                if terrain_grid[i][j] == water_img:
                    # Create a rectangular collision box for the current water tile
                    # scaled_tile_size adapts the collision box to the window dimensions
                    water_rect = pygame.Rect(
                    j * scaled_tile_size[0],  # X position based on column index
                    i * scaled_tile_size[1],  # Y position based on row index
                    scaled_tile_size[0],      # Width scaled to current window size
                    scaled_tile_size[1]       # Height scaled to current window size
                    )
                    
                    # Check if player's collision box overlaps with this water tile
                    if character_collision_box.colliderect(water_rect):
                        # Count how many water tiles are being touched simultaneously
                        water_collision_count += 1
                    
                    # Allow player to touch edges of water (max_allowed_water_collisions)
                    # This creates more natural movement around water bodies
                    if water_collision_count > max_allowed_water_collisions:
                        collision_with_water = True  # Too many water tiles touched, block movement
                        break  # Exit the column loop early for efficiency
                
                # If water collision detected, exit the row loop as well
                if collision_with_water:
                    break

        # Update character position only if no water collision
        if not collision_with_water:
            x, y = new_x, new_y
            character_rect.topleft = (x, y)
            r.topleft = (x + 30, y + 15)

        # Check for collision with objects
        for i, object_pos in enumerate(object_positions):
            # Only check collision if the object has not been collided with
            if not object_collided[i]:
                object_rect = object_img.get_rect(topleft=object_pos)
                if character_rect.colliderect(object_rect):
                    object_collided[i] = True  # Mark object as collided

        # Draw background and objects
        screen.fill((0, 0, 0))  # Clear screen with black color to prevent visual artifacts

        # Iterate over a 3x3 grid around the current view to allow seamless map wrapping
        for i in range(-1, 2):
            for j in range(-1, 2):
                # Loop through each row in the terrain grid
                for row_idx, row in enumerate(terrain_grid):
                    # Loop through each tile in the row
                    for col_idx, tile_img in enumerate(row):
                        # Calculate the screen position for the tile considering world wrapping
                        tile_x = col_idx * tile_size[0] + i * len(terrain_grid[0]) * tile_size[0]
                        tile_y = row_idx * tile_size[1] + j * len(terrain_grid) * tile_size[1]

                        # Ensure tile is within screen boundaries before drawing
                        if 0 <= tile_x < screen.get_width() and 0 <= tile_y < screen.get_height():
                            if tile_img != "outline":
                                # Draw regular terrain tile
                                screen.blit(tile_img, (tile_x, tile_y))
                            else:
                                # Draw custom water outline for water-adjacent tiles
                                screen.blit(water_outline_img, (tile_x, tile_y))

        # Draw objects, using the collision image if the object has been interacted with
        for i, object_pos in enumerate(object_positions):
            if object_collided[i]:
                screen.blit(object_collision_img, object_pos)  # Render collision version of object
            else:
                screen.blit(object_img, object_pos)  # Render regular object

        # Draw enemies, replaced with death animation if collided or dead
        for i, enemy_pos in enumerate(enemy_positions):
            # Check if enemy is dead (health below 0)
            if enemy_hp[i] < 0:
                # Cycle through death animation frames at 200ms intervals
                death_index = (pygame.time.get_ticks() // 200) % len(enemy_death_imgs)
                death_img = pygame.transform.scale(enemy_death_imgs[death_index], (60, 60))
                screen.blit(death_img, enemy_pos)  # Display death animation frame
            else:
                # Enemy is alive, draw normal enemy sprite
                screen.blit(enemy_img1, enemy_pos)

                # Draw red background for health bar
                pygame.draw.rect(screen, (200, 0, 0), (enemy_pos[0] - 10, enemy_pos[1] - 10, 80, 10))

                # Draw green portion of health bar based on current HP percentage
                pygame.draw.rect(screen, (0, 200, 0), 
                                 (enemy_pos[0] - 10, enemy_pos[1] - 10, 80 * (enemy_hp[i] / 10), 10))

        # Draw character sprite
        screen.blit(character_img, character_rect)

        # Draw equipped weapon sprite
        screen.blit(w, r)

        # Update the display with newly rendered frame
        pygame.display.update()

        # Cap the game loop to 60 frames per second
        clock.tick(60)  

        # Yield control to event loop for asynchronous operations
        await asyncio.sleep(0)  

# Generate a short random seed based on the current time
random_seed = int(str(int(time.time() * 10000))[-5:])

# Start the game with the generated seed
# (Or enter a custom seed number here to generate different terrains and object/enemy positions)
asyncio.run(main(seed=random_seed))
