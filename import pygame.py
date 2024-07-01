import pygame
import random
import time
import threading
import requests
import webbrowser

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600  # Set the screen dimensions

WHITE = (255, 255, 255)  # Define the color white
BLACK = (0, 0, 0)  # Define the color black
RED = (255, 0, 0)  # Define the color red
GREEN = (0, 255, 0)  # Define the color green
BLUE = (0, 0, 255)  # Define the color blue
DARK_BLUE = (0, 0, 139)
LIGHT_RED = (255, 102, 102)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
DARK_PURPLE = (75, 0, 130)
DARK_ORANGE = (255, 140, 0)
FONT_SIZE = 32  # Set the font size for the main text
INITIAL_MOVE_SPEED = 0.1  # Slower initial move speed  
SPEED_INCREMENT = 0.03  # Speed increment for each stage
WORDS_BUFFER_SIZE = 10  # Set the buffer size for pre-fetched words
last_speed_increase_time = time.time()

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Create the screen
pygame.display.set_caption("LETTER LEGEND")  # Set the window caption

game_background = pygame.image.load("bg.jpg")
game_background = pygame.transform.scale(game_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
menu_background = pygame.image.load("background2.jpg")
menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
level_background = pygame.image.load("bg1.jpg")
level_background = pygame.transform.scale(level_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
gameover = pygame.image.load("over.gif")
gameover = pygame.transform.scale(gameover, (SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.mixer.music.load("Music.mp3")
pygame.mixer.music.set_volume(0.1)
key_press_sound = pygame.mixer.Sound("key.mp3")
wrong_press_sound = pygame.mixer.Sound("wrong.mp3")
oversound = pygame.mixer.Sound("oversound.mp3")

def play_music():
    pygame.mixer.music.play(-1)  # Play music indefinitely (-1 loops)

# Function to pause music
def pause_music():
    pygame.mixer.music.pause()

# Function to unpause music
def unpause_music():
    pygame.mixer.music.unpause()

# Function to toggle mute state
def toggle_mute():
    if pygame.mixer.music.get_volume() == 0.0:
        pygame.mixer.music.set_volume(0.1)  # Set volume back to half
    else:
        pygame.mixer.music.set_volume(0.0)  # Mute music

# Fonts
font = pygame.font.SysFont('roboto', FONT_SIZE)  # Load the default system font
front_font = pygame.font.SysFont('consolas', 25)
mid_font = pygame.font.SysFont('comicsansms', 30)
big_font = pygame.font.SysFont('impact', 50)  # Load a larger font for game over text
level_up_font = pygame.font.SysFont('arialbold', 100)  # Load a larger font for level-up text

# Game variables
typed_text = ""  # Initialize the typed text
enemy_position = [random.randint(0, SCREEN_WIDTH - 200), 0]  # Randomly position the first word
level = 1  # Set the initial game level
score = 0  # Initialize the score
current_stage = 1  # Set the initial stage
MOVE_SPEED = INITIAL_MOVE_SPEED  # Set the initial move speed
timer_event = pygame.USEREVENT + 1  # Create a custom event for the timer

# Pre-fetch words
words = []  # Initialize the list of words
words_lock = threading.Lock()  # Create a lock for thread-safe access to the words list

def fetch_words():
    global words
    while True:
        response = requests.get("https://random-word-api.herokuapp.com/word?number=50")  # Fetch random words
        if response.status_code == 200:
            with words_lock:  # Acquire the lock
                words.extend(response.json())  # Add the fetched words to the list

def get_random_word():
    global words
    with words_lock:  # Acquire the lock
        if not words:
            return "start"  # Return "loading" if no words are available
        valid_words = [word for word in words if len(word) <= current_stage + 3]  # Filter words based on stage
        if valid_words:
            word = random.choice(valid_words)  # Choose a random word from the valid words
            words.remove(word)  # Remove the chosen word from the list
            return word
        else:
            return "loading"

# Start the word-fetching thread
threading.Thread(target=fetch_words, daemon=True).start()  # Start the fetch_words function in a new thread

current_name = get_random_word()  # Get the first random word

# Functions
def draw_text(text, font, color, surface, x, y):
    x_pos = x
    for idx, char in enumerate(text):
        letter_color = color
        if idx < len(typed_text) and char.lower() == typed_text[idx].lower():
            letter_color = BLACK  # Highlight color for correctly typed letters
        letter_surface = font.render(char, True, letter_color)
        surface.blit(letter_surface, (x_pos, y))
        x_pos += letter_surface.get_width()  # Move the position to the right for the next character


def update_stage():
    global current_stage, MOVE_SPEED, SPEED_INCREMENT, last_speed_increase_time
    stages = [(0, 1), (5, 2), (10, 3), (20, 4), (30, 5)]  # Define score thresholds and stages
    for threshold, stage in stages:
        if score >= threshold and current_stage < stage:
            current_stage = stage  # Update the current stage based on the score
            if stage == 5:
                MOVE_SPEED = INITIAL_MOVE_SPEED + (stage - 1) * SPEED_INCREMENT 
            else:
                MOVE_SPEED = INITIAL_MOVE_SPEED + (stage - 1) * SPEED_INCREMENT  # Increase the speed up to stage 5
            display_level_up_message(stage)  # Display the level-up message

    # Increase the speed every 10 seconds after reaching stage 5
    if current_stage >= 5:
        current_time = time.time()
        if current_time - last_speed_increase_time >= 8:  # Check if 10 seconds have passed
            MOVE_SPEED += SPEED_INCREMENT  # Increase the speed
            last_speed_increase_time = current_time  # Reset the timer

def display_level_up_message(stage):
    level_up_message = f"Level {stage} !"  # Create the level-up message
    screen.fill(WHITE)  # Fill the screen with white
    screen.blit(level_background, (0, 0))
    draw_text(level_up_message, level_up_font, CYAN, screen, SCREEN_WIDTH // 2.2 - 100, SCREEN_HEIGHT // 2.3)  # Draw the level-up message
    pygame.display.update()  # Update the screen
    time.sleep(3)  # Pause for  seconds

def shake_screen():
    shake_duration = 0.5  # Duration of the shake in seconds
    shake_intensity = 10  # Intensity of the shake
    start_time = time.time()
    
    while time.time() - start_time < shake_duration:
        shake_x = random.randint(-shake_intensity, shake_intensity)
        shake_y = random.randint(-shake_intensity, shake_intensity)
        
        screen.fill(WHITE)
        screen.blit(game_background, (shake_x, shake_y))
        
        draw_text(current_name, mid_font, LIGHT_RED, screen, enemy_position[0] + shake_x, enemy_position[1] + shake_y)
        draw_text(f'Typed Text: {typed_text}', font, BLACK, screen, 10 + shake_x, SCREEN_HEIGHT - 50 + shake_y)
        draw_text(f'Score: {score}', font, BLACK, screen, 10 + shake_x, 10 + shake_y)
        draw_text(f'Stage: {current_stage}', font, BLACK, screen, SCREEN_WIDTH - 150 + shake_x, 10 + shake_y)
        
        pygame.display.update()
        pygame.time.delay(50)


def display_instructions():
    instructions_running = True
    while instructions_running:
        screen.fill(WHITE)  # Clear the screen

        screen.blit(menu_background, (0, 0))


        sound_button_image = pygame.image.load("sound.png")
        sound_button_image = pygame.transform.scale(sound_button_image, (35, 35))
        sound_button_rect = sound_button_image.get_rect()
        sound_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        screen.blit(sound_button_image, sound_button_rect)
        
        # Display the mute button only if music is muted
        if pygame.mixer.music.get_volume() == 0.0:
            mute_button_image = pygame.image.load("mute.png")
            mute_button_image = pygame.transform.scale(mute_button_image, (35, 35))
            mute_button_rect = mute_button_image.get_rect()
            mute_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
            screen.blit(mute_button_image, mute_button_rect)
        elif pygame.mixer.music.get_volume() == 0.1:
            sound_button_image = pygame.image.load("sound.png")
            sound_button_image = pygame.transform.scale(sound_button_image, (35, 35))
            sound_button_rect = sound_button_image.get_rect()
            sound_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
            screen.blit(sound_button_image, sound_button_rect)

        # Display instructions
        title_text = "Instructions"
        title_surface = big_font.render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title_surface, title_rect)

        instruction_lines = [
            "Type the word shown on the screen.",
            "Score a point for each correct word typed.",
            "Avoid letting the words reach the bottom of the screen.",
            "Press ENTER to pause while ingame."
        ]
        y_pos = SCREEN_HEIGHT // 3 + 50
        for line in instruction_lines:
            line_surface = front_font.render(line, True, BLACK)
            line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            screen.blit(line_surface, line_rect)
            y_pos += FONT_SIZE + 0

        return_text = "Press ESC to Return"
        return_surface = font.render(return_text, True, BLACK)
        return_rect = return_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(return_surface, return_rect)

        pygame.display.update()  # Update the screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    instructions_running = False  # Return to main menu
                elif event.key == pygame.K_m:                     
                    toggle_mute()  # Toggle music mute state

# Inside main_menu() function
def main_menu():
    play_music()  # Start playing music
    global word_storage  # Access the word storage list

    menu_running = True
    while menu_running:
        screen.fill(WHITE)  # Clear the screen

        screen.blit(menu_background, (0, 0))

        sound_button_image = pygame.image.load("sound.png")
        sound_button_image = pygame.transform.scale(sound_button_image, (35, 35))
        sound_button_rect = sound_button_image.get_rect()
        sound_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        screen.blit(sound_button_image, sound_button_rect)
        
        # Display the mute button only if music is muted
        if pygame.mixer.music.get_volume() == 0.0:
            mute_button_image = pygame.image.load("mute.png")
            mute_button_image = pygame.transform.scale(mute_button_image, (35, 35))
            mute_button_rect = mute_button_image.get_rect()
            mute_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
            screen.blit(mute_button_image, mute_button_rect)
        elif pygame.mixer.music.get_volume() == 0.1:
            sound_button_image = pygame.image.load("sound.png")
            sound_button_image = pygame.transform.scale(sound_button_image, (35, 35))
            sound_button_rect = sound_button_image.get_rect()
            sound_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
            screen.blit(sound_button_image, sound_button_rect)


        # Display menu options
        title_text = "^LETTER LEGEND^"
        title_surface = big_font.render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title_surface, title_rect)

        menu_options = [
            ("Press SPACE to Start", SCREEN_HEIGHT // 2 - 50),
            ("Press I for Instructions", SCREEN_HEIGHT // 2),
            ("Press W for Word Storage", SCREEN_HEIGHT // 2 + 50),
            ("Press ESC to Quit", SCREEN_HEIGHT // 2 + 100),
        ]

        for text, y_pos in menu_options:
            text_surface = front_font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            screen.blit(text_surface, text_rect)

       
        pygame.display.update()  # Update the screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    menu_running = False  # Start the game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_i:
                    display_instructions()  # Display game instructions
                elif event.key == pygame.K_w:
                    display_word_storage()  # Display word storage
                elif event.key == pygame.K_m:
                    toggle_mute()  # Toggle music mute state


# Constants
GOOGLE_SEARCH_URL = "https://www.google.com/search?q="

def display_word_storage():
    global word_storage

    storage_running = True
    scroll_offset = 10  # Initial offset for scrolling


    while storage_running:
        screen.fill(WHITE)  # Clear the screen

        screen.blit(menu_background, (0, 0))

        sound_button_image = pygame.image.load("sound.png")
        sound_button_image = pygame.transform.scale(sound_button_image, (35, 35))
        sound_button_rect = sound_button_image.get_rect()
        sound_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        screen.blit(sound_button_image, sound_button_rect)
        
        # Display the mute button only if music is muted
        if pygame.mixer.music.get_volume() == 0.0:
            mute_button_image = pygame.image.load("mute.png")
            mute_button_image = pygame.transform.scale(mute_button_image, (35, 35))
            mute_button_rect = mute_button_image.get_rect()
            mute_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
            screen.blit(mute_button_image, mute_button_rect)
        elif pygame.mixer.music.get_volume() == 0.1:
            sound_button_image = pygame.image.load("sound.png")
            sound_button_image = pygame.transform.scale(sound_button_image, (35, 35))
            sound_button_rect = sound_button_image.get_rect()
            sound_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
            screen.blit(sound_button_image, sound_button_rect)

        # Display word storage title higher on the screen
        title_text = "Word Storage"
        title_width = big_font.size(title_text)[0]
        draw_text(title_text, big_font, BLACK, screen, (SCREEN_WIDTH - title_width) // 2, SCREEN_HEIGHT // 12)

        # Display word storage
        # Calculate the starting y-position just below the "Word Storage" title
        start_y_pos = SCREEN_HEIGHT // 12 + big_font.get_height() + 20

        # Calculate the ending y-position to ensure it does not pass "Press ESC to Return"
        end_y_pos = SCREEN_HEIGHT - 110 - font.get_height() - 20
        
        y_pos = SCREEN_HEIGHT // 6 + scroll_offset
        visible_words = word_storage[max(0, -scroll_offset // (FONT_SIZE + 10)):]  # Get the visible portion of word storage

        for index, word in enumerate(visible_words):
            if y_pos >= 100 and y_pos <= SCREEN_HEIGHT - 120:
                # Draw the word as a hyperlink
                text = f"{word}"
                text_width = font.size(text)[0]
                draw_text(text, font, BLUE, screen, (SCREEN_WIDTH - text_width) // 2, y_pos)
            y_pos += FONT_SIZE + 10

        footer_text = "Press ESC to Return"
        footer_width = font.size(footer_text)[0]
        draw_text(footer_text, font, BLACK, screen, (SCREEN_WIDTH - footer_width) // 2, SCREEN_HEIGHT - 110)

        pygame.display.update()  # Update the screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    storage_running = False  # Return to main menu
                elif event.key == pygame.K_UP:
                    if scroll_offset < 10:
                        scroll_offset += FONT_SIZE + 10  # Scroll up
                elif event.key == pygame.K_DOWN:
                    if len(word_storage) * (FONT_SIZE + 10) > SCREEN_HEIGHT - 100 and \
                            scroll_offset > -1 * ((len(word_storage) * (FONT_SIZE + 10)) - (SCREEN_HEIGHT - 100)):
                        scroll_offset -= FONT_SIZE + 10  # Scroll down
                elif event.key == pygame.K_m:                     
                    toggle_mute()  # Toggle music mute state
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button clicked
                    # Check if a word was clicked
                    clicked_y = event.pos[1]
                    clicked_index = (clicked_y - (SCREEN_HEIGHT // 6 + scroll_offset)) // (FONT_SIZE + 10)
                    if clicked_index >= 0 and clicked_index < len(visible_words):
                        word_to_search = visible_words[clicked_index]
                        search_query = f"{word_to_search} meaning"
                        search_url = GOOGLE_SEARCH_URL + search_query.replace(" ", "+")
                        webbrowser.open_new_tab(search_url)  # Open the web browser with the Google search URL

# Initialize an empty list to store generated words
word_storage = []


# Modify the main() function
def main():
    global current_name, typed_text, enemy_position, score, MOVE_SPEED, current_stage

    paused = False  # Initialize paused state

    while True:
        main_menu()  # Display the main menu

        # Reset game variables
        typed_text = ""
        enemy_position = [random.randint(0, SCREEN_WIDTH - 50), 0]
        score = 0
        current_stage = 1
        MOVE_SPEED = INITIAL_MOVE_SPEED

        # Game loop
        running = True
        while running:
            screen.fill(WHITE)  # Clear the screen

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        typed_text = ""  # Reset the typed text
                        running = False  # End the game
                    elif event.key == pygame.K_RETURN:
                        paused = not paused  # Toggle pause state
                    elif paused:  # Only handle additional events when paused
                        if event.key == pygame.K_m:
                            toggle_mute()
                    else:
                        if not paused:
                            typed_char = event.unicode
                            if typed_char.isalpha():
                                if typed_char.lower() == current_name[len(typed_text)].lower():
                                    typed_text += typed_char  # Add the typed character to the text
                                    key_press_sound.play()
                                    
                                else:
                                    # Incorrect letter typed, delete the last character
                                    wrong_press_sound.play()
                                    if typed_text:
                                        typed_text = typed_text
                                        enemy_position[1] += 20

                    if typed_text.lower() == current_name.lower() and not paused:
                        word_storage.append(current_name)  # Store the word
                        current_name = get_random_word()  # Get a new random word
                        typed_text = ""  # Reset the typed text
                        enemy_position = [random.randint(0, SCREEN_WIDTH - 100), 0]  # Reset the word position
                        score += 1  # Increase the score
                        update_stage()  # Update the stage based on the score
                        if score >= 40 :
                            shake_screen()  # Trigger the shake effect

            if not paused:
                # Move the enemy down the screen
                enemy_position[1] += MOVE_SPEED

                #gamepage
                screen.blit(game_background, (0, 0))

                # Draw the current name and typed text
                draw_text(current_name, mid_font, LIGHT_RED, screen, enemy_position[0], enemy_position[1])
                draw_text(f'Typed Text: {typed_text}', font, BLACK, screen, 10, SCREEN_HEIGHT - 50)
                draw_text(f'Score: {score}', font, BLACK, screen, 10, 10)
                draw_text(f'Stage: {current_stage}', font, BLACK, screen, SCREEN_WIDTH - 150, 10)

                # Check for collision
                if enemy_position[1] + FONT_SIZE > SCREEN_HEIGHT - 50:
                    # Display the GIF instead of text
                    pygame.mixer.music.set_volume(0.0)  # Mute music
                    screen.blit(gameover, (0, 0))
                    oversound.play()
                    pygame.display.update()
                    time.sleep(2)
                    pygame.mixer.music.set_volume(0.1)
                    running = False  # End the game
                    typed_text = ""  # Reset typed text upon game over

            else:
                # Display pause message
                screen.blit(menu_background, (0, 0))
                draw_text("Paused", big_font, BLACK, screen, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50)
                
                sound_button_image = pygame.image.load("sound.png")
                sound_button_image = pygame.transform.scale(sound_button_image, (35, 35))
                sound_button_rect = sound_button_image.get_rect()
                sound_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
                screen.blit(sound_button_image, sound_button_rect)

                if pygame.mixer.music.get_volume() == 0.0:
                    mute_button_image = pygame.image.load("mute.png")
                    mute_button_image = pygame.transform.scale(mute_button_image, (35, 35))
                    mute_button_rect = mute_button_image.get_rect()
                    mute_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
                    screen.blit(mute_button_image, mute_button_rect)
                elif pygame.mixer.music.get_volume() == 0.1:
                    sound_button_image = pygame.image.load("sound.png")
                    sound_button_image = pygame.transform.scale(sound_button_image, (35, 35))
                    sound_button_rect = sound_button_image.get_rect()
                    sound_button_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
                    screen.blit(sound_button_image, sound_button_rect)
                

            pygame.display.update()  # Update the screen

    pygame.quit()  # Quit Pygame





if __name__ == "__main__":
    main()  # Run the main function
