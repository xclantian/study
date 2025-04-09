import sys
import pygame
from pygame.sprite import Group
import random

pygame.init()

# 设定字体路径为 Hiragino Sans GB
font_path = '/System/Library/Fonts/Hiragino Sans GB.ttc'

# 定义不同场景下的字体大小
button_font_size = 36
scoreboard_font_size = 24


def get_pygame_chinese_font(size):
    return pygame.font.Font(font_path, size)


class Settings:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (255, 255, 255)
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255, 0, 0)
        self.bullets_allowed = 3
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10
        self.fleet_direction = 1
        self.speedup_scale = 1.1
        self.score_scale = 1.5
        self.alien_bullet_speed = 0.5  # 新增：外星人子弹速度
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1.0
        self.fleet_direction = 1
        self.alien_points = 50
        self.alien_bullet_speed = 0.5  # 新增：初始化外星人子弹速度

    def increase_speed(self):
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
        self.alien_bullet_speed *= self.speedup_scale  # 新增：增加外星人子弹速度

class Ship:
    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        try:
            self.image = pygame.image.load('ship.bmp')
        except pygame.error:
            print("无法加载飞船图像，请检查 ship.bmp 文件是否存在。")
            sys.exit()
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
        self.moving_right = False
        self.moving_left = False

    def update(self):
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        self.rect.x = self.x

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop
        self.y = float(self.rect.y)

    def update(self):
        self.y -= self.settings.bullet_speed
        self.rect.y = self.y

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)

class AlienBullet(pygame.sprite.Sprite):  # 新增：外星人子弹类
    def __init__(self, ai_game, alien):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = alien.rect.midbottom
        self.y = float(self.rect.y)

    def update(self):
        self.y += self.settings.alien_bullet_speed
        self.rect.y = self.y

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)

