import pyglet
from pyglet import shapes, clock
from DIPPID import SensorUDP
from time import sleep

WINDOW_WIDTH = 795
WINDOW_HEIGHT = 500
PORT = 5700
sensor = SensorUDP(PORT)

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

game_paused = True
game_won = False
dead = False

# Holds the info-texts for Gameplay
class Menu:
    menu = {}

    def __init__(self):
        self.background = shapes.Rectangle(x=0, y=0,
                                      width=WINDOW_WIDTH,
                                      height=WINDOW_HEIGHT,
                                      color=(150,150,150))
        self.text = pyglet.text.Label('info', font_name='Times New Roman',
                          font_size=20,
                          x=15, y=WINDOW_HEIGHT/2)
        self.info = 'start' # string tells which text will be displayed
        
    def create_Menu():
        Menu.menu = Menu()

    def draw_background():
        Menu.menu.background.opacity = 128 # half transparent background
        Menu.menu.background.draw()

    # menu / text shown before game starts
    def draw_start_menu():
        Menu.draw_background()
        Menu.menu.text.text = "Hold your phone sideways (to the left) and press 'button_1' to start."
        Menu.menu.text.draw()

    # menu / text shown after all bricks got cleared
    def draw_win_menu():
        Menu.draw_background()
        Menu.menu.text.text = "Congrats! You won! Press 'button_1' to play again."
        Menu.menu.text.draw()
        Menu.menu.info = 'win'

    # menu / text shown after ball touched the bottom border
    def draw_lose_menu():
        Menu.draw_background()
        Menu.menu.text.text = "Ups, you died... Press 'button_1' to restart."
        Menu.menu.text.draw()
        Menu.menu.info ='lose'

# holds the bricks
class Brick:
    bricks = []

    def __init__(self, x, y, width, height, color):
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


    def create_bricks():
        start_x = 10        # end of left border
        start_y = 470       # window height - height of top border
        brick_width = 50 
        brick_height =  20
        brick_margin = 5    # distance between individual bricks
        rows = 4            # determines how many rows of bricks
        items_per_row = 14  # determines how many bricks per row
        color = [           # set of color for individual row, meant for 4 rows
        (0,112,164), (0,139,185), (55,181,204), (74,193,216) ]
        # if more rows are being added, remember to add the color for more rows
        # colors from color palette: https://www.pinterest.de/pin/70437486736398/

        # creates the rows
        for i in range(rows):
            for j in range(items_per_row):
                # includes borders to get even margins
                x_calc = start_x + brick_margin + j * brick_margin + j * brick_width
                y_calc = start_y - brick_margin - i * brick_margin - i * brick_height
                Brick.bricks.append(Brick(x = x_calc, y = y_calc, width=brick_width, height=brick_height, 
                                          color=color[i])) # color per row is different
    
    # clears the list for a new game
    def restart_bricks():
        Brick.bricks.clear()
        Brick.create_bricks()

    def draw_bricks():
        if Brick.bricks:
            for brick in Brick.bricks:
                brick.draw()

    def draw(self):
        self.shape.draw()

