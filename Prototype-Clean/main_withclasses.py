import asyncio
import ctypes
import glob
import numpy as np
import random
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (360,200) # Determines the top-left corner of the screen

import pygame


class GameObject:
    def __init__(self, sprite, x, y):
        self.sprite = sprite
        self.rect = sprite.get_rect(topleft=(x, y))
        self.x = x
        self.y = y
        
    @property
    def position(self):
        return (self.x, self.y)
    
    def render(self, screen):
        upsprite = pygame.transform.scale_by(self.sprite, 1)
        screen.blit(upsprite, self.position)
        
    def mirror(self):
        self.sprite = pygame.transform.flip(self.sprite, True, False)
    
    
class Chest(GameObject):
    def __init__(self, sprite, open_sprite, x, y):
        super().__init__(sprite, x, y)
        self.opened = False
        self.open_sprite = open_sprite
        
    def open(self):
        self.opened = True
        self.sprite = self.open_sprite
        

class Entity(GameObject):
    def __init__(self, HP, sprite, x, y):
        super().__init__(sprite, x, y)
        self.HP = HP
        

class Player(Entity):
    def __init__(self, HP, sprite, x, y):
        super().__init__(HP, sprite, x, y)
        self.player_speed = 3
        self.radius = 48 # attack radius, currently unused

        self.sprite_ind = 0
        sprites = []
        for f in glob.iglob("player_*.png"):
            gi = pygame.image.load(f).convert_alpha()
            sprites.append(gi)
        self.sprites = sprites
        self.facing_left = False
        
    def move(self, move):
        new_x = self.x + move[0] * self.player_speed
        new_y = self.y + move[1] * self.player_speed
        
        # change character sprite according to movement
        if move[1] < -0.1:
            if abs(move[0]) > 0.1:
                self.sprite_ind = 1
            else:
                self.sprite_ind = 0
        elif -0.1 < move[1] < 0.1:
            if abs(move[0]) > 0.1:
                self.sprite_ind = 2
        else:
            if abs(move[0]) > 0.1:
                self.sprite_ind = 3
            else:
                self.sprite_ind = 4
        self.sprite = self.sprites[self.sprite_ind]
        if move[0] < -0.1:
            self.mirror()
            self.facing_left = True
        elif 0.1 > move[0] > -0.1 and self.facing_left:
            self.mirror()
        else:
            self.facing_left = False
            
        return new_x, new_y

class Enemy(Entity):
    def __init__(self, HP, sprite, x, y, radius):
        super().__init__(HP, sprite, x, y)
        self.radius = radius
        
    @property
    def dead(self):
        return self.HP <= 0
    
class Slime(Enemy):
    def __init__(self, HP, sprite, x, y):
        super().__init__(HP, sprite, x, y, 60)


class Tile(GameObject):
    def __init__(self, sprite, x, y, can_collide=False):
        super().__init__(sprite, x, y)
        self.can_collide = can_collide