class Alien(pygame.sprite.Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        try:
            self.image = pygame.image.load('alien.bmp')
        except pygame.error:
            print("无法加载外星人图像，请检查 alien.bmp 文件是否存在。")
            sys.exit()
        self.rect = self.image.get_rect()
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        self.x = float(self.rect.x)

    def check_edges(self):
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

    def update(self):
        self.x += (self.settings.alien_speed * self.settings.fleet_direction)
        self.rect.x = self.x

    def fire_bullet(self, ai_game):  # 新增：外星人发射子弹方法
        if random.randint(1, 15000) < 2:  # 3% 的概率发射子弹
            new_bullet = AlienBullet(ai_game, self)
            ai_game.alien_bullets.add(new_bullet)

class Button:
    def __init__(self, ai_game, msg):
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # 设置按钮的尺寸和颜色
        self.width, self.height = 200, 50
        self.button_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        self.font = get_pygame_chinese_font(button_font_size)

        # 创建按钮的矩形并将其居中
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # 准备按钮上的文本图像
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """将文本渲染为图像"""
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        """在屏幕上绘制按钮"""
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


class GameStats:
    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False
        self.high_score = 0
        self.aliens_killed = 0

    def reset_stats(self):
        self.ships_left = 3
        self.score = 0
        self.level = 1
        self.aliens_killed = 0


# 记分板类，用于显示游戏得分、最高得分和等级信息
class Scoreboard:
    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        # 使用 get_pygame_chinese_font 来获取中文字体，调整字体大小
        self.font = get_pygame_chinese_font(scoreboard_font_size)
        self.text_color = (0, 0, 0)
        self.prep_score()

        # 准备初始的得分、最高得分和等级图像
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships_left()
        self.prep_aliens_killed()

    def prep_score(self):
        try:
            rounded_score = round(self.stats.score, -1)
            score_str = f"得分: {str(self.stats.score)}"
            self.score_image = self.font.render(score_str, True, self.text_color, self.settings.bg_color)
            self.score_rect = self.score_image.get_rect()
            self.score_rect.right = self.screen_rect.right - 20
            self.score_rect.top = 20
            print(f"得分图像位置: {self.score_rect}")
        except Exception as e:
            print(f"得分图像渲染出错: {e}")

    def prep_high_score(self):
        high_score = round(self.stats.high_score, -1)
        high_score_str = f"历史最高分: {str(self.stats.high_score)}"
        self.high_score_image = self.font.render(high_score_str, True, self.text_color, self.settings.bg_color)
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = 20

    def prep_level(self):
        try:
            level_str = f"等级: {str(self.stats.level)}"
            self.level_image = self.font.render(level_str, True, self.text_color, self.settings.bg_color)
            self.level_rect = self.level_image.get_rect()
            # 将等级信息显示在得分信息下方，靠右对齐
            self.level_rect.right = self.score_rect.right
            self.level_rect.top = self.score_rect.bottom + 5
            print(f"等级图像位置: {self.level_rect}")
        except Exception as e:
            print(f"等级图像渲染出错: {e}")

    def prep_ships_left(self):
        ships_left_str = f"剩余飞船: {self.stats.ships_left}"
        self.ships_left_image = self.font.render(ships_left_str, True, self.text_color, self.settings.bg_color)
        self.ships_left_rect = self.ships_left_image.get_rect()
        self.ships_left_rect.topleft = (20, 20)

    def prep_aliens_killed(self):
        aliens_killed_str = f"已消灭外星人: {self.stats.aliens_killed}"
        self.aliens_killed_image = self.font.render(aliens_killed_str, True, self.text_color, self.settings.bg_color)
        self.aliens_killed_rect = self.aliens_killed_image.get_rect()
        self.aliens_killed_rect.topleft = (20, 50)

    def show_score(self):
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.screen.blit(self.ships_left_image, self.ships_left_rect)
        self.screen.blit(self.aliens_killed_image, self.aliens_killed_rect)

    def check_high_score(self):
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()


class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("横向射击")
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = Group()
        self.aliens = Group()
        self.alien_bullets = Group()  # 新增：外星人子弹组
        self._create_fleet()
        self.play_button = Button(self, "开始游戏")
        self.shot_sound = None
        self.explosion_sound = None
        try:
            self.shot_sound = pygame.mixer.Sound('shot.wav')
            self.explosion_sound = pygame.mixer.Sound('explosion.wav')
        except pygame.error:
            print("无法加载声音文件，请检查 shot.wav 和 explosion.wav 文件是否存在。")

    def run_game(self):
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullets()  # 新增：更新外星人子弹
            self._update_screen()

    def _check_events(self):
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)
        except Exception as e:
            print(f"事件处理出错: {e}")

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
            if self.shot_sound:
                self.shot_sound.play()
        elif event.key == pygame.K_q:
            sys.exit()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.stats.aliens_killed += len(aliens)
                if self.explosion_sound:
                    self.explosion_sound.play()
            self.sb.prep_score()
            self.sb.prep_aliens_killed()
            self.sb.check_high_score()
        if not self.aliens:
            self._start_new_level()

    def _start_new_level(self):
        self.bullets.empty()
        self.alien_bullets.empty()  # 新增：清空外星人子弹
        self._create_fleet()
        self.settings.increase_speed()
        self.stats.level += 1
        self.sb.prep_level()

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()  # 新增：清空外星人子弹
            self._create_fleet()
            self.ship.center_ship()
            self.sb.prep_ships_left()
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _update_aliens(self):
        self._check_fleet_edges()
        for alien in self.aliens.sprites():
            alien.update()
            alien.fire_bullet(self)  # 新增：让外星人尝试发射子弹
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        self._check_aliens_bottom()

    def _update_alien_bullets(self):  # 新增：更新外星人子弹
        self.alien_bullets.update()
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()

    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_high_score()
            self.sb.prep_ships_left()
            self.sb.prep_aliens_killed()
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()  # 新增：清空外星人子弹
            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for bullet in self.alien_bullets.sprites():  # 新增：绘制外星人子弹
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()