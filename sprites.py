# Import non-standard modules.
import pygame as pg
from pygame.locals import *

# Import local modules
from settings import *
from NeuralNetworkLib import NeuralNetwork

class Bird(pg.sprite.Sprite):
    def __init__(self, brain = None):
        pg.sprite.Sprite.__init__(self)
        # 50px by 50px
        self.image = pg.image.load("bird.png") #pg.Surface((PLAYER_WIDTH, PLAYER_WIDTH))
        self.image.set_colorkey(WHITE) 
        #self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.inflate(-30, -20)
        self.rect.center = (WIDTH / 3, 3 * HEIGHT / 5)
        self.y_velocity = STARTING_Y_VELOCITY
        self.single_score = 0
        self.score = 0
        self.fitness = 0
        self.alive = True

        # Keep track of if the player has done the first tap of the game
        self.first_tap = True

        if brain:
            self.brain = brain.copy();
        else:
            self.brain = NeuralNetwork(4, HIDDEN_NODES, 1)
    
    def update(self, dt):
        self.score += 1
        
        if self.first_tap == True:
            self.rect.y += self.y_velocity * dt
            self.y_velocity += GRAVITY

        # If player goes below 50 from the bottom
        if self.rect.bottom > HEIGHT - BOTTOM_KILL_THRESHOLD:
            self.rect.bottom = HEIGHT

    def flap(self):
        self.y_velocity = FLAP_VELOCITY
        self.first_tap = True

    def collide(self, spriteGroup):
        return pg.sprite.spritecollide(self, spriteGroup, False)
    
    # Genetic Algo Inputs and brain #

    # Returns distance to next pipe pair as a float
    def distance_to_next_pipe(self, pipe_list):
        if len(pipe_list) == 0:
            return WIDTH/3 - PLAYER_WIDTH/2
        for pipe in pipe_list:
            if pipe.focus and pipe.rect.right < self.rect.left:
                return (pipe.rect.right - self.rect.left)
        return 253
        
    # Returns verticle distance from bird to the bottom of the top pipe
    def distance_to_next_top(self, pipe_list):
        if len(pipe_list) == 0:
            return 1
        for pipe in pipe_list:
            if pipe.focus and pipe.rect.right < self.rect.left:
                return pipe.rect.bottom - self.rect.top
        return 0

    # Returns verticle distance from bird to the top of the bottom pipe
    def distance_to_next_bottom(self, pipe_list):
        if len(pipe_list) == 0:
            return 0
        for pipe in pipe_list:
            if pipe.focus and pipe.rect.right > self.rect.left:
                return pipe.rect.top - self.rect.bottom
        return 0

    # Returns this birds current y vel
    def current_y_vel(self):
        return self.y_velocity

    # Decides if the bird should flap during a given frame by feeding the inputs through its brain
    def think(self, top, bot):
        in_1 = self.distance_to_next_pipe(top) / 253
        in_2 = self.distance_to_next_top(top) / 480
        in_3 = self.distance_to_next_bottom(bot) / 480
        in_4 = self.current_y_vel()
        output = self.brain.feedforward([in_1, in_2, in_3, in_4])
        if output[0] > .5:
            self.flap()
   
class TopPipe(pg.sprite.Sprite):
    def __init__(self, bottom_height):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("top_pipe.png") 
        self.image.set_colorkey(WHITE) 
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom_height
        self.rect.left = WIDTH
        self.x_velcoity = INITIAL_PIPE_SPEED
        self.focus = True
        self.pipe_score_sent = False

    def update(self, dt):
        self.rect.right += self.x_velcoity * dt

        if self.rect.right < 0:
            self.kill()
        if self.rect.right < ((WIDTH / 3) - 20) and self.pipe_score_sent == False:
            self.focus = False
            self.pipe_score_sent = True

class BottomPipe(pg.sprite.Sprite):
    def __init__(self, top_height):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("bot_pipe.png")
        self.image.set_colorkey(WHITE) 
        self.rect = self.image.get_rect()
        self.rect.top = top_height
        self.rect.left = WIDTH
        self.x_velcoity = INITIAL_PIPE_SPEED
        self.pipe_score_sent = False
        self.focus = True

    def update(self, dt):
        self.rect.right += self.x_velcoity * dt
        if self.rect.right < 0:
            # Remove self from sprite group
            self.kill()
            # Send delete pipe pair event
            ee = pg.event.Event(USEREVENT+3)
            pg.event.post(ee)
        
        if self.rect.right < ((WIDTH / 3) - 20) and self.pipe_score_sent == False:
            # Add 1 to score event
            ee = pg.event.Event(USEREVENT+2)
            pg.event.post(ee)
            self.focus = False
            self.pipe_score_sent = True
