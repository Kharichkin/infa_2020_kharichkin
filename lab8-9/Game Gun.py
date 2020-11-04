from random import randrange as rnd, choice, uniform
import tkinter as tk
from tkinter import messagebox as mb
import math
from PIL import Image, ImageTk

FPS = 30
GRAVITY = 1 * 30 / FPS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_LEVEL = 560
GROUND_WIDTH = 10
TANK_IMAGE = Image.open('tank3.png')
TANK_IMAGE_WIDTH, TANK_IMAGE_HEIGHT = TANK_IMAGE.size
TANK_INIT_COORDS = ((SCREEN_WIDTH - TANK_IMAGE_WIDTH / 2) / 2, GROUND_LEVEL - GROUND_WIDTH / 2 - TANK_IMAGE_HEIGHT / 2)
TANK_TURRET_HEIGHT = 0.25 * TANK_IMAGE_HEIGHT
TANK_SPEED = 5
TANK_INIT_HEALTH = 10
GUN_INIT_COORDS = (TANK_INIT_COORDS[0], TANK_INIT_COORDS[1] - TANK_TURRET_HEIGHT)
GUN_WIDTH = 10
GUN_POWER = (10 * 30 / FPS, 40 * 30 / FPS)
GUN_POWER_INCREMENT = 1 * 30 / FPS
GUN_LENGTH_TO_POWER_PROPORTION = 3 * FPS / 30
GUN_ANGLE = 0
GUN_COLOR = ('#%02x%02x%02x' % (5, 180, 89), 'orange')
BALL_RADIUS = 10
BALL_COLORS = ['blue', 'green', 'red', 'yellow']
TARGET_COORDS_X = (50, 750)
TARGET_COORDS_Y = (50, 400)
TARGET_RADIUS = (10, 50)
TARGET_MAX_POINTS = 5
TARGET_COLOR = 'red'
TARGET_SPEED = 15 * 30 / FPS
BULLET_LENGTH = 15
BULLET_COLOR = 'black'
BULLET_SPEED = 35 * 30 / FPS
BULLET_WIDTH = 3
BOMB_RADIUS = 10
BOMB_COLOR = 'black'

root = tk.Tk()
root.geometry('{}x{}'.format(SCREEN_WIDTH, SCREEN_HEIGHT))
root.resizable(False, False)
root.title("Game \"Gun\"")
canvas = tk.Canvas(root, bg='white')
canvas.focus_set()
canvas.pack(fill=tk.BOTH, expand=1)


class Ball:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.r = BALL_RADIUS
        self.vx = vx
        self.vy = vy
        self.color = choice(BALL_COLORS)
        self.id = canvas.create_oval(
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r,
            fill=self.color
        )

    def move(self):
        if self.y > GROUND_LEVEL - GROUND_WIDTH / 2 - BALL_RADIUS:
            self.x += self.vx
            self.vy = -self.vy
            self.y += self.vy
        else:
            self.x += self.vx
            self.vy += GRAVITY
            self.y += self.vy
        canvas.coords(
            self.id,
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r
        )


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.l = BULLET_LENGTH
        self.v = BULLET_SPEED
        self.angle = angle
        self.color = BULLET_COLOR
        self.id = canvas.create_line(
            self.x,
            self.y,
            self.x + self.l * math.cos(self.angle),
            self.y + self.l * math.sin(self.angle),
            fill=self.color,
            width=BULLET_WIDTH
        )

    def move(self):
        if self.y > GROUND_LEVEL - GROUND_WIDTH / 2 - BALL_RADIUS:
            canvas.delete(self.id)
        else:
            self.x += self.v * math.cos(self.angle)
            self.y += self.v * math.sin(self.angle)
        canvas.coords(
            self.id,
            self.x,
            self.y,
            self.x + self.l * math.cos(self.angle),
            self.y + self.l * math.sin(self.angle),
        )


class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = BOMB_RADIUS
        self.vy = 0
        self.color = BOMB_COLOR
        self.id = canvas.create_oval(
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r,
            fill=self.color
        )

    def move(self):
        self.vy += GRAVITY
        self.y += self.vy
        canvas.coords(
            self.id,
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r
        )


