""" Flappy Bird Clone by Chris Gingerich """
# Import standard modules.
import sys
import random
import time

# Import non-standard modules.
import pygame as pg
from pygame.locals import *

# Import local modules
import NeuralNetworkLib as NN
from settings import *
from sprites import Bird, TopPipe, BottomPipe

class App():
    # initialize app window, etc
    def __init__(self):
        # Initialise PyGame.
        pg.init()

        # Initalize some font action
        pg.font.init()
        self.font_name = pg.font.match_font(FONT)

        # Set up the clock. This will tick every frame and thus maintain a relatively constant framerate. Hopefully.
        self.fps = FPS
        self.fpsClock = pg.time.Clock()

        # Set up the window.
        self.width, self.height = WIDTH, HEIGHT
        self.screen = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption(TITLE)
        self.floor = pg.image.load("floor.png")
        self.floor_rect = self.floor.get_rect()
        self.floor_rect.bottom = HEIGHT + 60

        # screen is the surface representing the window.
        # PyGame surfaces can be thought of as screen sections that you can draw onto.
        # You can also draw surfaces onto other surfaces, rotate surfaces, and transform surfaces.

        # Game type 0 is singleplayer
        self.gametype = 0
        self.running = True

    # Contains event loop which waits for a mouse click or space press
    # changes gametype variable to 1 or 0
    def show_start_screen(self):
        running = True
        while running:

            # Event handling for intro screen
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.gametype = 0
                        running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.gametype = 1
                    running = False

            # Displaying text on the intro screen
            largeText = pg.font.Font(pg.font.match_font("arial"), 50)
            text_surf, text_rect = self.text_objects(TITLE, largeText)
            text_rect.center = ((WIDTH / 2),(HEIGHT / 4))
            self.screen.blit(text_surf, text_rect)

            smaller_text = pg.font.Font(pg.font.match_font("arial"), 20)
            text_surf_2, text_rect_2 = self.text_objects("Press Space to start single player!", smaller_text)
            text_rect_2.center = ((WIDTH / 2),(3 * HEIGHT / 4))
            self.screen.blit(text_surf_2, text_rect_2)

            smaller_text = pg.font.Font(pg.font.match_font("arial"), 20)
            text_surf_2, text_rect_2 = self.text_objects("Click the screen to train!", smaller_text)
            text_rect_2.center = ((WIDTH / 2),(3.5 * HEIGHT / 4))
            self.screen.blit(text_surf_2, text_rect_2)

            pg.display.update()

            self.screen.fill(WHITE)
    
    # Preps the App for a solo game
    def setup_solo(self):
        self.playing = True
        self.dt = 1 / self.fps
        self.frame_count = 0

        self.player = Bird()
        self.player_group = pg.sprite.Group()
        self.player_group.add(self.player)

        # Set up pipe sprite group
        self.pipes_group = pg.sprite.Group()
        # Create 2 lists of pipes currently in action for future reference
        self.top_pipe_list = list()
        self.bottom_pipe_list = list()
        self.first_pipe_spawned = False

        self.speed_increase = 0
        #For first pipe timer
        self.start_ticks = pg.time.get_ticks()
        #pg.event.post(pg.event.Event(USEREVENT+4))
        pg.time.set_timer(USEREVENT+4, PIPE_TIMER)

    # Contains gameloop (for solo mode)
    def run_solo(self):
        self.setup_solo()
        while self.playing:
            self.events()
            self.update(self.dt)
            self.draw()
            self.dt = self.fpsClock.tick(self.fps)
            self.frame_count += 1

    # Pygame events are checked here (for solo mode)
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.flap()
            if event.type == USEREVENT+4:
                self.generate_pipe_pair()
            
            # USEREVENT+2 is a scored point event
            if event.type == USEREVENT+2:
                self.player.single_score += 1

            # USEREVENT+3 is a call to remove the first element of both pipe lists
            if event.type == USEREVENT+3:
                del self.bottom_pipe_list[0]
                del self.top_pipe_list[0]
                #self.generate_pipe_pair(self.speed_increase)
                #self.speed_increase += SPEED_INCREASE_RATE

    # Game logic is tested here and all sprites have their own update functions called (for solo mode)
    def update(self, dt):
        # Test for collision between player and pipes or player and the ground
        if self.player.collide(self.pipes_group) or self.player.rect.bottom == HEIGHT:
            self.playing = False

        self.pipes_group.update(dt)
        self.player.update(dt)
        # Show which pipe is focused on

        self.seconds = (pg.time.get_ticks()-self.start_ticks)/1000 #calculate how many seconds

    # Draws to the screen (for solo mode)
    def draw(self):
        self.screen.fill((0,204,255))  # Fill the screen with a color

        ##### Redraw screen here. #####
        # The pipes
        self.pipes_group.draw(self.screen)

        # Then draw ground 
        #pg.draw.rect(self.screen, BLACK, (0, HEIGHT - BOTTOM_KILL_THRESHOLD - 20, WIDTH, BOTTOM_KILL_THRESHOLD + 20))
        self.screen.blit(self.floor, self.floor_rect)
        
        # Then the player groups
        self.player_group.draw(self.screen)

        # Then finally the score
        self.draw_text(self.screen, ("Score: " + str(self.player.single_score)), 30, 0, 0)

        # Flip the display so that the things we drew actually show up.
        pg.display.flip()

    # Similar to show_start_screen(), waits for spacebar
    def show_game_over_screen(self):
        running = True

        while running:
            
            # Event handling for intro screen
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.player.y_velocity = 0
                        self.player.rect.center = (WIDTH / 2, HEIGHT / 2)
                        running = False
                        
            largeText = pg.font.Font(pg.font.match_font("arial"), 40)
            text_surf, text_rect = self.text_objects("Press Space to try again", largeText)
            text_rect.center = ((WIDTH / 2),(3 * HEIGHT / 4))
            self.screen.blit(text_surf, text_rect)

            pg.display.update()

    # Preps the App for an AI experience
    # Generates first generation of birds and preps game stuff
    def setup_training(self, Num_birds):
        self.training = True
        self.playing = True
        self.dt = 1 / self.fps
        self.frame_count = 0

        self.players = [Bird() for i in range(Num_birds)]
        self.saved_players = []
        self.players_group = pg.sprite.Group()
        self.players_group.add(self.players)

        self.generation = 1
        self.record = 0

        # Set up pipe sprite group
        self.pipes_group = pg.sprite.Group()
        # Create 2 lists of pipes currently in action for future reference
        self.top_pipe_list = list()
        self.bottom_pipe_list = list()
        self.first_pipe_spawned = False

        self.speed_increase = 0
        self.game_score = 0
        #For first pipe timer
        self.start_ticks = pg.time.get_ticks()
        #pg.event.post(pg.event.Event(USEREVENT+4))
        pg.time.set_timer(USEREVENT+4, PIPE_TIMER)

    # Main training game loop
    def run_training(self):
        self.training = True
        while self.training:
            for player in self.players:
                player.think(self.top_pipe_list, self.bottom_pipe_list)
            self.t_events()
            self.t_update(self.dt)
            self.t_draw()
            self.dt = self.fpsClock.tick(self.fps)
            self.frame_count += 1

    # Called once all the birds are dead, resets the game stuff
    def reset_training(self):
        self.playing = True
        self.dt = 1 / self.fps
        self.frame_count = 0

        # Set up pipe sprite group
        self.pipes_group.empty()
        # Create 2 lists of pipes currently in action for future reference
        self.top_pipe_list = list()
        self.bottom_pipe_list = list()
        self.first_pipe_spawned = False

        self.speed_increase = 0
        #For first pipe timer
        self.start_ticks = pg.time.get_ticks()
        #pg.time.set_timer(USEREVENT+4, 0)
        pg.time.set_timer(USEREVENT+4, PIPE_TIMER)

    # Pygame events for training
    def t_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                    self.training = False
                self.running = False
                break
            if event.type == USEREVENT+4:
                self.generate_pipe_pair()
            
            # USEREVENT+2 is a scored point event
            if event.type == USEREVENT+2:
                for player in self.players_group:
                    player.score += 1
                self.game_score += 1

            # USEREVENT+3 is a call to remove the first element of both pipe lists
            if event.type == USEREVENT+3:
                if self.bottom_pipe_list.__len__() != 0:
                    del self.bottom_pipe_list[0]
                if self.top_pipe_list.__len__() != 0:
                    del self.top_pipe_list[0]
                #self.generate_pipe_pair(self.speed_increase)
                #self.speed_increase += SPEED_INCREASE_RATE

    # Everyones update functions get called, game logic occurs
    # Calls next_generation() if all the birds die
    def t_update(self, dt):
        # Test for collision between player and pipes or player and the ground/roof
        for player in self.players_group:
            if player.collide(self.pipes_group) or player.rect.bottom == HEIGHT or player.rect.bottom < -40:
                player.alive = False

        self.pipes_group.update(dt)

        # Important
        if self.players.__len__() == 0:
            self.next_generation()
            self.training = False

        if self.record < self.game_score:
            self.record = self.game_score

        for player in self.players_group:
            player.update(dt)
            if not player.alive:
                self.saved_players.append(player)
                self.players.remove(player)
                player.kill()
        # Show which pipe is focused on
        self.seconds = (pg.time.get_ticks()-self.start_ticks)/1000 #calculate how many seconds

    # Draw the training mode to the screen
    def t_draw(self):
        self.screen.fill((0,204,255))  # Fill the screen with a color

        ##### Redraw screen here. #####
        # Then the pipes
        self.pipes_group.draw(self.screen)

        # Draw ground first
        self.screen.blit(self.floor, self.floor_rect)

        # Then the player groups
        self.players_group.draw(self.screen)

        # Then finally the generation number
        self.draw_text(self.screen, ("Generation: " + str(self.generation)), 30, 0, 0)
        self.draw_text(self.screen, ("Current # Pipes Cleared: " + str(self.game_score)), 30, 0, 35)
        self.draw_text(self.screen, ("Current Record: " + str(self.record)), 30, 0, 70)
        self.draw_text(self.screen, ("Current # Birds Alive: " + str(self.players.__len__())), 30, 0, 105)

        # Flip the display so that the things we drew actually show up.
        pg.display.flip()

    # Calculates the fitness of the birds, then calls pick_one_bird() n times until a new popluation has been created
    def next_generation(self):
        self.generation += 1
        self.game_score = 0
        self.calculate_fitness()
        for i in range(NUM_OF_BIRDS):
            new_bird = self.pick_one_bird()
            self.players.append(new_bird)
            self.players_group.add(new_bird)
        
        self.saved_players = []

    # Assigns each player a fitness score based on how well each proformed relative to eachother
    def calculate_fitness(self):
        total = 0
        for player in self.saved_players:
            total += player.score
        for player in self.saved_players:
            player.fitness = player.score / total

    # Algorithm to pick one bird out of a pool of birds with un equal probabilities of being picked
    # The higher the birds fitness score, the more likely this function will create a mutated copy
    # oh yeah, after it selects the bird, it mutates that bird before returing it alowing us to explore the landscape of posibilities
    # :')
    def pick_one_bird(self):
        index = 0
        r = random.random()
        while (r > 0):
            r = r - self.saved_players[index].fitness
            index += 1
        index -= 1

        bird = self.saved_players[index]
        child = Bird(bird.brain)
        child.brain.mutate(MUTATION_RATE)
        return child

    # Creates a text object
    def text_objects(self, text, font):
        textSurface = font.render(text, True, BLACK)
        return textSurface, textSurface.get_rect()

    # A function used to draw text on the screen
    def draw_text(self, surf, text, size, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, BLACK)
        text_rect = text_surface.get_rect()
        text_rect.x, text_rect.y = (x, y)
        surf.blit(text_surface, text_rect)

    # Creates 2 pipes that move to the left
    def generate_pipe_pair(self, speed_increase = 0):
        top_pipe_y = random.randrange(50, HEIGHT - BOTTOM_KILL_THRESHOLD - PIPE_GAP_SIZE - 50)
        #top_pipe_y = 200
        bottom_pipe_y = top_pipe_y + PIPE_GAP_SIZE

        top_pipe = TopPipe(top_pipe_y)
        top_pipe.x_velcoity += speed_increase
        self.top_pipe_list.append(top_pipe)
        self.pipes_group.add(top_pipe)

        bottom_pipe = BottomPipe(bottom_pipe_y)
        bottom_pipe.x_velcoity += speed_increase
        self.bottom_pipe_list.append(bottom_pipe)
        self.pipes_group.add(bottom_pipe)

# Program starts here
if __name__ == "__main__":
    a = App()
    while a.running: 

        a.show_start_screen()

        if a.gametype == 0:
            a.run_solo()
            a.show_game_over_screen()

        elif a.gametype == 1:
            a.setup_training(NUM_OF_BIRDS)
            while a.running:
                a.run_training()
                a.reset_training()
    
    pg.quit()