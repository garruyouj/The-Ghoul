from settings import * 
from pygame.sprite import Sprite
import pygame, sys

# lambda - shortcut way to write simple function
# vector2 - built in pygame class used to store, manipulate, and calculate 2d coordinates (x and y)

class Player(Sprite):
    ''' define the character's stats '''
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images() # this is a function that loads all img of character and store in dictionary
        self.state, self.frame_index = 'down', 0 # default state ng character (nakaharap)
        self.image = pygame.image.load(join('images', 'player', 'down', '0.png')).convert_alpha()
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect(center = pos) # positioning of the character
        self.hitbox_rect = self.rect.inflate(PLAYER_HITBOX_X, PLAYER_HITBOX_Y) #adjustable hitbox of character rect
    
        # movement 
        self.direction = pygame.Vector2() # gets x and y direction (default is 0,0)
        self.speed = PLAYER_SPEED # adjustable speed of character in settings
        self.collision_sprites = collision_sprites # list of sprites that character can collide with

        # health
        self.health = PLAYER_HEALTH
        self.is_vulnerable = True
        self.hit_time = 0
        self.invulenrability_duration = PLAYER_INVISIBILITY

    def load_images(self):
        ''' loads all images then store in a dictionary '''
        self.frames = {
            'left': [],
            'right': [],
            'up': [],
            'down': []
        } # dictionary that stores frames of each state, each state has list of frames (for animation)
        for state in self.frames.keys(): # loops through each state 
            for folder_path, subfolders, file_names in walk(join('Images', 'player', state)): # walk through folders and files in each state folder
                if file_names: # check if there are files in the folder
                    for file_name in sorted(file_names, key= lambda name: int (name.split('.')[0])): # extracts number before "." from file name and sort it 
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha() 
                        surf = pygame.transform.rotozoom(surf, 0, 0.5)
                        self.frames[state].append(surf) # adds the loaded img to the corresponding state list in self.frames dictionary

    def input(self):
        ''' checks for key presses and updates the direction vector accordingly '''
        keys = pygame.key.get_pressed()

        # get direction based on key presses, if right/d, x direction is one, if left/a, x direction is negative one.
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        if self.direction.magnitude() > 0: # checks if vector length greater than 0 (multiple keys pressed)
            self.direction = self.direction.normalize()  #  if true, then normalize to maintain consistent speed when moving diagonally
        else:
            self.direction = pygame.Vector2() # if no keys presseed, then default to zero

    def move(self, dt):
        ''' update hitbox position '''
        self.hitbox_rect.x += self.direction.x * self.speed * dt 
        self.collision('horizontal')

        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')

        self.rect.center = self.hitbox_rect.center # image rect follows hitbox rect

    def collision(self, direction):
        ''' checks for collision with sprites in collision_sprites group then adjusts position accordingly '''
        for sprite in self.collision_sprites: # loops through all sprites in collision_sprites group
            if sprite.rect.colliderect(self.hitbox_rect): # check if sprite's rect collides with player's hitbox rect
                if direction == 'horizontal':
                    if self.direction.x > 0: 
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: 
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: 
                        self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: 
                        self.hitbox_rect.bottom = sprite.rect.top

    def vulnerability_timer(self):
        ''' checks if player is currently invulnerable '''
        if not self.is_vulnerable: # check if player is invulenrable
            current_time = pygame.time.get_ticks() # get current time in milliseconds
            if current_time - self.hit_time >= self.invulenrability_duration: # check if enough time has passed since player was hit
                self.is_vulnerable = True #if yes, then make player vulnerable again

    def animate(self, dt):
        ''' updates player's image based on current state and frame index, also handles blinking effect when hit '''

        # get state 
        if self.direction.x > 0:
            self.state = 'right'
        elif self.direction.x < 0:
            self.state = 'left'
        elif self.direction.y > 0:
            self.state = 'down'
        elif self.direction.y < 0:
            self.state = 'up'
            
        # animate
        # checks if player is moving, if yes, then increase frame index by animation speed * dt, if no then reset frame index to 0
        self.frame_index = self.frame_index + 5 * dt if self.direction else 0 
        # updates player's image based on current state and frame index, uses modulo to loop through frames of current state
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

        # blink effect when hit
        if not self.is_vulnerable: # if player is hit
            if (pygame.time.get_ticks() // 100) % 2 == 0: 
                alpha = 120 # if even then set player's transparency to 120 (semi-transparent)
            else:
                alpha = 255 # if odd then set player's transparency to 255 (fully visible)
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255) # if player not hit, then ignore blinking effect

    def update(self, dt):
        ''' calls functions to update player '''
        self.input()
        self.move(dt)
        self.animate(dt)
        self.vulnerability_timer()