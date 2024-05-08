import pygame
import random as rdm
import os
import time

pygame.font.init()
Width = 750
Height = 750

screen = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Space Shooter")


# enemies
red_space_ship = pygame.image.load(os.path.join("space", "pixel_ship_red_small.png"))
yellow_space_ship = pygame.image.load(os.path.join("space", "pixel_ship_yellow.png"))
green_space_ship = pygame.image.load(
    os.path.join("space", "pixel_ship_green_small.png")
)
blue_space_ship = pygame.image.load(os.path.join("space", "pixel_ship_blue_small.png"))


# lasers
laser_yellow = pygame.image.load(os.path.join("space", "pixel_laser_yellow.png"))
laser_red = pygame.image.load(os.path.join("space", "pixel_laser_red.png"))
laser_green = pygame.image.load(os.path.join("space", "pixel_laser_green.png"))
laser_blue = pygame.image.load(os.path.join("space", "pixel_laser_blue.png"))
# player ship

# background
bg = pygame.image.load(os.path.join("space", "background-black.png"))
bg_scaled = pygame.transform.scale(bg, (Width, Height))


# Class
# ----------------
class Laser:
    def __init__(self, x, y, imag):
        self.x = x
        self.y = y
        self.img = imag
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not self.y <= height and self.y >= 0

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 15

    def __init__(
        self,
        x,
        y,
        health=100,
    ):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(Height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0

        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = yellow_space_ship
        self.laser_img = laser_yellow
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(Height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(
            window,
            (255, 0, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 10,
                self.ship_img.get_width(),
                10,
            ),
        )
        pygame.draw.rect(
            window,
            (0, 255, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 10,
                self.ship_img.get_width() * (self.health / self.max_health),
                10,
            ),
        )

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


class enemy(Ship):
    COLOR_MAP = {
        "red": (red_space_ship, laser_red),
        "green": (green_space_ship, laser_green),
        "blue": (blue_space_ship, laser_blue),
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


# ----------------


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 30, False)
    lost_font = pygame.font.SysFont("comicsans", 60, False)

    enemies = []
    wave_length = 5
    enemy_vel = 1
    laser_vel = 8.5

    player_velocity = 7

    player = Player(
        300,
        630,
    )
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    def redraw_window():
        screen.blit(bg_scaled, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        levle_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        screen.blit(lives_label, (10, 10))
        screen.blit(levle_label, (Width - levle_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)
        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            screen.blit(lost_label, (Width / 2 - lost_label.get_width() / 2, 350))
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemi = enemy(
                    rdm.randrange(50, Width - 100),
                    rdm.randrange(-1500, -100),
                    rdm.choice(["red", "blue", "green"]),
                )
                enemies.append(enemi)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q] and player.x - player_velocity > 0:
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < Width:
            player.x += player_velocity
        if keys[pygame.K_z] and player.y - player_velocity > 0:
            player.y -= player_velocity

        if (
            keys[pygame.K_s]
            and player.y + player_velocity + player.get_height() < Height
        ):
            player.y += player_velocity

        if keys[pygame.K_SPACE]:
            player.shoot()

        for foe in enemies[:]:
            foe.move(enemy_vel)
            foe.move_lasers(laser_vel, player)

            if rdm.randrange(0, 4 * 60) == 1:
                enemi.shoot()

            if collide(enemi, player):
                player.health -= 10
                enemies.remove(enemi)

            elif foe.y + foe.get_height() > Height:
                lives -= 1
                enemies.remove(foe)

        player.move_lasers(-laser_vel, enemies)


main()