class Gun:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.power = GUN_POWER[0]
        self.angle = GUN_ANGLE
        self.power_on = False
        self.id = canvas.create_line(self.x, self.y,
                                     self.x + self.power * GUN_LENGTH_TO_POWER_PROPORTION * math.cos(self.angle),
                                     self.y + self.power * GUN_LENGTH_TO_POWER_PROPORTION * math.sin(self.angle),
                                     width=GUN_WIDTH, fill=GUN_COLOR[0])

    def aim_start(self, event):
        self.power_on = True

    def aim_end(self, event):
        global balls
        new_ball_x = self.x + (self.power * GUN_LENGTH_TO_POWER_PROPORTION + BALL_RADIUS) * math.cos(self.angle)
        new_ball_y = self.y + (self.power * GUN_LENGTH_TO_POWER_PROPORTION + BALL_RADIUS) * math.sin(self.angle)
        new_ball_vx = self.power * math.cos(self.angle)
        new_ball_vy = self.power * math.sin(self.angle)
        new_ball = Ball(new_ball_x, new_ball_y, new_ball_vx, new_ball_vy)
        balls.add(new_ball)
        self.power_on = False
        self.power = GUN_POWER[0]

    def power_up(self):
        if self.power_on:
            if self.power < GUN_POWER[1]:
                self.power += GUN_POWER_INCREMENT
            canvas.itemconfig(self.id, fill=GUN_COLOR[1])
        else:
            canvas.itemconfig(self.id, fill=GUN_COLOR[0])
        canvas.coords(self.id, self.x, self.y,
                      self.x + min(round(self.power) * GUN_LENGTH_TO_POWER_PROPORTION,
                                   round(GUN_POWER[1] * GUN_LENGTH_TO_POWER_PROPORTION)) * math.cos(self.angle),
                      self.y + min(round(self.power) * GUN_LENGTH_TO_POWER_PROPORTION,
                                   round(GUN_POWER[1] * GUN_LENGTH_TO_POWER_PROPORTION)) * math.sin(self.angle))

    def aiming(self, event):
        try:
            angle = math.atan((event.y - self.y) / (event.x - self.x))
            if event.x > self.x:
                self.angle = angle
            else:
                self.angle = angle + math.pi
        except ZeroDivisionError:
            if event.y > self.y:
                self.angle = math.pi / 2
            else:
                self.angle = - math.pi / 2

    def shoot(self, event):
        global bullets
        new_bullet_x = self.x + (self.power * GUN_LENGTH_TO_POWER_PROPORTION) * math.cos(self.angle)
        new_bullet_y = self.y + (self.power * GUN_LENGTH_TO_POWER_PROPORTION) * math.sin(self.angle)
        new_bullet = Bullet(new_bullet_x, new_bullet_y, self.angle)
        bullets.add(new_bullet)

    def move(self, event):
        if str(event.keysym) == 'Left':
            if self.x > TANK_IMAGE_WIDTH / 2:
                self.x -= TANK_SPEED
        if str(event.keysym) == 'Right':
            if self.x < SCREEN_WIDTH - TANK_IMAGE_WIDTH / 2:
                self.x += TANK_SPEED
        canvas.coords(self.id, self.x, self.y,
                      self.x + self.power * GUN_LENGTH_TO_POWER_PROPORTION * math.cos(self.angle),
                      self.y + self.power * GUN_LENGTH_TO_POWER_PROPORTION * math.sin(self.angle))


class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tank_render = ImageTk.PhotoImage(TANK_IMAGE)
        self.id = canvas.create_image(self.x, self.y, image=self.tank_render)
        self.gun = Gun(GUN_INIT_COORDS[0], GUN_INIT_COORDS[1])
        self.health = TANK_INIT_HEALTH

    def move(self, event):
        if str(event.keysym) == 'Left':
            if self.x > TANK_IMAGE_WIDTH / 2:
                self.x -= TANK_SPEED
        if str(event.keysym) == 'Right':
            if self.x < SCREEN_WIDTH - TANK_IMAGE_WIDTH / 2:
                self.x += TANK_SPEED
        canvas.coords(self.id, self.x, self.y)
        self.gun.move(event)


class Target:
    def __init__(self):
        self.x = rnd(TARGET_COORDS_X[0], TARGET_COORDS_X[1])
        self.y = rnd(TARGET_COORDS_Y[0], TARGET_COORDS_Y[1])
        self.r = rnd(TARGET_RADIUS[0], TARGET_RADIUS[1])
        self.v = TARGET_SPEED
        self.angle = uniform(0, 2 * math.pi)
        self.color = TARGET_COLOR
        self.points = math.ceil(
            TARGET_MAX_POINTS * (1 - (self.r - TARGET_RADIUS[0]) / (TARGET_RADIUS[1] + 1 - TARGET_RADIUS[0])))
        self.id = canvas.create_oval(self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r,
                                     fill=self.color)
        self.points_id = canvas.create_text(self.x, self.y, text=self.points, font='bold 15')

    def move(self):
        if (self.x < TARGET_COORDS_X[0]) or (self.x > TARGET_COORDS_X[1]): self.angle = -self.angle + math.pi
        if (self.y < TARGET_COORDS_Y[0]) or (self.y > TARGET_COORDS_Y[1]): self.angle = -self.angle

        self.x += self.v * math.cos(self.angle)
        self.y += self.v * math.sin(self.angle)
        canvas.coords(self.id, self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)
        canvas.coords(self.points_id, self.x, self.y)

    def is_hit_by_balls(self):
        global balls
        is_hit = False
        balls_for_deletion = set()
        for ball in balls:
            if (ball.x - self.x) ** 2 + (ball.y - self.y) ** 2 < (ball.r + self.r) ** 2:
                balls_for_deletion.add(ball)
                is_hit = True
        for ball in balls_for_deletion:
            canvas.delete(ball.id)
        balls = balls - balls_for_deletion
        return is_hit

    def is_hit_by_bullets(self):
        global bullets
        is_hit = False
        bullets_for_deletion = set()
        for bullet in bullets:
            if ((bullet.x + bullet.l * math.cos(bullet.angle) - self.x) ** 2 + (
                    bullet.y + bullet.l * math.sin(bullet.angle) - self.y) ** 2 < self.r ** 2) or (
                    (bullet.x - self.x) ** 2 + (bullet.y - self.y) ** 2 < self.r ** 2):
                bullets_for_deletion.add(bullet)
                is_hit = True
        for bullet in bullets_for_deletion:
            canvas.delete(bullet.id)
        bullets = bullets - bullets_for_deletion
        return is_hit


