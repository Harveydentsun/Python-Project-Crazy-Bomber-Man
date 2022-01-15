'''
Function:
    炸弹人小游戏
'''
import sys
import cfg
import random
import pygame
from modules import *


'''游戏主程序'''
def main(cfg):
    # 初始化
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(cfg.BGMPATH)
    pygame.mixer.music.play(-1, 0.0)
    screen = pygame.display.set_mode(cfg.SCREENSIZE)
    pygame.display.set_caption('Crazy Bomber Man')
    # 开始界面
    player=Interface(screen, cfg, mode='game_start')
    # 游戏主循环
    font = pygame.font.SysFont('Consolas', 15)
    for gamemap_path in cfg.GAMEMAPPATHS[:1]:
        # -地图
        map_parser = mapParser(gamemap_path, bg_paths=cfg.BACKGROUNDPATHS, wall_paths=cfg.WALLPATHS, blocksize=cfg.BLOCKSIZE)
        # -水果
        fruit_sprite_group = pygame.sprite.Group()
        used_spaces = []
        for i in range(5):
            coordinate = map_parser.randomGetSpace(used_spaces)
            used_spaces.append(coordinate)
            fruit_sprite_group.add(Fruit(random.choice(cfg.FRUITPATHS), coordinate=coordinate, blocksize=cfg.BLOCKSIZE))
        # -炸弹bomb
        bomb_sprite_group = pygame.sprite.Group()
        # -用于判断游戏胜利或者失败的flag
        is_win_flag = False
        # -生成英雄
        hero_sprite_group = pygame.sprite.Group()
        aihero_sprite_group = pygame.sprite.Group()
        # -玩家Hero
        coordinate = map_parser.randomGetSpace(used_spaces)
        used_spaces.append(coordinate)
        hero1 = Hero(imagepaths=cfg.HERODKPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='DK')
        hero_sprite_group.add(hero1)
        if player == 2:
            coordinate = map_parser.randomGetSpace(used_spaces)
            used_spaces.append(coordinate)
            hero2 = Hero(imagepaths=cfg.HEROBATMANPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='BATMAN')
            hero_sprite_group.add(hero2)
        else:
            # -电脑Hero
            coordinate = map_parser.randomGetSpace(used_spaces)
            aihero_sprite_group.add(Hero(imagepaths=cfg.HEROBATMANPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='BATMAN'))
            used_spaces.append(coordinate)
            coordinate = map_parser.randomGetSpace(used_spaces)
            aihero_sprite_group.add(Hero(imagepaths=cfg.HEROZELDAPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='ZELDA'))
            used_spaces.append(coordinate)
        # -主循环
        screen = pygame.display.set_mode(map_parser.screen_size)
        clock = pygame.time.Clock()
        LOOP = True
        winner = 0
        log_sequence=[]    # 日志
        act=None
        while LOOP:
            dt = clock.tick(cfg.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # --player1 WASD键控制上下左右, 空格键丢炸弹
                    if event.key == pygame.K_w:
                        hero1.move('up')
                        act = 'up'
                    elif event.key == pygame.K_s:
                        hero1.move('down')
                        act = 'down'
                    elif event.key == pygame.K_a:
                        hero1.move('left')
                        act = 'left'
                    elif event.key == pygame.K_d:
                        hero1.move('right')
                        act = 'right'
                    elif event.key == pygame.K_SPACE:
                        if hero1.bomb_cooling_count <= 0:
                            bomb_sprite_group.add(hero1.generateBomb(imagepath=cfg.BOMBPATH, digitalcolor=cfg.YELLOW, explode_imagepath=cfg.FIREPATH))
                            act = 'bomb'
                    if player == 2:
                        # --player2 ↑↓←→键控制上下左右, 有shift键丢炸弹
                        if event.key == pygame.K_UP:
                            hero2.move('up')
                        elif event.key == pygame.K_DOWN:
                            hero2.move('down')
                        elif event.key == pygame.K_LEFT:
                            hero2.move('left')
                        elif event.key == pygame.K_RIGHT:
                            hero2.move('right')
                        elif event.key == pygame.K_RSHIFT:
                            if hero2.bomb_cooling_count <= 0:
                                bomb_sprite_group.add(hero2.generateBomb(imagepath=cfg.BOMBPATH, digitalcolor=cfg.YELLOW, explode_imagepath=cfg.FIREPATH))
            screen.fill(cfg.WHITE)
            if player != 2:
                # --电脑Hero随机行动
                for hero in aihero_sprite_group:
                    action, flag = hero.randomAction(dt)
                    if flag and action == 'dropbomb':
                        bomb_sprite_group.add(hero.generateBomb(imagepath=cfg.BOMBPATH, digitalcolor=cfg.YELLOW, explode_imagepath=cfg.FIREPATH))
            # --吃到水果加生命值(只要是Hero, 都能加)
            if player == 2:
                for hero in hero_sprite_group:
                    hero.eatFruit(fruit_sprite_group)
            else:
                hero1.eatFruit(fruit_sprite_group)
                for hero in aihero_sprite_group:
                    hero.eatFruit(fruit_sprite_group)
            # --游戏元素都绑定到屏幕上
            map_parser.draw(screen)
            fire = [] # 火焰范围
            for bomb in bomb_sprite_group:
                if not bomb.is_being:
                    bomb_sprite_group.remove(bomb)
                explode_area = bomb.draw(screen, dt, map_parser)
                if explode_area:
                    fire = fire + explode_area
                    # --爆炸火焰范围内的Hero生命值将持续下降
                    for hero in hero_sprite_group:
                        if hero.coordinate in explode_area:
                            hero.health_value -= bomb.harm_value
                    for hero in aihero_sprite_group:
                        if hero.coordinate in explode_area:
                            hero.health_value -= bomb.harm_value
            fruit_sprite_group.draw(screen)
            for hero in aihero_sprite_group:
                hero.draw(screen, dt)
            for hero in hero_sprite_group:
                hero.draw(screen, dt)
            # --左上角显示生命值
            pos_x = -10
            for hero in hero_sprite_group:
                pos_x, pos_y = pos_x+15, 5
                pos_x = showText(screen, font, text=hero.hero_name+':'+str(hero.health_value), color=cfg.YELLOW, position=[pos_x, pos_y])
            for hero in aihero_sprite_group:
                pos_x, pos_y = pos_x+15, 5
                pos_x = showText(screen, font, text=hero.hero_name+'(ai):'+str(hero.health_value), color=cfg.YELLOW, position=[pos_x, pos_y])
            # --一方玩家生命值小于等于0/电脑方玩家生命值均小于等于0则判断游戏结束
            for hero in hero_sprite_group:
                if hero.health_value <= 0:
                    is_win_flag = True if player == 2 else False
                    winner = 2 if hero.hero_name == 'DK' else 1
                    LOOP = False
            for hero in aihero_sprite_group:
                if hero.health_value <= 0:
                    aihero_sprite_group.remove(hero)
            if len(aihero_sprite_group) == 0 and player != 2:
                is_win_flag = True
                LOOP = False
            # 记录日志
            log_sequence.append(query_data(map_parser, hero1, aihero_sprite_group, fruit_sprite_group, bomb_sprite_group, fire, act))
            pygame.display.update()
            clock.tick(cfg.FPS)
        if is_win_flag:
            Interface(screen, cfg, mode='game_switch', winner=winner, log=log_sequence)
        else:
            break
    Interface(screen, cfg, mode='game_end', log=log_sequence)


'''run'''
if __name__ == '__main__':
    while True:
        main(cfg)
