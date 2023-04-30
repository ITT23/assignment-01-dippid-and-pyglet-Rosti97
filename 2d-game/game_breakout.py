import pyglet
from pyglet import shapes, clock
from DIPPID import SensorUDP
import numpy as np
import sys

WINDOW_WIDTH = 795
WINDOW_HEIGHT = 500
PORT = 5700
sensor = SensorUDP(PORT)

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

class Brick:
    bricks = []

    def __init__(self, x, y, width, height, color, lives):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.shape = shapes.Rectangle(x=self.x,
                                      y=self.y,
                                      width=self.width,
                                      height=self.height,
                                      color=self.color)
        self.lives = lives


    def create_bricks():
        # TODO in konstruktor rein
        start_x = 10 # x von border + width border + margin
        start_y = 470 # window height - y von top border

        brick_width = 50
        brick_height =  20
        brick_margin = 5
        color = [
        (0,0,255), (0,0,255), (0,255,0), (0,255,0),(255,0,0), (255,0,0)
    ]
        # all bricks should have same width + margin
        # for (int i) = row
        #   for int j = column
        #       new Brick (i * x, j * y, color[i])

        for i in range(6):
            for j in range(14):
                x_calc = start_x + brick_margin + j * brick_margin + j * brick_width
                y_calc = start_y - brick_margin - i * brick_margin - i * brick_height
                Brick.bricks.append(Brick(x = x_calc, y = y_calc, width=brick_width, height=brick_height, 
                                          color=color[i], lives=2))
    
    def draw_bricks():
        for brick in Brick.bricks:
            brick.draw()
            #print("draw_bricks")


    def draw(self):
        self.shape.draw()

class Ball:

    ball = {}

    def __init__(self, x, y, dx, dy, speed, width, height):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.width = width
        self.height = height
        self.speed = speed
        self.shape = shapes.Rectangle(x=self.x,
                                      y=self.y,
                                      width=self.width,
                                      height=self.height,
                                      color=(0,255,0))
        
    def create_ball():
        Ball.ball = Ball(x=WINDOW_WIDTH/2, y=180, dx=1, dy=2, speed=3,width=20, height=20)
        
    def draw_ball():
        Ball.ball.shape.draw()

    def update_ball():
        Ball.ball.shape.x += Ball.ball.dx * Ball.ball.speed
        Ball.ball.shape.y += Ball.ball.dy * Ball.ball.speed


    def change_ball_direction(self, is_horizontal_change):
        if is_horizontal_change:
            Ball.ball.dx = -Ball.ball.dx
        else:
            Ball.ball.dy = -Ball.ball.dy

    def check_brick_collision():
        for brick in Brick.bricks:
            if (Ball.ball.shape.x >= brick.x and Ball.ball.shape.x <= brick.x + brick.width and 
                Ball.ball.shape.y + Ball.ball.height >= brick.y):
                # change_loc_test()
                Brick.bricks.remove(brick)
                Ball.ball.change_ball_direction(False)
                break

    def check_border_collision():
        for border in Game_Border.game_borders:
            if border.location == "left" and Ball.ball.shape.x - border.width <= 0:
                # border left collision
                Ball.ball.change_ball_direction(True)
                break
            elif border.location == "right" and Ball.ball.shape.x + Ball.ball.width >= WINDOW_WIDTH - border.width:
                #border right collision
                Ball.ball.change_ball_direction(True)
                break
            elif border.location == "top" and Ball.ball.shape.y + Ball.ball.height >= border.y:
                # border top collision
                Ball.ball.change_ball_direction(False)
                break
            elif border.location == "down" and Ball.ball.shape.y <= border.y + border.height:
                # border down coll
                Ball.ball.change_ball_direction(False)
                break

    def check_player_collision():
        if (Ball.ball.shape.x >= Player.player.shape.x and 
            Ball.ball.shape.x + Ball.ball.width <= Player.player.shape.x + Player.player.width and 
            Ball.ball.shape.y <= Player.player.shape.y + Player.player.height):
            Ball.ball.change_ball_direction(False)
            
class Player:

    player= {}

    def __init__(self, x, y, dx, width, height):
        self.x = x
        self.y = y
        self.dx = dx
        self.width = width
        self.height = height
        self.shape = shapes.Rectangle(x=self.x,
                                      y=self.y,
                                      width=self.width,
                                      height=self.height,
                                      color=(0, 0, 255))
        
    def create_player():
        Player.player = Player(x=WINDOW_WIDTH/2, y=50, width=100, height=10, dx = 0)

    def draw_player():
        Player.player.shape.draw()

    def get_DIPPID_data():
        # check if the sensor has the 'gravity' capability
        if(sensor.has_capability('gravity')):
            # get gravity data for y-axis
            gravity_y_data = float(sensor.get_value('gravity')['y'])
            # little threshold for letting player standing still
            if gravity_y_data > 0 and Player.player.shape.x + Player.player.width >= WINDOW_WIDTH - Game_Border.border_width:
                return
            if gravity_y_data < 0 and Player.player.shape.x <= Game_Border.border_width:
                return
            Player.player.shape.x += gravity_y_data * 2

        
class Game_Border:

    game_borders = []
    border_width = 10

    def __init__(self, x, y, width, height, location, is_side_border):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.shape = shapes.Rectangle(x=self.x,
                                      y=self.y,
                                      width=self.width,
                                      height=self.height,
                                      color=(255,255,255))
        self.location = location
        self.is_side_border = is_side_border
        

    def create_borders():
        border_width = 10
        Game_Border.game_borders.append(Game_Border(x = 0, y = 0, width = border_width, height=WINDOW_HEIGHT, location="left", is_side_border=True))
        Game_Border.game_borders.append(Game_Border(x=WINDOW_WIDTH-border_width, y=0, width= border_width, height=WINDOW_HEIGHT, location="right", is_side_border=True))
        Game_Border.game_borders.append(Game_Border(x=0,y=WINDOW_HEIGHT-border_width, width=WINDOW_WIDTH, height=border_width, location="top", is_side_border=False))
        Game_Border.game_borders.append(Game_Border(x=0,y=0, width= WINDOW_WIDTH, height=border_width, location="down", is_side_border=False))

    def draw_borders():
        for border in Game_Border.game_borders:
            border.draw()


    def draw(self):
        self.shape.draw()

def draw_game_elements():
    Brick.draw_bricks()
    Game_Border.draw_borders()
    Player.draw_player()
    Ball.draw_ball()

def create_game():
    Game_Border.create_borders()
    Brick.create_bricks()
    Player.create_player()
    Ball.create_ball()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        create_game()

@window.event 
def on_show():
    create_game()

@window.event
def on_draw():
    window.clear()
    Ball.update_ball()
    Ball.check_border_collision()
    Ball.check_brick_collision()
    Ball.check_player_collision()
    Player.get_DIPPID_data()
    draw_game_elements()
    
pyglet.app.run()