def main():
    global score, balls, bullets, bombs, target

    balls_for_deletion = set()
    for ball in balls:
        if (ball.x > SCREEN_WIDTH + BALL_RADIUS) or (ball.x < 0):
            canvas.delete(ball.id)
            balls_for_deletion.add(ball)
    balls = balls - balls_for_deletion
    for ball in balls:
        ball.move()
        if target.is_hit_by_balls():
            score += target.points
            canvas.delete(target.id)
            canvas.delete(target.points_id)
            bombs.add(Bomb(target.x, target.y))
            target = Target()

    bullets_for_deletion = set()
    for bullet in bullets:
        if (bullet.x > SCREEN_WIDTH + BALL_RADIUS) or (bullet.x < 0) or (bullet.y < 0) or (
                bullet.y > GROUND_LEVEL - GROUND_WIDTH / 2):
            canvas.delete(bullet.id)
            bullets_for_deletion.add(bullet)
    bullets = bullets - bullets_for_deletion
    for bullet in bullets:
        bullet.move()
        if target.is_hit_by_bullets():
            score += target.points
            canvas.delete(target.id)
            canvas.delete(target.points_id)
            bombs.add(Bomb(target.x, target.y))
            target = Target()

    bombs_for_deletion = set()
    for bomb in bombs:
        bomb.move()
        if ((bomb.x > tank.x + TANK_IMAGE_WIDTH / 2) or (bomb.x < tank.x - TANK_IMAGE_WIDTH / 2)) and (
                bomb.y > GROUND_LEVEL - GROUND_WIDTH / 2):
            canvas.delete(bomb.id)
            bombs_for_deletion.add(bomb)
        if ((bomb.x < tank.x + TANK_IMAGE_WIDTH / 2) and (bomb.x > tank.x - TANK_IMAGE_WIDTH / 2)) and (
                bomb.y > tank.y - TANK_IMAGE_HEIGHT / 2):
            tank.health -= 1
            canvas.delete(bomb.id)
            bombs_for_deletion.add(bomb)
    bombs = bombs - bombs_for_deletion

    target.move()
    tank.gun.power_up()
    canvas.itemconfig(score_text, text="Your score: {}".format(score))
    canvas.itemconfig(health_text, text="Your health: {}".format(tank.health))

    if tank.health > 0:
        root.after(round(1000 / FPS), main)
    else:
        answer = mb.askyesno(title="Game over",
                             message="Tank has been destroyed! \n Your score: {}".format(score) + "\n Start new game?")
        if answer:
            new_game()
        else:
            root.destroy()


def new_game():
    canvas.delete(tk.ALL)

    global score, balls, bullets, bombs, target, tank, score_text, health_text

    score = 0
    balls = set()
    bullets = set()
    bombs = set()
    target = Target()
    tank = Tank(TANK_INIT_COORDS[0], TANK_INIT_COORDS[1])

    canvas.bind('<Button-1>', tank.gun.aim_start)
    canvas.bind('<ButtonRelease-1>', tank.gun.aim_end)
    canvas.bind('<Motion>', tank.gun.aiming)
    canvas.bind('<Button-3>', tank.gun.shoot)
    canvas.bind('<Left>', tank.move)
    canvas.bind('<Right>', tank.move)
    score_text = canvas.create_text(10, 10, text="Your score: {}".format(score), font="bold 17", anchor=tk.NW)
    health_text = canvas.create_text(10, 40, text="Your health: {}".format(tank.health), font="bold 17", anchor=tk.NW)
    canvas.create_line((0, GROUND_LEVEL), (SCREEN_WIDTH, GROUND_LEVEL), width=GROUND_WIDTH)

    main()


global score, balls, bullets, bombs, target, tank, score_text, health_text
new_game()

root.mainloop()
