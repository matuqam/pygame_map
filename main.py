import pygame, sys
# constants such as keyboard key names ex.: K_e for 'e' key
from pygame.locals import *

# info on pygame
#
# pygame starts with a window or screen
# it displays surfaces on top of that window
# it calculates objects with rect (aka rectangles) objects


clock = pygame.time.Clock()
pygame.init() # initiates pygame

pygame.display.set_caption('Pygame Platformer')

WINDOW_SIZE = (600,400)
TILE_SIZE = 16

# Initialize and set size of a window or screen for display;
screen = pygame.display.set_mode(size=WINDOW_SIZE) # initiate the window

# pygame object for representing images
display = pygame.Surface((300,200)) # used as the surface for rendering, which is scaled
test_surface = pygame.Surface(size=(200,30))

# player variables
player_display_hub: bool = False
PLAYER_MOVEMENT_SPEED: int = 10
moving_right: bool = False
moving_left: bool = False
vertical_momentum: float = 0
air_timer: int = 0

true_scroll = [0,0]

# keyboard control mapings
jump, down, left, right = (K_SPACE, K_d, K_s, K_f)

def load_map(path):
    f = open(path + '.txt','r')
    rows = f.read()
    f.close()
    rows = rows.split('\n')
    game_map = []
    for row in rows:
        game_map.append(list(row))
    return game_map

game_map = load_map('map')

grass_img = pygame.image.load('grass.png')
dirt_img = pygame.image.load('dirt.png')

player_img = pygame.image.load('player.png').convert()
player_img.set_colorkey((255,255,255))

player_rect = pygame.Rect(100,100,5,13)

background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

def collision_test(rect,tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move_player(player_pos,movement,tiles):
    collision_types = {'top':False,'bottom':False,'right':False,'left':False}
    player_pos.x += movement[0]
    hit_list = collision_test(player_pos,tiles)
    for tile in hit_list:
        if movement[0] > 0:
            player_pos.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            player_pos.left = tile.right
            collision_types['left'] = True
    player_pos.y += movement[1]
    hit_list = collision_test(player_pos,tiles)
    # Player hit a block
    for tile in hit_list:
        # from the top (player is falling)
        if movement[1] > 0:
            player_pos.bottom = tile.top
            collision_types['bottom'] = True
        # from the bottom (player is jumping)
        elif movement[1] < 0:
            player_pos.top = tile.bottom
            collision_types['top'] = True
    return player_pos, collision_types

while True: # game loop
    display.fill((146,244,255)) # clear screen by filling it with blue

    true_scroll[0] += (player_rect.x-true_scroll[0]-152)/20
    true_scroll[1] += (player_rect.y-true_scroll[1]-106)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    # backgroud visuals
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0]-scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display,(14,222,150),obj_rect)
        else:
            pygame.draw.rect(display,(9,91,85),obj_rect)

    ## parallax movement
    tile_rects = []
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':
                display.blit(dirt_img,(x*TILE_SIZE-scroll[0],y*TILE_SIZE-scroll[1]))
            if tile == '2':
                display.blit(grass_img,(x*TILE_SIZE-scroll[0],y*TILE_SIZE-scroll[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect(x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE))
            x += 1
        y += 1

    LAST_TILE_POSITION = len(game_map[0] * TILE_SIZE) # number of tiles per row * tile width

    # player
    ## movement
    player_movement = [0,0]
    if moving_right == True:
        player_movement[0] += PLAYER_MOVEMENT_SPEED
    if moving_left == True:
        player_movement[0] -= PLAYER_MOVEMENT_SPEED
    player_movement[1] += vertical_momentum
    vertical_momentum += 0.2
    vertical_momentum = min(vertical_momentum, 3)

    # collisions
    player_rect,collisions = move_player(player_rect,player_movement,tile_rects)
    if player_rect.y > 200:
        player_rect.x, player_rect.y = (100, 100)

    if collisions['bottom'] or collisions['top']:
        air_timer = 0
        vertical_momentum = 0
    else:
        air_timer += 1

    ## avatar display
    # Note all physics calculations are done with real dimentions but scroling
    # visuals are adjusted with scroll
    display.blit(player_img,(player_rect.x-scroll[0],player_rect.y-scroll[1]))

    # keyboard events
    for event in pygame.event.get(): # event loop
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # player keyboard actions
        if event.type == KEYDOWN:
            if event.key == right:
                moving_right = True
            if event.key == left:
                moving_left = True
            if event.key == jump:
                if air_timer < 6:
                    vertical_momentum = -5
        if event.type == KEYUP:
            if event.key == right:
                moving_right = False
            if event.key == left:
                moving_left = False
        
        # Toggle display hub
        if event.type == KEYDOWN and event.key == K_h:
            player_display_hub = not player_display_hub

    # draw one image onto another -- this does the view effect   
    screen.blit(
        pygame.transform.scale(
            surface=display, size=WINDOW_SIZE), 
            dest=(0, 0)
            )
    # TESTS
    ## refresh surface
    test_surface.fill(color=(200,180,150))
    ## add player image to test surface
    test_surface.blit(source=player_img, dest=((200-5) * player_rect.x/(LAST_TILE_POSITION+TILE_SIZE), 8))
    ## add test_surface to screen
    player_display_hub = player_display_hub and screen.blit(source=test_surface, dest=(0,0), area=None)
    
    pygame.display.update()
    clock.tick(60)
