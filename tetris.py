import pygame
import random
from pygame.mixer import Sound
from pygame.locals import *
import os

pygame.mixer.init()
pygame.init()
pygame.font.init()
# creating the data structure for pieces
# setting up global vars
# functions
# - create_grid
# - draw_grid
# - draw_window
# - rotating shape in main
# - setting up the main

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# SHAPE FORMATS

S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

# AUDIO SETTINGS
music_enabled = True
sfx_enabled = True
show_music_off_text = False
show_sound_fx_off_text = False
menu_music = True

def load_music_index():
    try:
        with open("music_index.txt", "r") as f:
            index = int(f.read())
            if 0 <= index < len(music_files):
                return index
            else:
                return 0
    except:
        return 0
    
# Find all MP3 files in the folder
music_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
current_music_index = load_music_index()
    
def save_music_index(index):
    with open("music_index.txt", "w") as f:
        f.write(str(index))

def play_music():
    global music_enabled, current_music_index
    if not music_enabled: 
        return
    if not music_files: 
        return

    pygame.mixer.music.load(music_files[current_music_index])
    pygame.mixer.music.play(-1)

def toggle_music():
    global music_enabled, show_music_off_text, menu_music
    music_enabled = not music_enabled
    if music_enabled:
        show_music_off_text = False
        play_music()
        menu_music = True
    else:
        pygame.mixer.music.pause()
        show_music_off_text = True
        menu_music = False

def next_music_track():
    global current_music_index
    if not music_files: 
        return
    current_music_index = (current_music_index + 1) % len(music_files)
    save_music_index(current_music_index)
    play_music()

def prev_music_track():
    global current_music_index
    if not music_files:
        return
    current_music_index = (current_music_index - 1) % len(music_files)
    save_music_index(current_music_index)
    play_music()

def play_sfx(soundfile, channel=0):
    if sfx_enabled:
        pygame.mixer.Channel(channel).play(Sound(soundfile))

def toggle_sfx():
    global sfx_enabled
    sfx_enabled = not sfx_enabled
    if not sfx_enabled:
        global show_sound_fx_off_text
        show_sound_fx_off_text = True
    else:
        show_sound_fx_off_text = False

def load_max_score():
    try:
        with open("highscore.txt", "r") as f:
            score = int(f.read())
            return score
    except:
        return 0

MAX_SCORE = load_max_score()  # global max score variable
    
def save_max_score(score):   
    with open("highscore.txt", "w") as f:
        f.write(str(score))

# index 0 - 6 represent shape
# piece class contains a constructor that takes in the parameters column, row, shape

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


# uses the grid data structure, each element in the list is
# a tuple representing the color black

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:  # checks if position in grid is in locked
                # positions, (a piece that's already fallen) and modify the grid to show the pieces
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]  # flattens the list into 1D

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):  # checks if positions are above the screen
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))

def display_title(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() - 300))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() - 100))

def draw_text_upper_right(surface, text, size, color, padding = 20, adjust = 0):
     font = pygame.font.Font('Tetris.ttf', size)
     label = font.render(text, True, color)
    # Upper right = screen_width - label_width - padding
     x = surface.get_width() - label.get_width() - padding + adjust
     y = padding  # top padding
     surface.blit(label, (x, y))

def draw_left_controls(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() + 10))


def draw_right_controls(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() + 40))


def draw_up_controls(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() + 70))


def draw_down_controls(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() + 100))


def draw_space_controls(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() + 130))

def draw_pause_controls(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() + 160))
    
def draw_music_controls(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() + 190))

def draw_sound_controls(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() + 220))

def draw_switch_controls(surface, text, size, color):
    font = pygame.font.Font('Tetris.ttf', size)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() + 250))

def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):  # for every row draw a line, draws 20 verticals and 10 horizontals
        pygame.draw.line(surface, (0, 0, 0), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (0, 0, 0), (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))

def clear_rows(grid, locked):
    '''
    Clear the rows by scanning each filled space,
    make them empty and insert a new row for each row of space removed
    '''
    inc = 0
    for i in range(len(grid)):
        filled = (0, 0, 0) not in grid[i]
        if filled:
            grid.pop(i) # remove the whole line
            grid.insert(0, [(0,0,0) for _ in grid[0]])
            play_sfx("cleared.wav", channel=3)
            inc += 1
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == (0, 0, 0):
                locked.pop((j, i), None)
            else:
                locked[(j, i)] = grid[i][j]
    return inc

def draw_next_shape(shape, surface):
    font = pygame.font.Font('Tetris.ttf', 20)
    label = font.render('Next Shape:', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j * 30, sy + i * block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))

def update_score(nscore):
    score = max_score()
    # print("Max {}, Curr {}".format(score, nscore))
    if score < nscore:
        global MAX_SCORE
        MAX_SCORE = nscore
        save_max_score(nscore)
        #high_score_menu(win)
        return True
    return False

def max_score():
    return MAX_SCORE

def draw_window(surface, grid, score=0, last_score=0):
    surface.fill((0, 0, 0))  # fill the surface with black
    pygame.font.init()
    font = pygame.font.Font('Tetris.ttf', 30)  # initialize the font
    label = font.render('TETRIS', 1, (255, 255, 255))  # initialize the label, antialiasing, white color label


    # draws the label on the screen, puts it in the middle of the screen
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))
    font = pygame.font.Font('Tetris.ttf', 20)
    label = font.render('Score: ' + str(score), 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    surface.blit(label, (sx + 20, sy + 160))

    label = font.render('High Score: ' + str(last_score), 1, (255, 255, 255))
    sx = top_left_x - 200
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):  # loops through every color in the grid
        for j in range(len(grid[i])):
            # surface is where it's drawn, grid[i][j] is the color, and the other parameter is position,
            # last is fill to fill in the box instead of a border
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 255, 255), (top_left_x, top_left_y, play_width, play_height), 5)
    draw_grid(surface, grid)

