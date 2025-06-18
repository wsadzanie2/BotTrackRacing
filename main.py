import time
import pygame
from pygame.event import Event
from pygame.locals import *
import math

screen = pygame.display.set_mode((1000, 1000), RESIZABLE)
cars_list = []
checkpoints_list = []
pygame.init()

font = pygame.font.SysFont(pygame.font.get_default_font(), 32)

car_img = pygame.image.load("assets/sport-car.png").convert_alpha()
track_image = pygame.image.load("assets/race-track.png").convert_alpha()
track_mask = pygame.mask.from_surface(track_image)
track_mask.invert()

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


class Checkpoint:
    def __init__(self, x, y, sx=50, sy=100) -> None:
        checkpoints_list.append(self)
        self.rect = pygame.Rect(x, y, sx, sy)
        self.index = len(checkpoints_list) - 1
    def draw(self, debug=False):
        global start
        if debug:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)
        elif self.index == 0:
            pygame.draw.rect(screen, (255, 255, 255), self.rect)
        # check for collisions
        for car in cars_list:
            x, y = car.get_poz()
            sx, sy = car_img.get_size()
            if self.rect.colliderect(pygame.Rect(x, y, sx, sy)):
                if debug:
                    pygame.draw.rect(screen, (0, 255, 0), self.rect)
                if car.cur_checkpoint == self.index:
                    car.cur_checkpoint += 1
                elif car.cur_checkpoint == len(checkpoints_list) and self.index == 0:
                    car.cur_checkpoint = 1
                    print(car.cur_checkpoint)
                    car.cur_lap_time = time.time() - start
                    start = time.time()
                    if car.best_lap_time is None or car.cur_lap_time < car.best_lap_time:
                        car.best_lap_time = car.cur_lap_time


class Car:
    def __init__(self, x=300, y=50, control='bot') -> None:
        cars_list.append(self)
        self.x, self.y = x, y
        self.control = control
        self.angle = 0
        self.angle_change = 0
        self.topspeed = 30
        self.turning_speed = 5
        self.speed = 0
        self.cur_checkpoint = 1
        self.best_lap_time = None
        self.cur_lap_time = None
    def draw(self):
        self.angle += self.angle_change * dt
        self.angle %= 360
        self.x += self.speed * math.cos(math.radians(-self.angle)) * dt
        self.y += self.speed * math.sin(math.radians(-self.angle)) * dt
        rotated_image = rot_center(car_img, self.angle)
        # if self.check_collision(track_mask):
        #    pygame.draw.rect(screen, (0, 255, 0), img_rect)
        screen.blit(rotated_image, (self.x, self.y))
    def update(self, event: Event):
        if self.control == 'bot':
            return
        if event.type == KEYDOWN:
            if event.key == K_d:
                self.angle_change = 0
                self.angle_change -= self.turning_speed
            if event.key == K_a:
                self.angle_change = 0
                self.angle_change += self.turning_speed
            if event.key == K_w:
                self.speed += self.topspeed
            if event.key == K_s:
                self.speed -= self.topspeed
        elif event.type == KEYUP:
            if event.key == K_d:
                self.angle_change = 0
            if event.key == K_a:
                self.angle_change = 0
            if event.key == K_w:
                self.speed = 0
            if event.key == K_s:
                self.speed = 0

    def check_collision(self, track: pygame.Mask):
        # return track.overlap(rotated_car_images[int(self.angle)][1], (self.x, self.y))
        return track.overlap(pygame.mask.from_surface(rot_center(car_img, self.angle)), (self.x, self.y))

    def set_speed(self, speed):
        if speed > 0:
            self.speed = (min(speed, 100) / 100) * self.topspeed
        else:
            self.speed = (max(speed, -100) / 100) * self.topspeed

    def rotate_by(self, angle):
        self.angle += angle
        self.angle %= 360

    def get_poz(self):
        return self.x, self.y

    def will_hit_at(self, distance: int, rel_angle: int):
        self.angle %= 360
        rel_angle %= 360
        angle = math.radians((rel_angle - self.angle) % 360)
        angle %= 360
        x = self.x + 50 + (distance * math.cos(angle))
        y = self.y + 45 + (distance * math.sin(angle))
        try:
            return track_mask.get_at((x, y))
        except Exception:
            return False


Checkpoint(300 + car_img.get_width(), 40)
Checkpoint(1400, 100)
Checkpoint(1400, 775)
Checkpoint(350, 700)

clock = pygame.time.Clock()
dt = 0
start = time.time()
def run():
    global dt, start
    run = True
    dt = clock.tick() / 100
    # if dt > 0:
    #     print(f"FPS: {10 / dt}")
    screen.fill((25, 125, 25))
    screen.blit(track_image, (0,0))
    # Draw time
    screen.blit(font.render(f"{round(time.time() - start, 1)}s", True, (255, 255, 255), (0, 0, 0)), (0, 0))
    for index, car in enumerate(cars_list):
        car.draw()
        if car.best_lap_time is not None:
            screen.blit(font.render(f"{round(car.best_lap_time, 2)}s", True, (255, 255, 255), (0, 0, 0)), (0, 32 + (32 * index)))
        else:
            screen.blit(font.render(f"None", True, (255, 255, 255), (0, 0, 0)), (0, 32 + (32 * index)))
        if car.check_collision(track_mask):
            print("Game over!")
            if car.control != 'bot':
                Car(300, 50, control=car.control)
            else:
                Car(300, 50)
            start = time.time()
            cars_list.remove(car)
    for checkpoint in checkpoints_list:
        checkpoint.draw()
    for event in pygame.event.get():
        for car in cars_list:
            car.update(event)
        if event.type == QUIT:
            run = False
    pygame.display.flip()
    return run

if __name__ == '__main__':
    Car(300, 50, control='player')
    running = True
    print('Running!')
    while running:
        running = run()
    pygame.quit()