class Game:
    def __init__(self):
        # This is necessary to ensure the display resolution is accurate
        ctypes.windll.user32.SetProcessDPIAware()

        # Establish global variables
        self.clock = pygame.time.Clock()
        self.expand_factor = 3 # Multiplies screen by this amount to increase screen size (see end of run())
        self.tile_size = (16, 16)
        grid_size = (25, 14) # Terrain grid dimensions
        self.screen = pygame.display.set_mode((self.tile_size[0]*grid_size[0],
                                               self.tile_size[1]*grid_size[1]))
        self.finalscreen = pygame.display.set_mode((self.screen.get_width()*self.expand_factor,
                                               self.screen.get_height()*self.expand_factor))

        self.player = None
        self.enemies = []
        self.objects = []
        self.default_img = pygame.image.load('grass.png').convert_alpha()
        self.terrain_grid = [[Tile(self.default_img, i*self.tile_size[0], j*self.tile_size[1])
                              for j in range(grid_size[0])] for i in range(grid_size[1])]


    '''
    Start of the game, instantiates important game elements and prepares for the main loop.
    '''
    def init(self):
        # Load character image
        character_img = pygame.image.load('character.png').convert_alpha()
        #character_img = pygame.transform.scale(character_img, (60, 80))  # Scale up character image
        character_rect = character_img.get_rect()
        character_hp = 10
        self.player = Player(character_hp, character_img, 0, 0)

        # Load enemy images
        enemy_img1 = pygame.image.load('enemy1.png').convert_alpha()
        #enemy_img1 = pygame.transform.scale(enemy_img1, (60, 60))  # Scale up enemy image
        enemy_img2 = pygame.image.load('enemy2.png').convert_alpha()
        #enemy_img2 = pygame.transform.scale(enemy_img2, (60, 60))  # Scale up enemy image
        #enemy_death_imgs = [pygame.transform.scale(pygame.image.load('enemy_death1.png').convert_alpha(), (180, 240)),
        #                    pygame.transform.scale(pygame.image.load('enemy_death2.png').convert_alpha(), (180, 240))]
        enemy_death_imgs = [pygame.image.load('enemy_death1.png').convert_alpha(),
                            pygame.image.load('enemy_death2.png').convert_alpha()]
        enemy_hp = []

        # Load object images
        object_img = pygame.image.load('object.png').convert_alpha()
        #object_img = pygame.transform.scale(object_img, (50, 50))  # Scale up object image
        object_collision_img = pygame.image.load('object_collision.png').convert_alpha()
        #object_collision_img = pygame.transform.scale(object_collision_img, (50, 50))  # Scale up collision object image

        # Load background images for different terrains
        self.grass_imgs = []
        for f in glob.iglob("grass_*.png"):
            gi = pygame.image.load(f).convert_alpha()
            self.grass_imgs.append(gi)
        self.water_img = pygame.image.load('water.png').convert_alpha()

        # Load custom water outline image
        self.water_outline_img = pygame.image.load('water_outline.png').convert_alpha()
        self.water_outline_img = pygame.transform.scale(self.water_outline_img, self.tile_size)

        # Generate random terrain grid based on seed with clusters of water
        for r in range(len(self.terrain_grid)):
            for c in range(len(self.terrain_grid[r])):
                self.terrain_grid[r][c].sprite = self.grass_imgs[random.randint(0, len(self.grass_imgs)-1)]
        num_clusters = random.randint(3, 5)  # Random number of clusters
        for _ in range(num_clusters):
            cluster_size = random.randint(2, 7)  # Random size for each cluster
            cluster_x = random.randint(0, len(self.terrain_grid[0]) - cluster_size)  # Random x position for the cluster
            cluster_y = random.randint(0, len(self.terrain_grid) - cluster_size)  # Random y position for the cluster
            for i in range(cluster_y, cluster_y + cluster_size):
                for j in range(cluster_x, cluster_x + cluster_size):
                    self.terrain_grid[i][j].sprite = self.water_img
                    self.terrain_grid[i][j].can_collide = True

        '''
        # This section doesn't work properly! Needs to be fixed.
        # Add outline to water tiles for collision detection
        # Original code inspired by Marcus Møller (https://github.com/marcusmoller/pyweek17-miner/blob/master/miner/engine.py#L202-L220)
        for i in range(len(self.terrain_grid)):
            for j in range(len(self.terrain_grid[0])):
                if self.terrain_grid[i][j] == self.water_img:
                    # Check neighbors for grass tiles directly adjacent to water and mark them as outline
                    if i > 0 and self.terrain_grid[i - 1][j] == self.grass_img:
                        self.terrain_grid[i - 1][j] = "outline"
                    if i < len(self.terrain_grid) - 1 and self.terrain_grid[i + 1][j] == self.grass_img:
                        self.terrain_grid[i + 1][j] = "outline"
                    if j > 0 and self.terrain_grid[i][j - 1] == self.grass_img:
                        self.terrain_grid[i][j - 1] = "outline"
                    if j < len(self.terrain_grid[0]) - 1 and self.terrain_grid[i][j + 1] == self.grass_img:
                        self.terrain_grid[i][j + 1] = "outline"
        '''

        # Generate random positions for objects, avoiding water/walls
        num_objects = random.randint(1, 4)  # Random number of objects
        for _ in range(num_objects):
            tile_x = random.randint(0, len(self.terrain_grid[0]) - 1)
            tile_y = random.randint(0, len(self.terrain_grid) - 1)
            if not self.terrain_grid[tile_y][tile_x].can_collide:
                object_x = tile_x * self.tile_size[0]
                object_y = tile_y * self.tile_size[1]
                obj = Chest(object_img, object_collision_img, object_x, object_y)
                self.objects.append(obj)

        # Generate random positions for enemy characters
        num_enemies = random.randint(1, 3)  # Random number of enemies
        for _ in range(num_enemies):
            enemy_hp = 10
            enemy_x = random.randint(0, len(self.terrain_grid[0]) - 1) * self.tile_size[0]
            enemy_y = random.randint(0, len(self.terrain_grid) - 1) * self.tile_size[1]
            e = Slime(enemy_hp, enemy_img1, enemy_x, enemy_y)
            self.enemies.append(e)


    '''
    Primary game loop, including rendering, physics, game logic, etc.
    '''
    def run(self):
        # Needed to handle window-based quite events (non-pygbag runs)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.VIDEORESIZE:  # Handle window resize event
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)  # Update screen size

        # Check if keys are _currently_ pressed down
        keys = pygame.key.get_pressed()
        move_vector = [0, 0]
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_vector[0] += -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_vector[0] += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_vector[1] += -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_vector[1] += 1
        if keys[pygame.K_q]:
            return -1
        if keys[pygame.K_z]: # attack
            for enemy in self.enemies:
                i, j = enemy.position
                if self.player.x - self.player.radius < i < self.player.x + self.player.radius and \
                    self.player.y - self.player.radius < j < self.player.y + self.player.radius:
                    enemy.HP -= 1
                if enemy.dead:
                    self.enemies.remove(enemy)
        
        # Normalizes diagonal player movement, then executes the move
        if move_vector[0] != 0 or move_vector[1] != 0:
            move_vector = move_vector / np.linalg.norm(move_vector)
        new_x, new_y = self.player.move(move_vector)

        # Check for out-of-bounds movement
        print(new_y)
        new_x = max(0, min(new_x, self.screen.get_width()/self.expand_factor - self.player.rect.width))
        new_y = max(0, min(new_y, self.screen.get_height()/self.expand_factor - self.player.rect.height))

        # This doesn't work properly; needs to be fixed
        # Check for collision with water in the vicinity of the character
        collision_with_water = False
        ### Quick fix to make the water collision work
        scaled_tile_size = (self.tile_size[0]*2, self.tile_size[1]*2)
        character_box = self.player.rect.move(new_x, new_y).scale_by(3).move(self.player.rect.width, self.player.rect.height)
        ###
        for i in range(len(self.terrain_grid)):
            for j in range(len(self.terrain_grid[0])):
                if self.terrain_grid[i][j].can_collide:
                    water_rect = pygame.Rect(j * scaled_tile_size[0], i * scaled_tile_size[1],
                                             scaled_tile_size[0], scaled_tile_size[1])
                    if character_box.colliderect(water_rect):
                        collision_with_water = True
                        break
            if collision_with_water:
                break

        # Update character position if no collision
        if not collision_with_water:
            self.player.x, self.player.y = new_x, new_y
            self.player.rect.topleft = (self.player.x, self.player.y)

        # Check for collision with objects
        for obj in self.objects:
            if not obj.opened:  # Only check collision if the object has not been collided with
                if self.player.rect.colliderect(obj.rect):
                    obj.open()

        # Check for collision with enemies
        '''for i, enemy_pos in enumerate(enemy_positions):
            if not enemy_collided[i]:  # Only check collision if the enemy has not been collided with
                enemy_rect = enemy_img1.get_rect(topleft=enemy_pos)
                if character_rect.colliderect(enemy_rect):
                    enemy_collided[i] = True  # Mark enemy as collided'''

        self.draw()
        
        scaled_win = pygame.transform.scale_by(self.screen, self.expand_factor)
        self.finalscreen.blit(scaled_win, (0, 0))

        pygame.display.update()
        self.clock.tick(60)  # Wait until next frame (at 60 FPS)
        return 0
    
    '''
    Draws all sprites to the screen.
    '''
    def draw(self):
        self.draw_background()

        # Draw objects, replaced with collision image if collided
        for obj in self.objects:
            if obj.opened:
                self.screen.blit(obj.open_sprite, obj.position)
            else:
                self.screen.blit(obj.sprite, obj.position)

        # Draw enemies, replaced with death animation if collided
        for enemy in self.enemies:
            if enemy.HP < 0:
                death_img = pygame.transform.scale(enemy.sprite, (60, 60))
                self.screen.blit(death_img, enemy.position)
            else:
                self.screen.blit(enemy.sprite, enemy.position)

        # Draw character
        #self.screen.blit(self.player.sprite, self.player.position)
        self.player.render(self.screen)
        
    '''
    Draws all background sprites to the screen.
    '''
    def draw_background(self):
        self.screen.fill((0, 0, 0))  # Clear screen with black color
        for row_idx, row in enumerate(self.terrain_grid):
            for col_idx, tile in enumerate(row):
                self.screen.blit(tile.sprite,
                            (col_idx * self.tile_size[0],
                                row_idx * self.tile_size[1]))
    
    

#seed = 12
async def main(seed):
    """
    Main function to run the game.

    Args:
        seed (int): The seed for random number generation.
    """
    
    random.seed(seed)  # Set the random seed
    
    game = Game()
    game.init()

    while True:
        if game.run() != 0:
            break
        #await asyncio.sleep(0)  # Very important, and keep it 0
        

asyncio.run(main(seed=12))  # Enter any seed number here to generate a different terrain and object/enemy positions