def pause(pause_key):
    pygame.mixer.music.pause()
    draw_text_middle(win, 'PAUSED', 25, (255, 255, 255))
    pygame.display.update()
    pause = True
    while pause:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pause_key:
                if music_enabled:
                    pygame.mixer.music.unpause()
                pause = False
                return
            if event.type == pygame.QUIT:
                pause = False
                pygame.display.quit()
                quit()

def main(win):
    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    play_music()
    pygame.mixer.music.set_volume(0.5)

    change_piece = False
    run = True  # for the while loop
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.50
    level_time = 0
    score = 0
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
    

        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    play_sfx("move.wav", channel=0)
                    current_piece.x -= 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    play_sfx("move.wav", channel=0)
                    current_piece.x += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    play_sfx("move.wav", channel=0)
                    current_piece.y += 2
                    if not (valid_space(current_piece, grid)):
                        current_piece.y -= 2
                if event.key == pygame.K_UP:
                    play_sfx("shift.wav", channel=0)
                    current_piece.rotation += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                if event.key == pygame.K_p:
                    pause(pygame.K_p)
                if event.key == pygame.K_m:
                    toggle_music()

                if event.key == pygame.K_n:
                    toggle_sfx()

                if event.key == pygame.K_PERIOD:   # > key
                    next_music_track()

                if event.key == pygame.K_COMMA:    # < key
                    prev_music_track()

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
            play_sfx("lock.wav", channel=0)

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        if show_music_off_text:
            draw_text_upper_right(win, 'MUSIC OFF', 25, (255, 0, 0))
        if show_sound_fx_off_text:
            draw_text_upper_right(win, 'SOUND FX OFF', 25, (255, 0, 0), padding = 50, adjust = 30)

        pygame.display.update()
        
        if check_lost(locked_positions):
            pygame.mixer.music.pause()
            play_sfx("game_over.wav", channel=2)
            draw_text_middle(win, "GAME OVER", 80, (255, 255, 255))
            pygame.display.update()

            # Show GAME OVER text for 1.5 seconds
            pygame.time.delay(150)

            # ---- Ignore all key inputs for 5 seconds ----
            ignore_end_time = pygame.time.get_ticks() + 500
            while pygame.time.get_ticks() < ignore_end_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return  # or sys.exit()
        # Optional: still allow drawing/updating screen
                pygame.display.update()

    # ---- After ignoring keys, continue ----
            run = False

            if update_score(score):
                high_score_menu(win)
            else:
                main_menu(win)

def high_score_menu(win):
    run = True
    count = 0

    # --- Ignore key inputs for the first 2 seconds ---
    ignore_until = pygame.time.get_ticks() + 2000  

    pygame.mixer.music.load("highscore.wav")
    pygame.mixer.music.play(0)

    while run:
        win.fill((0, 0, 0))
        count += 1

        if count % 2 == 0:
            sel_color = shape_colors[0]
        elif count % 3 == 0:
            sel_color = shape_colors[1]
        elif count % 4 == 0:
            sel_color = shape_colors[2]
        elif count % 5 == 0:
            sel_color = shape_colors[3]
        else:
            sel_color = shape_colors[6]

        display_title(win, "NEW HIGHSCORE", 70, sel_color)
        score = max_score()
        draw_text_middle(win, f'{score}', 70, (255, 255, 255))
        pygame.display.update()

        # --- Event loop ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # Ignore key presses during the first 2 seconds
                if pygame.time.get_ticks() < ignore_until:
                    continue

                pygame.mixer.music.stop()
                main_menu(win)


def main_menu(win):
    clock = pygame.time.Clock()
    if menu_music:
        pygame.mixer.music.load("beat.wav")
        pygame.mixer.music.play(-1)
    
    count = 0
    run = True
    while run:
        win.fill((0, 0, 0))
        count += 1
        if count % 2 == 0:
            sel_color = shape_colors[0]
        elif count % 3 == 0:
            sel_color = shape_colors[1]
        elif count % 4 == 0:
            sel_color = shape_colors[2]
        elif count % 5 == 0:
            sel_color = shape_colors[3]
        else:
            sel_color = shape_colors[6]
        display_title(win, "PYTHON TETRIS", 70, sel_color)
        draw_text_middle(win, 'Press any key to play', 30, (255, 255, 255))
        draw_right_controls(win, 'Press right to move block right', 20, (255, 255, 255))
        draw_left_controls(win, 'Press left to move block left', 20, (255, 255, 255))
        draw_up_controls(win, 'Press up to shift shape configuration', 20, (255, 255, 255))
        draw_down_controls(win, 'Press down to increase block speed', 20, (255, 255, 255))
        draw_space_controls(win, 'Press space to slam a block down', 20, (255, 255, 255))
        draw_pause_controls(win, 'Press p to pause', 20, (255, 255, 255))
        draw_music_controls(win, 'Press M to toggle music', 20, (255, 255, 255))
        draw_sound_controls(win, 'Press N to toggle sound FX', 20, (255, 255, 255))
        draw_switch_controls(win, 'Press < or > to switch music tracks', 20, (255, 255, 255))
        pygame.display.update()
        clock.tick(5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit() #Force quitting the game
            if event.type == pygame.KEYDOWN:
                pygame.mixer.music.stop()
                main(win)

win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
main_menu(win)  # start game
