import pygame
from sys import exit
from os.path import join 
from os import walk 
from random import randint, choice 
from pytmx.util_pygame import load_pygame 

# Internal Modular Imports
from settings import *
from player import Player
from groups import AllSprites
from sprites import *
import ui 

class Game:
    def __init__(self):
        """Initializes the entire game state, assets, and engine setups."""
        # Core Window Setup
        pygame.init()
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("The Ghoul")
        self.clock = pygame.time.Clock()

        # Game State and Tracking Metrics
        self.running = True
        self.game_state = 'menu'
        self.game_has_started = False
        self.story_mode = 'intro'
        self.zombies_killed = 0
        self.victory_time = 0 
        self.survival_time = 0
        self.highest_kills = 0
        self.best_survival_time = 0
        self.best_infinite_stage = 1
        self.survival_goal = SURVIVAL_TIME 

        # Boss & Infinite Mode Tracking
        self.boss_spawned = False
        self.boss_kill_milestone = 1
        self.is_infinite_mode = False
        self.infinite_level = 1
        self.last_boss_spawn_time = 0

        self.booster_active = None         
        self.booster_start_time = 0
        self.booster_duration = 7000       # 7 Seconds (7000ms)
        self.blink_timer = 0
        self.blink_visible = True

        # Sprint System Metrics
        self.is_sprinting = False
        self.stamina = PLAYER_STAMINA
        self.max_stamina = PLAYER_STAMINA
        self.stamina_drain = 40        # stamina drained per second
        self.stamina_recovery = 25     # stamina recovered per second
        self.sprint_cooldown = False
        self.cooldown_time = 0
        self.cooldown_duration = 2000  # milliseconds
        self.normal_speed = PLAYER_SPEED
        self.sprint_speed = PLAYER_SPEED * 1.8

        # Sprite Management Groups
        self.all_sprites = AllSprites() 
        self.collision_sprites = pygame.sprite.Group() 
        self.bullet_sprites = pygame.sprite.Group() 
        self.enemy_sprites = pygame.sprite.Group() 

        # Combat Cooldowns and Spawning Timers
        self.can_shoot = True 
        self.shoot_time = 0 
        self.gun_cooldown = GUN_COOLDOWN
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, ENEMY_SPAWN)
        self.spawn_positions = []

        # UI & Font Configuration Pipelines
        self.init_fonts_and_ui()
        self.load_audio()
        self.load_images()
        self.import_assets()
        
        # Storyline Configuration
        self.init_storyline()

        # Map Load Initial Execution
        self.setup(self.tmx_maps['world'], None)

    def init_fonts_and_ui(self):
        """Initializes internal font instances and static UI Text Surfaces."""
        # Fonts
        self.difficulty_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 50)
        self.pause_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 70)
        self.story_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 30)
        self.mode_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 50) 

        # Difficulty Menu Surfaces & Rects
        self.easy_surf = pygame.transform.rotozoom(pygame.image.load(join("Images", "ui", "buttons", "easy_button.png")).convert_alpha(), 0, 0.7)
        self.medium_surf = pygame.transform.rotozoom(pygame.image.load(join("Images", "ui", "buttons", "medium_button.png")).convert_alpha(), 0, 0.7)
        self.hard_surf = pygame.transform.rotozoom(pygame.image.load(join("Images", "ui", "buttons", "hard_button.png")).convert_alpha(), 0, 0.7)
        self.infinite_surf = pygame.transform.rotozoom(pygame.image.load(join("Images", "ui", "buttons", "endless_button.png")).convert_alpha(), 0, 0.7)

        self.easy_rect = self.easy_surf.get_rect(center=(window_width // 2, window_height // 2 - 70))
        self.medium_rect = self.medium_surf.get_rect(center=(window_width // 2, window_height // 2 + 40))
        self.hard_rect = self.hard_surf.get_rect(center=(window_width // 2, window_height // 2 + 150))
        self.infinite_rect = self.infinite_surf.get_rect(center=(window_width // 2, window_height // 2 + 260))

    def init_storyline(self):
        """Initializes assets and narrative text slices for introduction scenes."""
        self.current_scene_index = 0
        self.scene_progress = 0.0
        self.pan_speed = 0.12
        self.text_visible_chars = 0.0
        self.text_speed = 30.0
        self.story_mode = 'intro'

        self.story_scenes = [
            ("1.png", [
                "In the land of Vermille, NeuroCore Institute,", 
                "a science laboratory in the city, were to create a",
                "brain enhancer due to the City’s educational crisis."
            ], 400, 300),
            ("2.png", [
                "The experimental concoction is injected to a volunteer", 
                "called Subject X."
            ], 300, 400),
            ("3.png", [
                "With every minute passed by, Subject X showed", 
                "erratic behavior."
            ], 400, 300),
            ("4.png", [
                "The chaos has begun, Subject X becomes violent", 
                "as he eats other Scientists in the lab."
            ], 300, 400),
            ("5.png", [
                "Professor A immediately hides under the table.",
                "As she was hiding, scared to death.", 
                "Realizing the weight of her creation,",
                "she then stumbled upon a piece of paper."
            ], 400, 300),
            ("6.png", [""], 300, 400),
            ("7.png", [
                "Professor A stood up, she then witnessed something peculiar.", 
                "Catching the sight of Subject X pointing to its targeted prey,", 
                "heads of the infected scientist turn towards it as if they obey",
                "Subject X’s commands."
            ], 400, 300),
            ("8.png", [
                "A chorus of panicked screams echoed outside", 
                "as the virus spread throughout the city."
            ], 300, 400),
            ("9.png", [
                "Suddenly, a loud noise came from the entrance of the lab.", 
                "Subject X broke free as the glasses shattered across the floor.",
                "Then, a realization hits,",
                "“I must finish what I’ve started.”"
            ], 400, 300)
        ] 

        self.outro_scenes = [
            ("1.png", [
                "Blood splashes onto the ground. The so-called",
                "Boss also known as Subject X collapsed as his heads started",
                "to decapitate one by one."
            ], 400, 300),
            ("2.png", [
                "As the Boss died, the infected zombies stopped",
                "moving as it slowly became lifeless."
            ], 300, 400),
            ("3.png", [
                "The sound of a helicopter echoed",
                "through the thick bloody air."
            ], 300, 400),
            ("4.png", [
                "As the vehicle landed on the ground,",
                "several scientists came out and rescued the only survivor,", 
                "Professor A."
            ], 400, 300),
        ] 
        
        self.skip_surf = pygame.image.load(join('Images', 'ui', 'buttons', 'skip.png')).convert_alpha()
        self.skip_surf = pygame.transform.rotozoom(self.skip_surf, 0, 0.9)
        self.skip_rect = self.skip_surf.get_rect(bottomright=(window_width - 350, window_height - 200))
        
    def load_audio(self):
        """Initializes sound arrays and configures global volumes."""
        self.shoot_sound = pygame.mixer.Sound(join('Audios', 'Shoot.MP3'))
        self.shoot_object_sound = pygame.mixer.Sound(join('Audios', 'bullet hit obj.MP3'))
        self.impact_sound = pygame.mixer.Sound(join('Audios', 'Impact.MP3'))
        self.kill_sound = pygame.mixer.Sound(join('Audios', 'Killed.MP3'))
        self.player_hit_sound = pygame.mixer.Sound(join('Audios', 'ouch.MP3'))
        self.bg_music = pygame.mixer.Sound(join('Audios', 'Background_music.MP3'))
        self.click_sound = pygame.mixer.Sound(join('Audios', 'Click.MP3'))
        
        for sound in [self.shoot_sound, self.impact_sound, self.kill_sound, self.player_hit_sound]:
            sound.set_volume(0.4) 
        self.bg_music.set_volume(2) 
        self.bg_music.play(loops=-1) 

    def load_images(self):
        """Loads framework sprite sheets and baseline image overlays."""
        # Main Menu Graphics
        self.menu_bg_surf = pygame.image.load(join('Images', 'ui', 'backgroundmostfinal.jpg')).convert_alpha()
        self.menu_bg_surf = pygame.transform.rotozoom(self.menu_bg_surf, 0, 0.7)
        self.menu_bg_rect = self.menu_bg_surf.get_rect(center=(window_width // 2, window_height // 2))

        self.logo_surf = pygame.image.load(join('Images', 'ui', 'logos', 'the_ghoul_logo.png')).convert_alpha()
        self.logo_surf = pygame.transform.rotozoom(self.logo_surf, 0, 0.7)
        self.logo_rect = self.logo_surf.get_rect(center=(window_width // 2 - 380, window_height // 2 - 100))

        self.play_button_surf = pygame.image.load(join('Images', 'ui', 'buttons', 'start_button.png')).convert_alpha()
        self.play_button_surf = pygame.transform.rotozoom(self.play_button_surf, 0, 0.7)
        self.play_button_rect = self.play_button_surf.get_rect(center=(window_width // 2 - 400, window_height // 2 + 50))

        self.quit_button_surf = pygame.image.load(join('Images', 'ui', 'buttons', 'quit_button.png')).convert_alpha()
        self.quit_button_surf = pygame.transform.rotozoom(self.quit_button_surf, 0, 0.7)
        self.menu_quit_rect = self.quit_button_surf.get_rect(center=(window_width // 2 - 400, window_height // 2 + 200))
        self.menu_button_surf = pygame.image.load(join('Images', 'ui', 'buttons', 'menu_button.png')).convert_alpha()
        self.menu_button_surf = pygame.transform.rotozoom(self.menu_button_surf, 0, 0.7)
        
        # Mid-Session Interface Assets
        self.continue_button_surf = pygame.image.load(join('Images', 'ui', 'buttons', 'continue.png')).convert_alpha()
        self.continue_button_surf = pygame.transform.rotozoom(self.continue_button_surf, 0, 0.9)
        self.continue_rect = self.continue_button_surf.get_rect(center=(window_width // 2 - 400, window_height // 2 + 30))
        
        self.newgame_button_surf = pygame.image.load(join('Images', 'ui', 'buttons', 'new_game.png')).convert_alpha()
        self.newgame_button_surf = pygame.transform.rotozoom(self.newgame_button_surf, 0, 0.9)
        self.newgame_rect = self.newgame_button_surf.get_rect(center=(window_width // 2 - 400, window_height // 2 + 150))
        self.menu_quit2_rect = self.quit_button_surf.get_rect(center=(window_width // 2 - 400, window_height // 2 + 280))     
        
        # Icons
        self.home_icon_surf = pygame.image.load(join('Images', 'ui', 'icons', 'home_icon.png'))
        self.home_icon_surf = pygame.transform.rotozoom(self.home_icon_surf, 0, 0.4)
        self.exit_icon_surf = pygame.image.load(join('Images', 'ui', 'icons', 'exit_icon.png')).convert_alpha()
        self.exit_icon_surf = pygame.transform.rotozoom(self.exit_icon_surf, 0, 0.4)
        self.pause_icon_surf = pygame.image.load(join('Images', 'ui', 'icons', 'pause_icon.png')).convert_alpha()
        self.pause_icon_surf = pygame.transform.rotozoom(self.pause_icon_surf, 0, 0.1)
        self.pause_icon_rect = self.pause_icon_surf.get_rect(topright=(window_width - 350, 200))
        self.play_icon_surf = pygame.image.load(join('Images', 'ui', 'icons', 'play_icon.png')).convert_alpha()
        self.play_icon_surf = pygame.transform.rotozoom(self.play_icon_surf, 0, 0.1)
        self.play_icon_rect = self.play_icon_surf.get_rect(topright=(window_width - 350, 200))

        # Pause Screen
        self.resume_button_surf = pygame.transform.rotozoom(pygame.image.load(join("Images", "ui", "buttons", "resume.png")).convert_alpha(), 0, 0.7)
        self.menu_button_pause_surf = pygame.transform.rotozoom(pygame.image.load(join("Images", "ui", "buttons", "menu_button.png")).convert_alpha(), 0, 0.7)
        self.quit_button_pause_surf = pygame.transform.rotozoom(pygame.image.load(join("Images", "ui", "buttons", "quit_button.png")).convert_alpha(), 0, 0.7)

        self.resume_rect = self.resume_button_surf.get_rect(center=(window_width // 2, window_height // 2 - 40))
        self.menu_rect_pause = self.menu_button_pause_surf.get_rect(center=(window_width // 2, window_height // 2 + 80))
        self.quit_rect_pause = self.quit_button_pause_surf.get_rect(center=(window_width // 2, window_height // 2 + 200))
        
        # Game Over Screen
        self.game_over_surf = pygame.image.load(join('Images', 'ui', 'logos', 'you_died.png')).convert_alpha()
        self.game_over_surf = pygame.transform.rotozoom(self.game_over_surf, 0, 1)
        self.game_over_rect = self.game_over_surf.get_rect(center=(window_width // 2, window_height // 2 - 250))
        self.try_again_surf = pygame.image.load(join('Images', 'ui', 'buttons', 'try_again.png')).convert_alpha()
        self.try_again_surf = pygame.transform.rotozoom(self.try_again_surf, 0, 0.7)

        # Victory Screens
        self.you_survived_surf = pygame.image.load(join('Images', 'ui', 'logos', 'you_survived.png')).convert_alpha()
        self.you_survived_rect = self.you_survived_surf.get_rect(center=(window_width // 2, window_height // 2 - 250))
        self.play_again_surf = pygame.image.load(join('Images', 'ui', 'buttons', 'play_again.png'))
        self.play_again_surf = pygame.transform.rotozoom(self.play_again_surf, 0, 0.7)

        # Combat Entities & Icons
        self.bullet_surf = pygame.image.load(join('Images', 'gun', 'bullet.png')).convert_alpha()
        self.bullet_surf = pygame.transform.rotozoom(self.bullet_surf, 0, 0.5)

        # Zombie Animation Frame Import
        self.enemy_frames = {}
        folders = ['zombie_1', 'zombie_2']
        for folder in folders:
            self.enemy_frames[folder] = []
            folder_path = join('Images', 'enemies', folder)
            try:
                for folder_root, _, file_names in walk(folder_path):
                    img_files = [f for f in file_names if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                    for file_name in sorted(img_files, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_root, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        surf = pygame.transform.rotozoom(surf, 0, 0.3)
                        self.enemy_frames[folder].append(surf)
            except Exception as e:
                print(f"Error loading normal enemy folder '{folder}': {e}")

        # Unique Boss Frame Import Loop
        self.boss_frames = []
        boss_folder_path = join('Images', 'enemies', 'boss')
        try:
            for folder_root, _, file_names in walk(boss_folder_path):
                img_files = [f for f in file_names if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                for file_name in sorted(img_files, key=lambda name: int(name.split('.')[0])):
                    full_path = join(folder_root, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.boss_frames.append(surf)
        except Exception as e:
            print(f"Error loading boss folder: {e}")
            if self.enemy_frames:
                self.boss_frames = choice(list(self.enemy_frames.values()))

    def import_assets(self):
        """Loads data packages from Tiled."""
        self.tmx_maps = {
            'world': load_pygame(join('data', 'maps', 'world.tmx'))
        }

    def apply_difficulty(self, mode):
        """Overrides configurations dynamically depending on chosen difficulty tier."""
        self.is_infinite_mode = False
        if mode == 'easy':
            self.survival_goal = SURVIVAL_TIME                     
            self.boss_kill_milestone = BOSS_MILESTONE - 10           
            self.stamina_recovery = PLAYER_STAMINA_RECOVERY           
            pygame.time.set_timer(self.enemy_event, int(ENEMY_SPAWN * 0.5)) 
            self.player_health = PLAYER_HEALTH                    
            self.difficulty_speed_modifier = 1.2     

            self.boss_difficulty_health = int(BOSS_HEALTH * 0.75)             
            self.boss_difficulty_speed_modifier = BOSS_SPEED * 0.70
            
        elif mode == 'medium':
            self.survival_goal = SURVIVAL_TIME - 120        
            self.boss_kill_milestone = BOSS_MILESTONE
            self.stamina_recovery = 25 
            pygame.time.set_timer(self.enemy_event, ENEMY_SPAWN)
            self.player_health = PLAYER_HEALTH
            self.difficulty_speed_modifier = 1.75

            self.boss_difficulty_health = BOSS_HEALTH             
            self.boss_difficulty_speed_modifier = BOSS_SPEED 
            
        elif mode == 'hard':
            self.survival_goal = SURVIVAL_TIME  - 300                    
            self.boss_kill_milestone = BOSS_MILESTONE + 10                
            self.stamina_recovery = 15                    
            pygame.time.set_timer(self.enemy_event, int(ENEMY_SPAWN * 0.5))  
            self.player_health = PLAYER_HEALTH              
            self.difficulty_speed_modifier = 2

            self.boss_difficulty_health = int(BOSS_HEALTH * 1.75)             
            self.boss_difficulty_speed_modifier = BOSS_SPEED * 1.70
            
        elif mode == 'infinite':
            self.is_infinite_mode = True
            self.infinite_level = 1
            self.survival_goal = 999999                   
            self.boss_kill_milestone = 999999             
            self.stamina_recovery = PLAYER_STAMINA_RECOVERY
            pygame.time.set_timer(self.enemy_event, ENEMY_SPAWN) 
            self.player_health = PLAYER_HEALTH                      
            self.difficulty_speed_modifier = 1.0          
            self.last_boss_spawn_time = pygame.time.get_ticks()
            self.boss_spawned = False     

    def setup(self, tmx_map, player_start_pos):
        """Generates game geometry, collisions, and spawns based on active map grid."""
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.enemy_sprites.empty()
        self.spawn_positions = []
        self.boss_spawned = False

        # Ground Layer Mapping
        for x, y, image in tmx_map.get_layer_by_name('Ground').tiles():
            BaseSprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        # Solid Structural Layers
        for obj in tmx_map.get_layer_by_name('Objects1'):
            if obj.image:
                scaled_image = pygame.transform.scale(obj.image, (int(obj.width), int(obj.height)))
                CollisionSprite((obj.x, obj.y), scaled_image, (self.all_sprites, self.collision_sprites))

        # Ambient Structural Decoration
        for obj in tmx_map.get_layer_by_name('Objects2'):
            if obj.image:
                scaled_image = pygame.transform.scale(obj.image, (int(obj.width), int(obj.height)))
                DecorationSprite((obj.x, obj.y), scaled_image, self.all_sprites)
                
        # Hidden Invisible Bounds Layout
        for obj in tmx_map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        
        # Entity Spawning Handlers
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                if player_start_pos:
                    coords = player_start_pos
                else:
                    coords = (obj.x, obj.y)
                if isinstance(coords, str):
                    split_text = coords.split(',')
                    spawn_coords = (int(split_text[0]), int(split_text[1]))
                else:
                    spawn_coords = coords
                
                self.player = Player(spawn_coords, self.all_sprites, self.collision_sprites)
                
                if hasattr(self, 'player_health'):
                    self.player.health = self.player_health
                    
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def spawn_boss(self):
        """Instantly spawns a single Boss unit with scaled health parameters."""
        if self.spawn_positions:
            boss_pos = choice(self.spawn_positions)
            boss_enemy = Enemy(boss_pos, self.boss_frames, 
                  (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, is_boss=True)
            
            if self.is_infinite_mode:
                scaled_health = BOSS_HEALTH + (self.infinite_level * 5)
                boss_enemy.health = scaled_health
                boss_enemy.max_health = scaled_health
                boss_enemy.speed = BOSS_SPEED + (self.infinite_level * 10)

    def input_shooting(self):
        """Handles weapon fire commands triggered by Left Click."""
        if pygame.mouse.get_pressed()[0] and self.can_shoot: 
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
    
    def gun_timer(self):
        """Tracks combat cooldown phases on weapon mechanics."""
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True
    
    def handle_sprint(self, dt):
        """Tracks sprint requests, stamina usage, and cooldown management."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LSHIFT] and self.stamina > 0 and not self.sprint_cooldown:
            self.is_sprinting = True
            self.player.speed = self.sprint_speed
            self.stamina -= self.stamina_drain * dt

            if self.stamina <= 0:
                self.stamina = 0
                self.sprint_cooldown = True
                self.cooldown_time = pygame.time.get_ticks()
        else:
            self.is_sprinting = False
            self.player.speed = self.normal_speed

            if self.sprint_cooldown:
                if pygame.time.get_ticks() - self.cooldown_time >= self.cooldown_duration:
                    self.sprint_cooldown = False
            else:
                if self.stamina < self.max_stamina:
                    self.stamina += self.stamina_recovery * dt
                    self.stamina = min(self.stamina, self.max_stamina)

    def check_collisions(self):
        """Resolves structural physics overlaps between weapons, enemies, and player."""
        import random  # Ensures random distributions are accessible locally
        current_time = pygame.time.get_ticks()

        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                if pygame.sprite.spritecollide(bullet, self.collision_sprites, False):
                    self.shoot_object_sound.play()
                    bullet.kill()
                    continue

                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        if sprite.death_time == 0:
                            if sprite.is_boss:
                                sprite.health -= 1
                                if sprite.health <= 0:
                                    sprite.destroy()
                                    self.zombies_killed += 1
                                    self.kill_sound.play()
                                    
                                    if not self.is_infinite_mode:
                                        self.game_state = 'story'
                                        self.story_mode = 'outro'
                                        self.current_scene_index = 0
                                        self.scene_progress = 0.0
                                        self.text_visible_chars = 0.0
                                        bullet.kill()
                                        return  
                                    else:
                                        self.infinite_level += 1 
                            else:
                                sprite.destroy()
                                self.zombies_killed += 1
                                self.kill_sound.play()

                                # --- BOOSTER DROP SYSTEM WITH WEIGHTED PERCENTAGES ---
                                if self.is_infinite_mode and random.random() <= 0.25: # 25% overall drop chance
                                    roll = random.random()
                                    self.booster_start_time = current_time
                                    
                                    if roll < 0.40:       # 40% chance of the drop for Speed Boost
                                        self.booster_active = 'speed'
                                        self.normal_speed = PLAYER_SPEED * 1.5
                                        self.sprint_speed = (PLAYER_SPEED * 1.8) * 1.4
                                    elif roll < 0.80:     # 40% chance of the drop for Rapid Fire
                                        self.booster_active = 'fire_rate'
                                        self.gun_cooldown = GUN_COOLDOWN // 2
                                    else:                 # 20% chance of the drop for Invisibility
                                        self.booster_active = 'invisibility'

                            if not self.is_infinite_mode and self.game_state != 'story':
                                if self.zombies_killed >= self.boss_kill_milestone and not self.boss_spawned:
                                    if self.spawn_positions:
                                        self.spawn_boss()
                                        self.boss_spawned = True
                                    
                    bullet.kill()
        
        if self.player.is_vulnerable:
            # Block physical damage ticks entirely if the player has active invisibility
            if self.is_infinite_mode and self.booster_active == 'invisibility':
                pass
            else:
                colliding_enemies = [
                    enemy for enemy in self.enemy_sprites 
                    if enemy.hitbox_rect.colliderect(self.player.hitbox_rect) and enemy.death_time == 0
                ]
                
                if colliding_enemies:
                    self.player.health -= 1
                    self.player.is_vulnerable = False
                    self.player.hit_time = current_time
                    self.player_hit_sound.play()
                    
                    if self.player.health <= 0:
                        # Update endless records if applicable before entering game over state
                        if self.is_infinite_mode:
                            if self.infinite_level > self.best_infinite_stage:
                                self.best_infinite_stage = self.infinite_level
                                
                        self.game_state = 'game_over'
                 
    def update_highscores(self):
        """Updates persistence high scores upon terminal death updates."""
        if self.zombies_killed > self.highest_kills:
            self.highest_kills = self.zombies_killed
        if self.survival_time > self.best_survival_time:
            self.best_survival_time = self.survival_time
                    
    def format_time(self, seconds):
        """Helper utility converting seconds into structured MM:SS strings."""
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"

    def event_loop(self):
        """Polls engine execution system inputs, key hits, and interaction triggers."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.click_sound.play()
                    self.running = False
                if event.key == pygame.K_SPACE or event.key == pygame.K_p:
                    if self.game_state == 'game':
                        self.click_sound.play()
                        self.game_state = 'paused'
                    elif self.game_state == 'paused':
                        self.click_sound.play()
                        self.game_state = 'game'
                        
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if self.game_state == 'game':
                    if self.pause_icon_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.game_state = 'paused'
                
                elif self.game_state == 'menu':
                    if not self.game_has_started:
                        if self.play_button_rect.collidepoint(mouse_pos):
                            self.click_sound.play()
                            self.game_state = 'gamemode_selection'
                        elif self.menu_quit_rect.collidepoint(mouse_pos):
                            self.running = False
                    else:
                        if self.continue_rect.collidepoint(mouse_pos):
                            self.game_state = 'game'
                        elif self.newgame_rect.collidepoint(mouse_pos):
                            self.click_sound.play()
                            self.game_state = 'gamemode_selection'
                        elif self.menu_quit2_rect.collidepoint(mouse_pos):
                            self.running = False
                            
                elif self.game_state == 'gamemode_selection':
                    selected = False
                    mode_chosen = None
                    if self.easy_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        mode_chosen = 'easy'
                        selected = True
                    elif self.medium_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        mode_chosen = 'medium'
                        selected = True
                    elif self.hard_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        mode_chosen = 'hard'
                        selected = True
                    elif self.infinite_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        mode_chosen = 'infinite'
                        selected = True
                        
                    if selected:
                        self.game_has_started = True
                        self.zombies_killed = 0
                        self.survival_time = 0 
                        self.setup(self.tmx_maps['world'], None) 
                        self.apply_difficulty(mode_chosen)
                        self.init_storyline() 
                        self.game_state = 'story' 
                        
                elif self.game_state == 'story':
                    # Determine which list collection is actively being used
                    active_list = self.outro_scenes if self.story_mode == 'outro' else self.story_scenes
                    
                    if self.skip_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        if self.story_mode == 'outro':
                            self.update_highscores()
                            self.game_state = 'victory'
                        else:
                            self.game_state = 'directions'
                    else:
                        self.click_sound.play()
                        self.current_scene_index += 1
                        
                        # Compare directly against the entire total scene length count
                        if self.current_scene_index >= len(active_list):
                            if self.story_mode == 'outro':
                                self.update_highscores()
                                self.game_state = 'victory'
                            else:
                                self.game_state = 'directions'
                        else:
                            self.scene_progress = 0.0
                            self.text_visible_chars = 0.0
                
                elif self.game_state == 'directions':
                    self.click_sound.play()
                    self.game_state = 'game'
                
                elif self.game_state == 'paused':
                    if self.resume_rect.collidepoint(mouse_pos) or self.pause_icon_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.game_state = 'game'
                    elif self.menu_rect_pause.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.game_state = 'menu'
                    elif self.quit_rect_pause.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.running = False
                        
                elif self.game_state == 'game_over':
                    if self.gameover_try_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.setup(self.tmx_maps['world'], None)
                        self.survival_time = 0
                        self.zombies_killed = 0
                        self.game_state = 'game'
                        self.game_has_started = True
                    elif self.gameover_home_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.survival_time = 0
                        self.zombies_killed = 0
                        self.game_state = 'menu'
                    elif self.gameover_menu_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.survival_time = 0
                        self.zombies_killed = 0
                        self.game_state = 'menu'
                    elif self.gameover_exit_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.running = False
                        
                elif self.game_state == 'victory':
                    if self.play_again_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.setup(self.tmx_maps['world'], None)
                        self.survival_time = 0
                        self.zombies_killed = 0
                        self.game_state = 'game'
                        self.game_has_started = True
                    elif self.victory_home_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.survival_time = 0
                        self.zombies_killed = 0
                        self.game_state = 'menu'
                    elif self.victory_menu_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.survival_time = 0
                        self.zombies_killed = 0
                        self.game_state = 'menu'
                    elif self.victory_exit_rect.collidepoint(mouse_pos):
                        self.click_sound.play()
                        self.running = False

            if self.game_state == 'game' and event.type == self.enemy_event:
                spawned_enemy = Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, is_boss=False)
                if hasattr(self, 'difficulty_speed_modifier'):
                    spawned_enemy.speed *= self.difficulty_speed_modifier
                if hasattr(self, 'is_infinite_mode') and self.is_infinite_mode:
                    level_speed_multiplier = 1.0 + (self.infinite_level * 0.05)
                    spawned_enemy.speed *= level_speed_multiplier

    def run(self):
        """Executes full operational frame runtime pipeline loops."""
        while self.running:
            dt = self.clock.tick() / 1000
            current_time = pygame.time.get_ticks()
            
            self.event_loop()

            if self.game_state == 'menu':
                ui.draw_menu(self)
            elif self.game_state == 'gamemode_selection':
                ui.draw_difficulty_screen(self)
            elif self.game_state == 'story':
                ui.draw_story(self, dt)
            elif self.game_state == 'directions':
                self.screen.fill((0,0,0))
                ui.draw_directions(self)
            elif self.game_state == 'game':
                self.survival_time += dt
                if not self.is_infinite_mode and self.survival_time >= self.survival_goal:
                    self.survival_time = 0
                    self.zombies_killed = 0
                    self.game_state = 'game_over'

                if self.is_infinite_mode:
                    # 1. Manage Active Booster Expiration Cooldowns
                    if self.booster_active:
                        if current_time - self.booster_start_time >= self.booster_duration:
                            # Restore original baseline statistics configuration properties
                            self.normal_speed = PLAYER_SPEED
                            self.sprint_speed = PLAYER_SPEED * 1.8
                            self.gun_cooldown = GUN_COOLDOWN
                            self.player.image.set_alpha(255)
                            self.booster_active = None

                    # 2. Infinite Mode Boss Spawn Waves
                    time_since_last_boss_spawn = current_time - self.last_boss_spawn_time
                    if time_since_last_boss_spawn >= 30000: 
                        self.spawn_boss()
                        self.last_boss_spawn_time = current_time 

                self.input_shooting()
                self.gun_timer()
                self.handle_sprint(dt)
                
                self.all_sprites.update(dt)
                self.check_collisions()

                # --- CUSTOM VISUAL BLINKING LAYER PROCESSING ---
                if self.is_infinite_mode and self.booster_active == 'invisibility':
                    # A. Booster Invisibility Flashing (Distinct speed for power-up feedback)
                    if current_time - self.blink_timer >= 120: 
                        self.blink_visible = not self.blink_visible
                        self.blink_timer = current_time
                    self.player.image.set_alpha(160 if self.blink_visible else 40)

                elif not self.player.is_vulnerable:
                    # B. Default Damage Blinking (Activates when hit normally)
                    time_since_hit = current_time - getattr(self.player, 'hit_time', 0)
                    if (time_since_hit // 100) % 2 == 0:
                        self.player.image.set_alpha(0)   # Blinks completely invisible
                    else:
                        self.player.image.set_alpha(255) # Blinks visible
                else:
                    # C. Standard State (No boosters active, not currently damaged)
                    self.player.image.set_alpha(255)

                self.screen.fill((0, 0, 0))
                self.all_sprites.draw(self.player.rect.center)
                
                for enemy in self.enemy_sprites:
                    if enemy.is_boss:
                        enemy.draw_health_bar(self.screen, self.all_sprites.offset)

                ui.draw_boss_health_bar(self)
                ui.draw_health_bar(self)
                ui.draw_timer(self)
                ui.draw_stamina_bar(self)
                
                # --- DRAW THE ACTIVE BOOSTER HUD SYSTEM ---
                ui.draw_booster_hud(self)
                
                # Pause Icon Hover Darken
                mouse_pos = pygame.mouse.get_pos()
                if self.pause_icon_rect.collidepoint(mouse_pos):
                    hover_surf = self.pause_icon_surf.copy()
                    hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
                    self.screen.blit(hover_surf, self.pause_icon_rect)
                else:
                    self.screen.blit(self.pause_icon_surf, self.pause_icon_rect)
                    
            elif self.game_state == 'paused':
                self.all_sprites.draw(self.player.rect.center)

                pause_overlay = pygame.Surface((window_width, window_height))
                pause_overlay.fill((0, 0, 0))
                pause_overlay.set_alpha(150)
                self.screen.blit(pause_overlay, (0, 0))
                ui.draw_health_bar(self)
                ui.draw_timer(self)
                ui.draw_stamina_bar(self)
                ui.draw_pause(self)
            elif self.game_state == 'game_over':
                ui.draw_game_over(self)
            elif self.game_state == 'victory':
                ui.draw_victory(self)

            pygame.display.update()

        pygame.quit()
        exit()


if __name__ == '__main__':
    game = Game()
    game.run()