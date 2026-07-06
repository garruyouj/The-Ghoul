import pygame
from settings import *
from math import atan2, degrees
from pygame.sprite import Sprite

class BaseSprite(Sprite):
    ''' Base blueprint for all objects '''
    def __init__(self, pos, surf, groups):
        ''' Constructor: takes position(pos), image(surf), and spawns it at the exact spot '''
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.ground = True

class CollisionSprite(Sprite):
    ''' (OBJECTS 1 in TILED) Solid Objects (objs na may collisions, but nasa decoration sprite mostly ang mga objs bcs mas better if manual collision sa tiled) '''
    def __init__(self, pos, surf, groups):
        ''' Takes position, image, grabs layout, and throws it into collision groups to act like a wall '''
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

        # This class is called in setup()

class DecorationSprite(Sprite):
    ''' (OBJECTS 2 in TILED) Objects that does not have collision, only for decorations '''
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

        # This class is also called in setup()

class Gun(Sprite):
    ''' Simulation of a Gun that rotates around the player according to the mouse position '''
    def __init__(self, player, groups):
        ''' how far is gun from player, load gun asset, scales it, initialize default direction '''
        # player connection
        self.player = player 
        self.distance = GUN_DISTANCE # how far is gun from player
        self.player_direction = pygame.Vector2(0,1)

        #sprite setup
        super().__init__(groups)
        self.gun_surf = pygame.image.load(join('Images', 'gun', 'gun.png')).convert_alpha()
        self.gun_surf = pygame.transform.rotozoom(self.gun_surf, 0, 0.5)
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center = self.player.rect.center + self.player_direction * self.distance) # gun is below the player as initial position

    def get_direction(self):
        ''' checks user's mouse, grabs current mouse cursor coordinates, compares to center of screen, calculates math arrow '''
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(window_width / 2,  window_height / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    def rotate_gun(self):
        ''' calculates angle of user's aim. if right = tilts gun texture, if left = flips upside down '''
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90 # atan2 gives angle in radians, then degrees converts it to degrees. subtract 90 degrees bcs gun imag orginally points down
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else: # if position is pointing left (more less than 0 degrees), image will be flipped
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)
        
    def update(self, _):
        ''' updates direction, rotation, and snaps gun's pos to stay attached to moving player '''
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(Sprite):
    ''' Projectiles that shoots out from the gun '''
    def __init__(self, surf, pos, direction, groups):
        ''' spawns bullet at tip of the gun, copies gun's direction, and stamps time stamp '''
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000 # bullets only appear for 1 sec then it will disappear after.
        self.direction = direction
        self.speed = 1200

        # shooting cooldown is in the maingame file: gun_timer()

    def update(self, dt):
        ''' moves bullet forward based on speed, checks bullet if it has been alive mlonger than 1 sec, then if yes it will be deleted '''
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

class Enemy(Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, is_boss = False):
        super().__init__(groups)
        self.player = player
        self.is_boss = is_boss
        self.frames, self.frame_index = frames, 0
        
        if self.is_boss:
            self.image = pygame.transform.rotozoom(self.frames[self.frame_index], 0, 0.5)
            self.health = getattr(player, 'boss_difficulty_health', BOSS_HEALTH)
            self.max_health = self.health
            self.speed = getattr(player, 'boss_difficulty_speed_modifier', BOSS_SPEED) # Fallback to base setting
            boss_hitbox_width, boss_hitbox_height = BOSS_HITBOX_X, BOSS_HITBOX_Y
        else:
            self.image = self.frames[self.frame_index]
            self.health = 1
            self.max_health = 1
            self.speed = getattr(player, 'difficulty_speed_modifier', ENEMY_SPEED)
            boss_hitbox_width, boss_hitbox_height = ENEMY_HITBOX_X, ENEMY_HITBOX_Y

        self.animation_speed = ENEMY_ANIMATION_SPEED
        
        # Inflate properly relative to center positions
        temp_rect = self.image.get_rect(center = pos)
        self.hitbox_rect = temp_rect.inflate(boss_hitbox_width, boss_hitbox_height)
        self.rect = self.image.get_rect(center = self.hitbox_rect.center)
        
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.death_time = 0
        self.death_duration = 200

        # --- HIGH PRECISION DECIMAL COORDINATES FOR MOVEMENT ---
        self.pos_x = float(self.hitbox_rect.x)
        self.pos_y = float(self.hitbox_rect.y)

    def animate(self, dt):
        ''' Loops frames sequentially without directional splits '''
        if self.frames:
            self.frame_index += self.animation_speed * dt
            # Modulo length check handles single files (1 % 1 = 0) or multiple frames smoothly
            current_frame = self.frames[int(self.frame_index) % len(self.frames)]
            
            if self.is_boss:
                # Keep the boss continuously scaled up on every animation update frame
                self.image = pygame.transform.rotozoom(current_frame, 0, 0.5)
            else:
                self.image = current_frame

    def move(self, dt):
        ''' Enemy Pathfinding '''
        player_pos = pygame.Vector2(self.player.rect.center) # takes player's position
        enemy_pos = pygame.Vector2(self.rect.center) # takes enemy position
        
        if player_pos != enemy_pos:
            self.direction = (player_pos - enemy_pos).normalize() # subtract vector pointing from enemy to player
        else:
            self.direction = pygame.Vector2()

        # Horizontal movement using the high precision trackers
        self.pos_x += self.direction.x * self.speed * dt
        self.hitbox_rect.x = round(self.pos_x)
        self.collision('horizontal')

        # Vertical movement using the high precision trackers
        self.pos_y += self.direction.y * self.speed * dt
        self.hitbox_rect.y = round(self.pos_y)
        self.collision('vertical')

        self.rect.center = self.hitbox_rect.center
 
    def collision(self, direction):
        collided = False
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                collided = True
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                    self.pos_x = float(self.hitbox_rect.x) # Sync precision position
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    self.pos_y = float(self.hitbox_rect.y) # Sync precision position
        return collided

    def destroy(self):
        ''' when bullet hits, zombie is immediately dead nd transformed its sprite img into silhouette mask '''
        if self.is_boss:
            self.health -= 1
            if self.health >0:
                return
        # start a timer
        self.death_time = pygame.time.get_ticks()
        # change image
        surf = pygame.mask.from_surface(self.frames[0]). to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def death_timer(self):
        ''' zombie sillouhette corpse stay on screen for a while then be deleted '''
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def draw_health_bar(self, screen, offset):
        if not self.is_boss or self.death_time != 0:
            return

        bar_width = 120
        bar_height = 12

        health_ratio = self.health / 20   # boss max health

        # Convert world position to screen position
        screen_x = self.rect.centerx + offset.x - bar_width // 2
        screen_y = self.rect.top + offset.y - 25

        # Background
        pygame.draw.rect(
            screen,
            (40, 40, 40),
            (screen_x, screen_y, bar_width, bar_height),
            border_radius=4
        )

        # Current HP
        pygame.draw.rect(
            screen,
            (220, 30, 30),
            (screen_x, screen_y, bar_width * health_ratio, bar_height),
            border_radius=4
        )

        # Border
        pygame.draw.rect(
            screen,
            "white",
            (screen_x, screen_y, bar_width, bar_height),
            2,
            border_radius=4
        )

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()
