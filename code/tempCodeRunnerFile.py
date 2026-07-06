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