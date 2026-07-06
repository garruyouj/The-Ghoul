import pygame
from os.path import join
from settings import window_width, window_height

def draw_difficulty_screen(game):
    """Renders buttons for choosing difficulty selection."""
    game.screen.fill((20, 20, 25))
    
    # Title shadow text effect
    title_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 60)
    title_shadow = title_font.render("SELECT DIFFICULTY", True, (10, 10, 15))
    title_text = title_font.render("SELECT DIFFICULTY", True, (240, 230, 220))
    
    shadow_rect = title_shadow.get_rect(center=(window_width // 2 + 4, window_height // 2 - 200 + 4))
    title_rect = title_text.get_rect(center=(window_width // 2, window_height // 2 - 200))
    
    game.screen.blit(title_shadow, shadow_rect)
    game.screen.blit(title_text, title_rect)

    # Checks mouse collision to darken button when hovered
    mouse_pos = pygame.mouse.get_pos()
    modes = [
        {"surf": game.easy_surf, "rect": game.easy_rect},
        {"surf": game.medium_surf, "rect": game.medium_rect},
        {"surf": game.hard_surf, "rect": game.hard_rect},
        {"surf": game.infinite_surf, "rect": game.infinite_rect}
    ]

    for mode in modes:
        if mode["rect"].collidepoint(mouse_pos):
            hover_surf = mode["surf"].copy()
            hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
            game.screen.blit(hover_surf, mode["rect"])
        else:
            game.screen.blit(mode["surf"], mode["rect"])

def draw_health_bar(game):
    """Renders player dynamic health gauge layout tracking metrics."""
    bar_width, bar_height = 250, 20
    x, y = 350, 780
    max_health_calc = game.player_health if hasattr(game, 'player_health') else 5
    health_ratio = game.player.health / max_health_calc
    current_width = bar_width * health_ratio
    
    pygame.draw.rect(game.screen, (40, 40, 40), (x, y, bar_width, bar_height), border_radius=8)
    pygame.draw.rect(game.screen, (200, 50, 50), (x, y, current_width, bar_height), border_radius=8)
    pygame.draw.rect(game.screen, "white", (x, y, bar_width, bar_height), 2, border_radius=8)
    
    font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 18)
    text = font.render("HEALTH", True, "white")
    game.screen.blit(text, (x, y - 25))

def draw_boss_health_bar(game):
    """Renders dynamic boss health gauge tracking matrix whenever one exists."""
    boss = None
    for enemy in game.enemy_sprites:
        if hasattr(enemy, "is_boss") and enemy.is_boss and enemy.death_time == 0:
            boss = enemy
            break
            
    if not boss:
        return

    bar_width, bar_height = 120, 30
    x = (window_width - bar_width) // 2
    y = 40
    max_health = boss.max_health if hasattr(boss, 'max_health') else 20
    health_ratio = boss.health / max_health
    current_width = bar_width * health_ratio
    
    pygame.draw.rect(game.screen, (40, 40, 40), (x, y, bar_width, bar_height), border_radius=10)
    pygame.draw.rect(game.screen, (220, 30, 30), (x, y, current_width, bar_height), border_radius=10)
    pygame.draw.rect(game.screen, "white", (x, y, bar_width, bar_height), 2, border_radius=10)
    
    font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 24)
    text = font.render("BOSS", True, "white")
    text_rect = text.get_rect(center=(window_width // 2, y - 20))
    game.screen.blit(text, text_rect)

def draw_timer(game):
    """Displays formatted mission timing interface elements safely on display frames."""
    if hasattr(game, 'is_infinite_mode') and game.is_infinite_mode:
        timer_text = game.format_time(game.survival_time)
        color = "white"
    else:
        remaining_time = max(0, game.survival_goal - game.survival_time)
        timer_text = game.format_time(remaining_time)

        if remaining_time <= 30:
            color = (200,50,50)
        else:
            color = "white"

    timer_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 36)
    
    # Shadow text effect
    shadow_surf = timer_font.render(timer_text, True, (20, 20, 20))
    text_surf = timer_font.render(timer_text, True, color)
    
    text_rect = text_surf.get_rect(topleft=(350, 715))
    game.screen.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
    game.screen.blit(text_surf, text_rect)

    if hasattr(game, 'is_infinite_mode') and game.is_infinite_mode:
        level_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 24)
        level_shadow_surf = level_font.render(f"STAGE {game.infinite_level}", True, (20, 20, 20))
        level_text_surf = level_font.render(f"STAGE {game.infinite_level}", True, (255, 215, 0))
        level_rect = level_text_surf.get_rect(midtop=(window_width // 2, text_rect.bottom + 10))
        game.screen.blit(level_shadow_surf, (level_rect.x + 2, level_rect.y + 2))
        game.screen.blit(level_text_surf, level_rect)

def draw_stamina_bar(game):
    """Displays stamina resource capacity graphics overlays."""
    bar_width, bar_height = 250, 25
    x, y = 350, 840
    
    pygame.draw.rect(game.screen, (40, 40, 40), (x, y, bar_width, bar_height), border_radius=8)
    stamina_ratio = game.stamina / game.max_stamina
    current_width = bar_width * stamina_ratio
    
    if game.sprint_cooldown:
        color = (255, 60, 60)
    elif game.is_sprinting:
        color = (255, 220, 50)
    else:
        color = (80, 220, 255)
        
    pygame.draw.rect(game.screen, color, (x, y, current_width, bar_height), border_radius=8)
    pygame.draw.rect(game.screen, "white", (x, y, bar_width, bar_height), 2, border_radius=8)
    
    stamina_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 18)
    text = stamina_font.render("EXHAUSTED" if game.sprint_cooldown else "STAMINA", True, "white")
    game.screen.blit(text, (x, y - 25))

def draw_menu(game):
    """Displays root title dashboard views."""
    game.screen.fill((20, 20, 25))
    game.screen.blit(game.menu_bg_surf, game.menu_bg_rect)
    game.screen.blit(game.logo_surf, game.logo_rect)
    mouse_pos = pygame.mouse.get_pos()
    
    if not game.game_has_started:
        if game.play_button_rect.collidepoint(mouse_pos):
            hover_surf = game.play_button_surf.copy()
            hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
            game.screen.blit(hover_surf, game.play_button_rect)
        else:
            game.screen.blit(game.play_button_surf, game.play_button_rect)

        if game.menu_quit_rect.collidepoint(mouse_pos):
            hover_surf = game.quit_button_surf.copy()
            hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
            game.screen.blit(hover_surf, game.menu_quit_rect)
        else:
            game.screen.blit(game.quit_button_surf, game.menu_quit_rect)
    else:
        if game.continue_rect.collidepoint(mouse_pos):
            hover_surf = game.continue_button_surf.copy()
            hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
            game.screen.blit(hover_surf, game.continue_rect)
        else:
            game.screen.blit(game.continue_button_surf, game.continue_rect)

        if game.newgame_rect.collidepoint(mouse_pos):
            hover_surf = game.newgame_button_surf.copy()
            hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
            game.screen.blit(hover_surf, game.newgame_rect)
        else:
            game.screen.blit(game.newgame_button_surf, game.newgame_rect)

        if game.menu_quit2_rect.collidepoint(mouse_pos):
            hover_surf = game.quit_button_surf.copy()
            hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
            game.screen.blit(hover_surf, game.menu_quit2_rect)
        else:
            game.screen.blit(game.quit_button_surf, game.menu_quit2_rect)

def draw_pause(game):
    """Renders pause configurations directly over active display grids."""
    mouse_pos = pygame.mouse.get_pos()
    
    # Text Headline
    text_surf = game.pause_font.render("GAME PAUSED", True, "red")
    text_rect = text_surf.get_rect(center=(window_width // 2, window_height // 2 - 200))
    game.screen.blit(text_surf, text_rect)

    if game.resume_rect.collidepoint(mouse_pos):
        hover_surf = game.resume_button_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.resume_rect)
    else:
        game.screen.blit(game.resume_button_surf, game.resume_rect)

    if game.menu_rect_pause.collidepoint(mouse_pos):
        hover_surf = game.menu_button_pause_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.menu_rect_pause)
    else:
        game.screen.blit(game.menu_button_pause_surf, game.menu_rect_pause)

    if game.quit_rect_pause.collidepoint(mouse_pos):
        hover_surf = game.quit_button_pause_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.quit_rect_pause)
    else:
        game.screen.blit(game.quit_button_pause_surf, game.quit_rect_pause)

def draw_directions(game):
    """Displays key bindings, operational rules, and movement instructions with multi-colored keywords."""
    mouse_pos = pygame.mouse.get_pos()
    
    # 1. Clear Screen Canvas Background
    game.screen.fill((0, 0, 0))
    
    # 2. Render Title Header
    dir_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 48)
    title_surf = dir_font.render("HOW TO PLAY", True, (255, 215, 0)) # Gold
    title_rect = title_surf.get_rect(center=(window_width // 2, 150))
    game.screen.blit(title_surf, title_rect)
    
    # 3. Base Body Font Configuration
    body_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 24)
    
    instructions = [
        "WASD or ARROW KEYS  -  Move character around the map",
        "LEFT CLICK MOUSE    -  Aim and shoot projectiles at the enemies",
        "SHIFT KEY           -  Sprint (Consumes Stamina resource bar)",
        "SPACEBAR or P KEY   -  Toggle game pausing system",
        "ESCAPE KEY          -  Instantly exit the game",
        "",
        "OBJECTIVE:",
        "NORMAL MODES: THE GHOUL is to enraged the boss to spawn\nby killing specific amount of zombies, \nDefeat the Central Host to win!",
        "ENDLESS MODE: every wave, the boss will appear and \nTHE GHOUL is to survive as long as you can"
    ]
    
    # --- COLOR KEYWORD MAP DICTIONARY ---
    # Add any word or phrase you want to change colors here!
    color_map = {
        "THE GHOUL": (0, 255, 0),              # Green (Handles your second line variation)
        "NORMAL MODES:": (255, 69, 0),   # Red-Orange
        "ENDLESS MODE:": (255, 69, 0),   # Red-Orange
        "The Central Host": (255, 0, 255),# Magenta / Purple Boss Highlight
        "OBJECTIVE:": (255, 215, 0)      # Gold
    }
    
    start_y = 280
    base_x = 450 # Static anchor line alignment margin for the objectives block
    
    for line in instructions:
        sub_lines = line.split('\n')
        
        # Track paragraph adjustments across line breaks
        is_continuation_line = False
        header_offset = 0
        
        for sub_line in sub_lines:
            # Check if this line belongs to the left-justified objectives block
            is_objective_block = any(keyword in line for keyword in ["OBJECTIVE:", "NORMAL MODES:", "ENDLESS MODE:"])
            
            # 1. Break down the line into individual segments by matching against our color dictionary keys
            segments = []
            working_text = sub_line
            
            while working_text:
                earliest_match = None
                earliest_index = len(working_text)
                match_keyword = ""
                
                # Check which keyword appears first in our current processing fragment string
                for keyword in color_map:
                    idx = working_text.find(keyword)
                    if idx != -1 and idx < earliest_index:
                        earliest_index = idx
                        earliest_match = keyword
                
                if earliest_match:
                    # Capture text before the keyword (default white)
                    if earliest_index > 0:
                        segments.append((working_text[:earliest_index], (255, 255, 255)))
                    # Capture the highlighted keyword with its custom mapped color palette
                    segments.append((earliest_match, color_map[earliest_match]))
                    # Slice out processed text strings
                    working_text = working_text[earliest_index + len(earliest_match):]
                else:
                    # No more matching keywords found; dump remaining text line group as plain white
                    segments.append((working_text, (255, 255, 255)))
                    break
            
            # 2. Determine initial drawing horizontal position configurations
            if is_objective_block:
                # Track indentation adjustments if it's the text row directly below a \n character
                if "NORMAL MODES:" in sub_line:
                    header_offset = body_font.render("NORMAL MODES: ", True, "white").get_width()
                elif "ENDLESS MODE:" in sub_line:
                    header_offset = body_font.render("ENDLESS MODE: ", True, "white").get_width()
                
                current_x = base_x + header_offset if is_continuation_line else base_x
            else:
                # Calculate the combined full width of all segments to center the keyboard layout controls lines
                total_width = sum(body_font.render(text, True, "white").get_width() for text, _ in segments)
                current_x = (window_width - total_width) // 2
                
            # 3. Draw each processed colored string fragment side by side across the screen surface layout
            for text, color in segments:
                if text:
                    text_surf = body_font.render(text, True, color)
                    game.screen.blit(text_surf, (current_x, start_y))
                    current_x += text_surf.get_width()
            
            is_continuation_line = True
            start_y += 45

    # 4. Flashing Bottom Screen Action Prompt Button Selection
    prompt_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 28)
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        prompt_surf = prompt_font.render("CLICK ANYWHERE TO CONTINUE TO THE WORLD MAP", True, "red")
    else:
        prompt_surf = prompt_font.render("CLICK ANYWHERE TO CONTINUE TO THE WORLD MAP", True, (40, 40, 40))
        
    prompt_rect = prompt_surf.get_rect(center=(window_width // 2, window_height - 150))
    game.screen.blit(prompt_surf, prompt_rect)

def draw_game_over(game):
    """Displays standard terminal death dashboard layouts on screen viewports."""
    game.screen.fill('black')
    game.screen.blit(game.game_over_surf, game.game_over_rect)
    
    stats_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 30)
    
    # Existing metrics
    survival_time_text = stats_font.render(f"Survival Time: {game.format_time(game.survival_time)}", True, "white")
    survival_rect = survival_time_text.get_rect(center=(window_width // 2, window_height // 2 - 160))
    
    kills_text = stats_font.render(f"Zombies Killed: {game.zombies_killed}", True, "white")
    kills_rect = kills_text.get_rect(center=(window_width // 2, window_height // 2 - 110))
    
    
    if hasattr(game, 'is_infinite_mode') and game.is_infinite_mode:
        stage_text = stats_font.render(f"Highest Stage Reached: {game.infinite_level}", True, "white")
        stage_rect = stage_text.get_rect(center=(window_width // 2, window_height // 2 - 60))
        game.screen.blit(stage_text, stage_rect)
        
        # Adjust existing lower metrics downwards so they don't overlap in endless mode
        best_time_rect_y = window_height // 2 + 40
        highest_kills_rect_y = window_height // 2 + 90
    else:
        # Standard layout positions for normal game modes
        best_time_rect_y = window_height // 2 - 50
        highest_kills_rect_y = window_height // 2

    # Updated positions using the dynamic offsets calculated above
    best_time_text = stats_font.render(f"Best Survival Time: {game.format_time(game.best_survival_time)}", True, "yellow")
    best_time_rect = best_time_text.get_rect(center=(window_width // 2, best_time_rect_y))
    
    highest_kills_text = stats_font.render(f"Highest Kills: {game.highest_kills}", True, "red")
    highest_kills_rect = highest_kills_text.get_rect(center=(window_width // 2, highest_kills_rect_y))

    # --- Leave the rest of the buttons code (try_again, menu, exit, etc.) exactly as it is ---
    game.gameover_try_rect = game.try_again_surf.get_rect(center=(window_width // 2, window_height // 2 + 180)) # Shifted button layout slightly lower to account for new space
    game.gameover_menu_rect = game.menu_button_surf.get_rect(center=(window_width // 2, window_height // 2 + 280))
    game.gameover_exit_rect = game.exit_icon_surf.get_rect(center=(window_width // 2 + 590, window_height // 2 - 320))
    game.gameover_home_rect = game.home_icon_surf.get_rect(center=(window_width // 2 + 520, window_height // 2 - 320))

    mouse_pos = pygame.mouse.get_pos()
    
    if game.gameover_try_rect.collidepoint(mouse_pos):
        hover_surf = game.try_again_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.gameover_try_rect)
    else:
        game.screen.blit(game.try_again_surf, game.gameover_try_rect)

    if game.gameover_menu_rect.collidepoint(mouse_pos):
        hover_surf = game.menu_button_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.gameover_menu_rect)
    else:
        game.screen.blit(game.menu_button_surf, game.gameover_menu_rect)

    if game.gameover_home_rect.collidepoint(mouse_pos):
        hover_surf = game.home_icon_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.gameover_home_rect)
    else:
        game.screen.blit(game.home_icon_surf, game.gameover_home_rect)

    if game.gameover_exit_rect.collidepoint(mouse_pos):
        hover_surf = game.exit_icon_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.gameover_exit_rect)
    else:
        game.screen.blit(game.exit_icon_surf, game.gameover_exit_rect)

    # Rendering elements safely on frames
    game.screen.blit(survival_time_text, survival_rect)
    game.screen.blit(kills_text, kills_rect)

def draw_victory(game):
    """Displays standard win victory dashboard views."""
    game.screen.fill('black')
    game.screen.blit(game.you_survived_surf, game.you_survived_rect)
    
    stats_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 30)
    best_time_text = stats_font.render(f"Best Time: {game.format_time(game.best_survival_time)} ", True, "yellow")
    best_time_rect = best_time_text.get_rect(center=(window_width // 2, window_height // 2 - 150))
    
    kills_text = stats_font.render(f"Zombies Killed: {game.zombies_killed}", True, "white")
    kills_rect = kills_text.get_rect(center=(window_width // 2, window_height // 2 - 100))
    
    highest_kills_text = stats_font.render(f"Highest Kills: {game.highest_kills}", True, "red")
    highest_kills_rect = highest_kills_text.get_rect(center=(window_width // 2, window_height // 2 - 50))
    
    game.victory_menu_rect = game.menu_button_surf.get_rect(center=(window_width // 2, window_height // 2 + 210))
    game.victory_exit_rect = game.exit_icon_surf.get_rect(center=(window_width // 2 + 590, window_height // 2 - 320))
    game.victory_home_rect = game.home_icon_surf.get_rect(center=(window_width // 2 + 520, window_height // 2 - 320))
    game.play_again_rect = game.play_again_surf.get_rect(center=(window_width // 2, window_height // 2 + 90))

    mouse_pos = pygame.mouse.get_pos()
    
    if game.play_again_rect.collidepoint(mouse_pos):
        hover_surf = game.play_again_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.play_again_rect)
    else:
        game.screen.blit(game.play_again_surf, game.play_again_rect)

    if game.victory_menu_rect.collidepoint(mouse_pos):
        hover_surf = game.menu_button_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.victory_menu_rect)
    else:
        game.screen.blit(game.menu_button_surf, game.victory_menu_rect)

    if game.victory_home_rect.collidepoint(mouse_pos):
        hover_surf = game.home_icon_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.victory_home_rect)
    else:
        game.screen.blit(game.home_icon_surf, game.victory_home_rect)

    if game.victory_exit_rect.collidepoint(mouse_pos):
        hover_surf = game.exit_icon_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.victory_exit_rect)
    else:
        game.screen.blit(game.exit_icon_surf, game.victory_exit_rect)

    game.screen.blit(best_time_text, best_time_rect)
    game.screen.blit(kills_text, kills_rect)
    game.screen.blit(highest_kills_text, highest_kills_rect)

def draw_story(game, dt):
    """Processes typewriter calculations and updates current cinematic storyboards."""
    game.screen.fill('black')
    active_scenes = game.outro_scenes if game.story_mode == 'outro' else game.story_scenes

    if game.current_scene_index >= len(active_scenes):
        if game.story_mode == 'outro':
            game.update_highscores()
            game.game_state = 'victory'
        else:
            game.game_state = 'directions'
        return

    img_name, text_lines_list, start_x, end_x = active_scenes[game.current_scene_index]
    sub_folder = 'outro' if game.story_mode == 'outro' else 'intro'
    
    try:
        raw_img = pygame.image.load(join('Images', 'story', sub_folder, img_name)).convert_alpha()
    except FileNotFoundError:
        try:
            raw_img = pygame.image.load(join('images', 'story', sub_folder, img_name)).convert_alpha()
        except FileNotFoundError:
            raw_img = pygame.image.load(join('Images', 'story', img_name)).convert_alpha()

    game.scene_progress += game.pan_speed * dt
    if game.scene_progress > 1.0:
        game.scene_progress = 1.0
        
    render_x = start_x + (end_x - start_x) * game.scene_progress
    render_y = (window_height - raw_img.get_height()) // 2
    game.screen.blit(raw_img, (render_x, render_y))

    # Dark background bar for text layout safety
    text_bar = pygame.Surface((window_width, 180)) # Slightly taller to fit multi-lines
    text_bar.fill((0, 0, 0))
    text_bar.set_alpha(200)
    game.screen.blit(text_bar, (0, window_height // 2 + 140))

    # Calculate the grand total of characters across all rows combined in this scene
    total_chars = sum(len(line) for line in text_lines_list)
    
    if game.text_visible_chars < total_chars:
        game.text_visible_chars += game.text_speed * dt
        
    visible_chars_pool = int(game.text_visible_chars)
    
    # Starting baseline Y position inside the dark UI panel box
    current_y_position = window_height // 2 + 190
    
    # Process and build text layout sentence by sentence
    for line in text_lines_list:
        if visible_chars_pool > 0:
            # Take a slice of the string up to whatever typewriter allocation is left
            line_slice = line[0:visible_chars_pool]
            
            # Draw individual row lines centered perfectly along the horizontal midplane axis
            text_surf = game.story_font.render(line_slice, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(window_width // 2, current_y_position))
            game.screen.blit(text_surf, text_rect)
            
            # Step the Y anchor downwards by 35 pixels for the next sequence wrap line
            current_y_position += 35
            
            # Consume the number of processed characters from our visible allocation pool
            visible_chars_pool -= len(line)

    # Skip Button Interaction Framework
    mouse_pos = pygame.mouse.get_pos()
    if game.skip_rect.collidepoint(mouse_pos):
        hover_surf = game.skip_surf.copy()
        hover_surf.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)
        game.screen.blit(hover_surf, game.skip_rect)
    else:
        game.screen.blit(game.skip_surf, game.skip_rect)

def draw_booster_hud(game):
    """Displays active infinite mode boosters along with a remaining time progress tracker."""
    if not hasattr(game, 'is_infinite_mode') or not game.is_infinite_mode or not game.booster_active:
        return

    # Calculate remaining time left on active power-up allocation window
    current_time = pygame.time.get_ticks()
    elapsed = current_time - game.booster_start_time
    remaining_ms = max(0, game.booster_duration - elapsed)
    remaining_secs = remaining_ms / 1000.0

    # Configure distinct string colors and text descriptions for each booster
    if game.booster_active == 'speed':
        msg = f"SPEED BOOST: {remaining_secs:.1f}s"
        color = (100, 255, 255) # Cyan
    elif game.booster_active == 'fire_rate':
        msg = f"RAPID FIRE: {remaining_secs:.1f}s"
        color = (255, 100, 255) # Pink / Magenta
    elif game.booster_active == 'invisibility':
        msg = f"INVINCIBILITY: {remaining_secs:.1f}s"
        color = (100, 255, 100) # Bright Green
    else:
        return

    # Render out HUD indicators below health metrics area positions cleanly
    hud_font = pygame.font.Font(join("Fonts", "pixelated.ttf"), 22)
    
    # Shadow text effect
    shadow_surf = hud_font.render(msg, True, (15, 15, 15))
    text_surf = hud_font.render(msg, True, color)
    
    # Positioned neatly over the health bar area
    x_pos, y_pos = 350, 680
    game.screen.blit(shadow_surf, (x_pos + 2, y_pos + 2))
    game.screen.blit(text_surf, (x_pos, y_pos))