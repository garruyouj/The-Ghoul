import pygame
from os.path import join
from os import walk # alows us to list all files inside folders

# DIMENSIONS of the game:
window_width = 1920
window_height = 1080

# Game mechanics:
SURVIVAL_TIME = 600 #seconds
BOSS_MILESTONE = 15 #zombies to kill before boss
TILE_SIZE = 64
opacity = 10 #tinanggal ko muna ito kasi ang lag
TOTAL_ITEMS_TO_SPAWN = 20
ITEM_TILE_SIZE = 64

# Character Stats
PLAYER_SPEED = 400
PLAYER_HEALTH = 5
PLAYER_HITBOX_X, PLAYER_HITBOX_Y = -20, -70
PLAYER_INVISIBILITY = 2000 # how long is player invicible when hit
PLAYER_STAMINA = 100
PLAYER_STAMINA_RECOVERY = 35

# Enemy
ENEMY_SPEED = 150
ENEMY_HITBOX_X, ENEMY_HITBOX_Y = -20, -70
BOSS_HITBOX_X, BOSS_HITBOX_Y = -80, -99
BOSS_HEALTH = 10
BOSS_SPEED = 200
ENEMY_ANIMATION_SPEED = 3
ENEMY_SPAWN = 1500 # milliseconds

# Gun
GUN_COOLDOWN = 600 # milliseconds firing cooldown
GUN_DISTANCE = 60 # pixels away from player

