from settings import *

# lambda - shortcut way to write simple function
# vector2 - built in pygame class used to store, manipulate, and calculate 2d coordinates (x and y)

class AllSprites(pygame.sprite.Group):
    ''' Sets up camera group, and hold and manipulate objects simultaneously '''
    def __init__(self):
        super().__init__() # calls parent class constructor
        self.screen = pygame.display.get_surface() # gets main window surface
        self.offset = pygame.Vector2() # stores camera's how much to horizontally and vertically shift the world
    
    def draw(self, target_pos): # target_pos represents the player's world position coordinates
        # calculate the offset math based on where the player is walking
        self.offset.x = - (target_pos[0] - window_width / 2) # target_pos[0] is the horizontal  position of the player
        self.offset.y = - (target_pos[1] - window_height / 2) # target_pos[1] is the vertical position of the player
        # EXAMPLE: if position of player is like at x = 1000, then window_width is 1920, the offset will move to the left by 40 pixels

        # FLOOR TILES - goes through all sprite in this group, keeps only those who have variable called "ground"
        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')] 

        # ENTITIES AND OBJECT TILES - keeps that don't have attr 'ground'
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground')]

        # y-sorting to create depth
        for layer in [ground_sprites, object_sprites]: # draws ground first
            for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery): # sorts sprites by their vertical center position (lower number = higher on screen, hence it will be drawn first)
                self.screen.blit(sprite.image, sprite.rect.topleft + self.offset) # draws spritee at its normal position plus camera shift

        

