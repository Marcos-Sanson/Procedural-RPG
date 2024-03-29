"""
CIS 350 - Introduction to Software Engineering
Winter 2024 Semester Project
Authors: Marcos Sanson, Jerod Muilenburg, William Krol, Brendon Do, Ely Miller

Prototype 2: Simple Procedurally-Generated Game

A simple game where a character navigates through a terrain with objects and water.
Has the following features:
- Character movement with arrow keys or WASD
- Collision detection with water and objects (work in progress)
- Randomly generated terrain with clusters of water (work in progress)
- Randomly generated objects with collision detection (work in progress)

Original sprite movement code from Dr. Byron DeVries.

Original art, sprites, and images from Game Endeavor's Mystic Woods downloadable asset pack (Free Version): 
https://game-endeavor.itch.io/mystic-woods

Date: March 25, 2024
"""
import pygame
import asyncio
import random


class Player:

    def __init__(self, HP, x, y):
        self.HP = HP
        self.x = x
        self.y = y


class Enemy:

    def __init__(self, HP, x, y):
        self.HP = HP
        self.x = x
        self.y = y



async def main(seed):
    """
    Main function to run the game loop.

    Args:
        seed (int): The seed for random number generation.
    """
    random.seed(seed)  # Set the random seed

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)  # Make the window resizable
    delta = 5
    x = y = 0
    counter = 0

    # Load character image
    character_img = pygame.image.load('character.png').convert_alpha()
    character_img = pygame.transform.scale(character_img, (60, 80))  # Scale up character image
    character_rect = character_img.get_rect()
    character_hp = 10

    # Load enemy images
    enemy_img1 = pygame.image.load('enemy1.png').convert_alpha()
    enemy_img1 = pygame.transform.scale(enemy_img1, (60, 60))  # Scale up enemy image
    enemy_img2 = pygame.image.load('enemy2.png').convert_alpha()
    enemy_img2 = pygame.transform.scale(enemy_img2, (60, 60))  # Scale up enemy image
    enemy_death_imgs = [pygame.transform.scale(pygame.image.load('enemy_death1.png').convert_alpha(), (180, 240)),
                        pygame.transform.scale(pygame.image.load('enemy_death2.png').convert_alpha(), (180, 240))]
    enemy_hp = []

    # Load object images
    object_img = pygame.image.load('object.png').convert_alpha()
    object_img = pygame.transform.scale(object_img, (50, 50))  # Scale up object image
    object_collision_img = pygame.image.load('object_collision.png').convert_alpha()
    object_collision_img = pygame.transform.scale(object_collision_img, (50, 50))  # Scale up collision object image

    # Load background images for different terrains
    grass_img = pygame.image.load('grass.png').convert_alpha()
    water_img = pygame.image.load('water.png').convert_alpha()
    tile_size = (32, 32)  # Size of each tile

    # Load custom water outline image
    water_outline_img = pygame.image.load('water_outline.png').convert_alpha()
    water_outline_img = pygame.transform.scale(water_outline_img, tile_size)

    # Generate random terrain grid based on seed with clusters of water
    terrain_grid = [[grass_img for _ in range(25)] for _ in range(20)]
    num_clusters = random.randint(3, 5)  # Random number of clusters
    for _ in range(num_clusters):
        cluster_size = random.randint(2, 7)  # Random size for each cluster
        cluster_x = random.randint(0, len(terrain_grid[0]) - cluster_size)  # Random x position for the cluster
        cluster_y = random.randint(0, len(terrain_grid) - cluster_size)  # Random y position for the cluster
        for i in range(cluster_y, cluster_y + cluster_size):
            for j in range(cluster_x, cluster_x + cluster_size):
                terrain_grid[i][j] = water_img

    # This section mostly works properly, but is a little rough around the edges (literally--the water tiles are not outlined properly)
    # Add outline to water tiles for collision detection
    # Original code inspired by Marcus Møller (https://github.com/marcusmoller/pyweek17-miner/blob/master/miner/engine.py#L202-L220)
    for i in range(len(terrain_grid)):
        for j in range(len(terrain_grid[0])):
            if terrain_grid[i][j] == water_img:
                # Check neighbors for grass tiles directly adjacent to water and mark them as outline
                if i > 0 and terrain_grid[i - 1][j] == grass_img:
                    terrain_grid[i - 1][j] = "outline"
                if i < len(terrain_grid) - 1 and terrain_grid[i + 1][j] == grass_img:
                    terrain_grid[i + 1][j] = "outline"
                if j > 0 and terrain_grid[i][j - 1] == grass_img:
                    terrain_grid[i][j - 1] = "outline"
                if j < len(terrain_grid[0]) - 1 and terrain_grid[i][j + 1] == grass_img:
                    terrain_grid[i][j + 1] = "outline"

    # Generate random positions for objects
    num_objects = random.randint(1, 4)  # Random number of objects
    object_positions = []
    object_collided = []  # Track collision status for each object
    for _ in range(num_objects):
        object_x = random.randint(0, len(terrain_grid[0]) - 1) * tile_size[0]
        object_y = random.randint(0, len(terrain_grid) - 1) * tile_size[1]
        object_positions.append((object_x, object_y))
        object_collided.append(False)  # Initialize collision status as False for each object

    # Generate random positions for enemy characters
    num_enemies = random.randint(1, 3)  # Random number of enemies
    enemy_positions = []
    enemy_collided = []  # Track collision status for each enemy
    for _ in range(num_enemies):
        enemy_x = random.randint(0, len(terrain_grid[0]) - 1) * tile_size[0]
        enemy_y = random.randint(0, len(terrain_grid) - 1) * tile_size[1]
        enemy_positions.append((enemy_x, enemy_y))
        enemy_hp.append(10)
        enemy_collided.append(False)  # Initialize collision status as False for each enemy

    while True:
        # Needed to handle window-based quite events (non-pygbag runs)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.VIDEORESIZE:  # Handle window resize event
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)  # Update screen size

        # Check if keys are _currently_ pressed down
        keys = pygame.key.get_pressed()
        new_x, new_y = x, y
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= delta
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += delta
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= delta
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += delta
        if keys[pygame.K_q]:
            return
        if keys[pygame.K_z]:
            for i, j in enemy_positions:
                if x - 60 < i < x + 60 and y - 60 < j < y + 60:
                    enemy_hp[counter] -= 1
                counter += 1
            counter = 0

        # Check for out-of-bounds movement
        new_x = max(0, min(new_x, screen.get_width() - character_rect.width))
        new_y = max(0, min(new_y, screen.get_height() - character_rect.height))

        # Check for collision with water in the vicinity of the character
        collision_with_water = False
        scaled_tile_size = (tile_size[0]*2,tile_size[1]*2)  #(screen.get_width() / len(terrain_grid[0]), screen.get_height() / len(terrain_grid))
        character_box = character_rect.move(new_x, new_y).inflate(-character_rect.width/2, -character_rect.height/2)
        for i in range(len(terrain_grid)):
            for j in range(len(terrain_grid[0])):
                if terrain_grid[i][j] in [water_img, "outline"]:
                    water_rect = pygame.Rect(j * scaled_tile_size[0], i * scaled_tile_size[1], scaled_tile_size[0], scaled_tile_size[1])
                    if character_box.colliderect(water_rect):
                        collision_with_water = True
                        break
            if collision_with_water:
                break

        # Update character position if no collision
        if not collision_with_water:
            x, y = new_x, new_y
            character_rect.topleft = (x, y)

        # Check for collision with objects
        for i, object_pos in enumerate(object_positions):
            if not object_collided[i]:  # Only check collision if the object has not been collided with
                object_rect = object_img.get_rect(topleft=object_pos)
                if character_rect.colliderect(object_rect):
                    object_collided[i] = True  # Mark object as collided

        # Check for collision with enemies
        '''for i, enemy_pos in enumerate(enemy_positions):
            if not enemy_collided[i]:  # Only check collision if the enemy has not been collided with
                enemy_rect = enemy_img1.get_rect(topleft=enemy_pos)
                if character_rect.colliderect(enemy_rect):
                    enemy_collided[i] = True  # Mark enemy as collided'''

        # Draw background and objects
        screen.fill((0, 0, 0))  # Clear screen with black color
        for i in range(-1, 2):
            for j in range(-1, 2):
                for row_idx, row in enumerate(terrain_grid):
                    for col_idx, tile_img in enumerate(row):
                        if 0 <= (col_idx * tile_size[0] + i * len(terrain_grid[0]) * tile_size[0]) < screen.get_width() and \
                                0 <= (row_idx * tile_size[1] + j * len(terrain_grid) * tile_size[1]) < screen.get_height():
                            if tile_img != "outline":
                                screen.blit(tile_img,
                                            (col_idx * tile_size[0] + i * len(terrain_grid[0]) * tile_size[0],
                                             row_idx * tile_size[1] + j * len(terrain_grid) * tile_size[1]))
                            else:
                                screen.blit(water_outline_img,  # Use custom water outline image
                                            (col_idx * tile_size[0] + i * len(terrain_grid[0]) * tile_size[0],
                                             row_idx * tile_size[1] + j * len(terrain_grid) * tile_size[1]))

        # Draw objects, replaced with collision image if collided
        for i, object_pos in enumerate(object_positions):
            if object_collided[i]:
                screen.blit(object_collision_img, object_pos)
            else:
                screen.blit(object_img, object_pos)

        # Draw enemies, replaced with death animation if collided
        for i, enemy_pos in enumerate(enemy_positions):
            '''if enemy_collided[i]:
                # Draw death animation
                death_index = (pygame.time.get_ticks() // 200) % len(enemy_death_imgs)
                death_img = pygame.transform.scale(enemy_death_imgs[death_index], (60, 60))
                screen.blit(death_img, enemy_pos)
            else:'''
            if enemy_hp[i] < 0:
                death_index = (pygame.time.get_ticks() // 200) % len(enemy_death_imgs)
                death_img = pygame.transform.scale(enemy_death_imgs[death_index], (60, 60))
                screen.blit(death_img, enemy_pos)
            else:
                screen.blit(enemy_img1, enemy_pos)

        # Draw character
        screen.blit(character_img, character_rect)

        pygame.display.update()
        clock.tick(60)  # Wait until next frame (at 60 FPS)
        await asyncio.sleep(0)  # Very important, and keep it 0

asyncio.run(main(seed=42))  # Enter any seed number here to generate a different terrain and object/enemy positions
