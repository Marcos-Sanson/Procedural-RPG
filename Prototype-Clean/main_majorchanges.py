import asyncio
import ctypes
import glob
import numpy as np
import random
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (300,100)

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
    
    '''
    Returns an array of sprites pulled from the given spritesheet.
    '''
    def load_anim(self, fpath, tile_x):
        sheet = self.load_img(fpath)
        sprites = []
        for i in range(int(sheet.get_width()/tile_x)):
            rect = pygame.Rect(tile_x*i, 0, tile_x, sheet.get_height())
            spr = pygame.Surface(rect.size).convert_alpha()
            spr.blit(sheet, (0, 0), rect)
            sprites.append(spr)
        return sprites
    
    '''
    Returns a pygame Surface made from the given filepath.
    '''
    def load_img(self, fpath):
        try:
            img = pygame.image.load(fpath).convert_alpha()
            return img
        except Exception:
            print("No file found at path " + fpath + " - unexpected behavior may occur!")
        return pygame.Surface((0, 0))
    
    def draw(self, screen):
        screen.blit(self.sprite, self.position)
        
    def mirror(self):
        self.sprite = pygame.transform.flip(self.sprite, True, False)
        
    def update(self):
        pass
    
    
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
        self.radius = 48

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
    
    def take_damage(self, damage):
        self.HP -= damage
        if self.dead:
            return
    
class Slime(Enemy):
    def __init__(self, HP, sprite, x, y):
        super().__init__(HP, sprite, x, y, 60)
        self.sprites_idle = self.load_anim('slime_idle.png', 16)
        self.sprite_ind = 0
        
    def update(self):
        self.sprite_ind += 1
        if self.sprite_ind == len(self.sprites_idle):
            self.sprite_ind = 0
        self.sprite = self.sprites_idle[self.sprite_ind]


class Tile(GameObject):
    def __init__(self, sprite, x, y, can_collide=False):
        super().__init__(sprite, x, y)
        self.can_collide = can_collide



class Game:
    def __init__(self):
        # This is necessary to ensure the display resolution is accurate
        ctypes.windll.user32.SetProcessDPIAware()

        # Establish game variables
        self.clock = pygame.time.Clock()
        self.tile_size = (16, 16)
        grid_size = (25, 15)
        self.expand_factor = 2
        self.screen = pygame.display.set_mode((self.tile_size[0]*grid_size[0],
                                               self.tile_size[1]*grid_size[1]))
        self.finalscreen = pygame.display.set_mode((self.screen.get_width()*self.expand_factor,
                                               self.screen.get_height()*self.expand_factor))

        self.player = None
        self.enemies = []
        self.objects = []
        self.default_img = self.load_img('grass.png')
        self.terrain_grid = [[Tile(self.default_img, i*self.tile_size[0], j*self.tile_size[1]) for j in range(grid_size[0])] for i in range(grid_size[1])]
        self.water_img = None
        self.water_outline_img = None

    '''
    Start of the game, instantiates important game elements and prepares for the main loop.
    '''
    def init(self):
        # Load character image
        character_img = self.load_img('character_me.png')
        character_hp = 10
        self.player = Player(character_hp, character_img, 0, 0)

        # Load enemy images
        enemy_img1 = self.load_img('enemy1.png')
        enemy_img2 = self.load_img('enemy2.png')
        enemy_death_imgs = [pygame.image.load('enemy_death1.png').convert_alpha(),
                            pygame.image.load('enemy_death2.png').convert_alpha()]
        enemy_hp = []

        # Load object images
        object_img = pygame.image.load('object.png').convert_alpha()
        object_collision_img = pygame.image.load('object_collision.png').convert_alpha()

        # Load background images for different terrains
        self.grass_imgs = []
        self.water_imgs = []
        for f in glob.iglob("grass_*.png"):
            gi = pygame.image.load(f).convert_alpha()
            self.grass_imgs.append(gi)
        for f in glob.iglob("water_idle_*.png"):
            gi = pygame.image.load(f).convert_alpha()
            self.water_imgs.append(gi)

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
                    self.terrain_grid[i][j].sprite = self.water_imgs[random.randint(0, len(self.water_imgs)-1)]
                    self.terrain_grid[i][j].can_collide = True

        # Generate random positions for objects
        num_objects = random.randint(1, 4)  # Random number of objects
        for _ in range(num_objects):
            object_x = random.randint(0, len(self.terrain_grid[0]) - 1) * self.tile_size[0]
            object_y = random.randint(0, len(self.terrain_grid) - 1) * self.tile_size[1]
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
        
        self.draw()

    def load_img(self, fpath):
        try:
            img = pygame.image.load(fpath).convert_alpha()
            return img
        except Exception:
            print("No file found at path " + fpath + " - unexpected behavior may occur!")
        return pygame.Surface((0, 0))

    '''
    Primary game loop, including rendering, physics, game logic, etc.
    '''
    def run(self):
        for e in self.enemies:
            e.update()

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
                    enemy.take_damage(1)
        
        # Normalizes diagonal player movement, then executes the move
        if move_vector[0] != 0 or move_vector[1] != 0:
            move_vector = move_vector / np.linalg.norm(move_vector)
        new_x, new_y = self.player.move(move_vector)

        # Check for out-of-bounds movement
        new_x = max(0, min(new_x, self.screen.get_width() - self.player.rect.width))
        new_y = max(0, min(new_y, self.screen.get_height() - self.player.rect.height))

        # This doesn't work properly; needs to be fixed
        # Check for collision with water in the vicinity of the character
        collision_with_water = False
        ### Quick fix to make the water collision work
        scaled_tile_size = (self.tile_size[0]*2, self.tile_size[1]*2)
        character_box = self.player.rect.move(new_x, new_y).scale_by(2).move(self.player.rect.width/2, self.player.rect.height/2)
        ###
        for i in range(len(self.terrain_grid)):
            for j in range(len(self.terrain_grid[0])):
                if self.terrain_grid[i][j].can_collide:
                    water_rect = pygame.Rect(j * scaled_tile_size[0], i * scaled_tile_size[1], scaled_tile_size[0], scaled_tile_size[1])
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
                    obj.open()  # Mark object as collided

        self.draw()
        
        scaled_win = pygame.transform.scale_by(self.screen, self.expand_factor)
        self.finalscreen.blit(scaled_win, (0, 0))

        pygame.display.update()
        self.clock.tick(60)  # Wait until next frame (at 60 FPS)
        print(self.clock.get_fps())
        return 0
    
    '''
    Draws all sprites to the screen.
    '''
    def draw(self):
        # Draw background & tiles
        self.screen.fill((0, 0, 0))  # Clear screen with black color
        for row_idx, row in enumerate(self.terrain_grid):
            for col_idx, tile in enumerate(row):
                self.screen.blit(tile.sprite,
                            (col_idx * self.tile_size[0],
                                row_idx * self.tile_size[1]))

        # Draw objects, replaced with collision image if collided
        for obj in self.objects:
            obj.draw(self.screen)

        # Draw enemies, replaced with death animation if collided
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw character
        self.player.draw(self.screen)
    

seed = 12
if __name__ == "__main__": #async def main(seed):
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
        

#asyncio.run(main(seed=11))  # Enter any seed number here to generate a different terrain and object/enemy positions