# holds the game-ball
class Ball:

    ball = {}

    def __init__(self, x, y, dx, dy, speed, width, height):
        self.x = x
        self.y = y
        self.dx = dx            # for change of coordinates
        self.dy = dy            # for change of coordinates
        self.width = width
        self.height = height
        self.speed = speed      # determines how fast game-ball will change
        self.shape = shapes.Rectangle(x=self.x,
                                      y=self.y,
                                      width=self.width,
                                      height=self.height,
                                      color=(255,50,50))
        
    def create_ball():
        Ball.ball = Ball(x=WINDOW_WIDTH/2, y=35, dx=1, dy=2, speed=3, width=10, height=10)
        
    def draw_ball():
        Ball.ball.shape.draw()

    # every frame coordinates change with direction
    def update_ball():
        Ball.ball.shape.x += Ball.ball.dx * Ball.ball.speed
        Ball.ball.shape.y += Ball.ball.dy * Ball.ball.speed

    # sets direction and position back to start
    def restart_ball():
        Ball.ball.dx = 1
        Ball.ball.dy = 2
        Ball.ball.shape.x = Ball.ball.x
        Ball.ball.shape.y = Ball.ball.y

    # changes the direction where ball is going (up or down and left or right)
    def change_ball_direction(self, is_horizontal_change):
        if is_horizontal_change:
            Ball.ball.dx = -Ball.ball.dx
        else:
            Ball.ball.dy = -Ball.ball.dy

    # checks if game-ball hits any brick and removes this brick from game
    def check_brick_collision():
        global game_paused, game_won
        for brick in Brick.bricks:
            if (Ball.ball.shape.x >= brick.x and Ball.ball.shape.x <= brick.x + brick.width and 
                Ball.ball.shape.y + Ball.ball.height >= brick.y):
                Brick.bricks.remove(brick)
                if not Brick.bricks:        # if no bricks are left, game is over (positively)
                    game_won = True
                    game_paused = True
                    restart()
                    return
                Ball.ball.change_ball_direction(False)  # False = vertical change
                break

    # checks if game-ball hits any borders and changes direction accordingly
    def check_border_collision():
        global game_paused, dead
        for border in Game_Border.game_borders:
            if border.location == "left" and Ball.ball.shape.x - border.width <= 0:
                # left border collision -> changes horizontal direction
                Ball.ball.change_ball_direction(True)
                break
            elif border.location == "right" and Ball.ball.shape.x + Ball.ball.width >= WINDOW_WIDTH - border.width:
                # right border collision -> changes horizontal direction
                Ball.ball.change_ball_direction(True)
                break
            elif border.location == "top" and Ball.ball.shape.y + Ball.ball.height >= border.y:
                # top border collision -> changes vertical direction
                Ball.ball.change_ball_direction(False)
                break
            elif border.location == "down" and Ball.ball.shape.y <= border.y + border.height:
                # bottom border collision -> game over (negatively) -> restart
                Menu.menu.info = 'lose'
                game_paused = True
                dead = True
                restart()
                break

    # checks if game-ball is hit with player-object and changes vertical direction
    def check_player_collision():
        if (Ball.ball.shape.x >= Player.player.shape.x and 
            Ball.ball.shape.x + Ball.ball.width <= Player.player.shape.x + Player.player.width and 
            Ball.ball.shape.y <= Player.player.shape.y + Player.player.height):
            Ball.ball.change_ball_direction(False)

# holds player object         
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
                                      color=(255,150,0))
        
    def create_player():
        Player.player = Player(x=WINDOW_WIDTH/2, y=20, width=100, height=10, dx = 0)

    def draw_player():
        Player.player.shape.draw()

    def restart_player():
        Player.player.shape.x = Player.player.x        

    def get_DIPPID_data():
        # check if the sensor has the 'gravity' capability
        if(sensor.has_capability('gravity')):
            # get gravity data for y-axis
            gravity_y_data = float(sensor.get_value('gravity')['y'])
            # little threshold for letting player standing still
            # if player is already on one side border the input will not change the player
            if gravity_y_data > 0 and Player.player.shape.x + Player.player.width >= WINDOW_WIDTH - Game_Border.border_width:
                return
            if gravity_y_data < 0 and Player.player.shape.x <= Game_Border.border_width:
                return
            Player.player.shape.x += gravity_y_data * 2     # data multiplied for faster interaction

# holds all borders      
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
        
    # creates borders in window on left, right, top and bottom
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

# resets global variables for fresh start of game
def reset_variables():
    global game_paused, dead, game_won
    game_paused = True
    dead = False
    game_won = False
    Menu.menu.info = 'start'

# handles DIPPID button_1 presses and changes global variables accordingly
def handle_button_press(data):
    global game_paused, dead, game_won
    if Menu.menu.info == 'start' and int(data) != 0:        # button pressed while start-menu: start game
        game_paused = False
        return
    elif Menu.menu.info == 'win' and int(data) != 0:        # button pressed while win-menu: reset game
        reset_variables()
        return
    elif Menu.menu.info == 'lose' and int(data) != 0:       # buttom pressed while lose-menu: reset game
        reset_variables()
        return
    if game_paused:                                         # button input put to sleep for half second
        sleep(0.5)                                          # to prevent unwanted double taps
    
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
    Menu.create_Menu()

def restart():
    Brick.restart_bricks()
    Player.restart_player()
    Ball.restart_ball()

# creates game elements as soon as window opens
@window.event 
def on_show():
    create_game()

@window.event
def on_draw():
    window.clear()
    if game_paused and not dead and not game_won:   # start-menu
        draw_game_elements()
        Menu.draw_start_menu()
        return
    elif game_paused and dead:                      # lose-menu
        Menu.draw_lose_menu()
        return
    elif game_paused and game_won:                  # win-menu
        Menu.draw_win_menu()
        return
    elif not game_paused:                           # in-game
        Ball.check_border_collision()
        Ball.check_brick_collision()
        Ball.check_player_collision()
        Player.get_DIPPID_data()
        draw_game_elements()
        Ball.update_ball()

sensor.register_callback('button_1', handle_button_press)
pyglet.app.run()