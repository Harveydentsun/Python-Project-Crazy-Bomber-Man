'''
Function:
    炸弹人小游戏
'''
import sys
import os
import cfg
import random
import pygame
from modules import *
from pathlib import Path
import pickle
import time
import numpy as np

#提供一个跑完结果的log，从而放入model.train，还有一个告诉电脑咋走的model.predict
from DQAgent import DQAgent
from DQNetwork import DQNetwork
# from bombermaaan import bomberman_train


'''游戏主程序'''
def main(cfg,model):
    # 初始化
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(cfg.BGMPATH)
    pygame.mixer.music.play(-1, 0.0)
    screen = pygame.display.set_mode(cfg.SCREENSIZE)
    pygame.display.set_caption('Crazy Bomber Man')
    # 开始界面
    player=Interface(screen, cfg, mode='game_start')    #这里player是1，因为只会返回这一个数字
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
        hero_sprite_group = pygame.sprite.Group()   #真实的玩家
        enemy1_sprite_group = pygame.sprite.Group() #对于玩家1而言的敌人
        enemy2_sprite_group = pygame.sprite.Group() #对于玩家2而言的敌人
        aihero_sprite_group = pygame.sprite.Group() #Ai玩家
        # -玩家Hero
        coordinate = map_parser.randomGetSpace(used_spaces)
        used_spaces.append(coordinate)
        hero1 = Hero(imagepaths=cfg.HERODKPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='DK')
        hero_sprite_group.add(hero1)
        enemy2_sprite_group.add(hero1)
        if player == 2:   #其实不用管，因为我们根本不会选这个选项
            coordinate = map_parser.randomGetSpace(used_spaces)
            used_spaces.append(coordinate)
            hero2 = Hero(imagepaths=cfg.HEROBATMANPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='BATMAN')
            hero_sprite_group.add(hero2)
            enemy1_sprite_group.add(hero2)
        else:
            # -电脑Hero两个，然后他们的行为都是随机数
            coordinate = map_parser.randomGetSpace(used_spaces)
            hero3=Hero(imagepaths=cfg.HEROBATMANPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='BATMAN')
            aihero_sprite_group.add(hero3)
            enemy1_sprite_group.add(hero3)
            enemy2_sprite_group.add(hero3)
            used_spaces.append(coordinate)
            coordinate = map_parser.randomGetSpace(used_spaces)
            hero4=Hero(imagepaths=cfg.HEROZELDAPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='ZELDA')
            aihero_sprite_group.add(hero4)
            enemy1_sprite_group.add(hero4)
            enemy2_sprite_group.add(hero4)
            used_spaces.append(coordinate)
        # -主循环
        screen = pygame.display.set_mode(map_parser.screen_size)
        clock = pygame.time.Clock()
        LOOP = True
        winner = 0
        log_sequence=[]    # 日志
        act=None
        Nopredict = 0
        count = 0
        while LOOP:
            if Nopredict == 0:
                Nopredict = 1
                dt = clock.tick(cfg.FPS)
                #第一步没有参数，我们就不跑了
            else:
                state=query_data(map_parser, hero1, enemy1_sprite_group, fruit_sprite_group, bomb_sprite_group, fire, act)['state'].reshape((1, 11, 13, 11))
                if count % 3 == 0:
                    action_index = model.get_action(state)  # 第二次运行以后开始有action
                else:
                    action_index = 5
                count += 1
                actions_list = ["up", "down", "right", "left", "bomb", None]
                ouraction = actions_list[action_index]
                dt = clock.tick(cfg.FPS)   #作用？更新循环频率？
                if ouraction == 'up':
                    hero1.move('up')
                elif ouraction == 'down':
                    hero1.move('down')
                elif ouraction == 'left':
                    hero1.move('left')
                elif ouraction == 'right':
                    hero1.move('right')
                elif ouraction == 'bomb':
                    if hero1.bomb_cooling_count <= 0:
                        bomb_sprite_group.add(hero1.generateBomb(imagepath=cfg.BOMBPATH, digitalcolor=cfg.YELLOW, explode_imagepath=cfg.FIREPATH))
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
            #对于第一个人来说2也是敌人，之前已经加入
            log_sequence.append(query_data(map_parser, hero1, enemy1_sprite_group, fruit_sprite_group, bomb_sprite_group, fire, act))
            pygame.display.update()
            clock.tick(cfg.FPS)
        if is_win_flag:
            Interface(screen, cfg, mode='game_switch', winner=winner, log=log_sequence)
        else:
            break
    Interface(screen, cfg, mode='game_end', log=log_sequence)


def main_train(cfg, model, episode):
    # 初始化
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode(cfg.SCREENSIZE)
    pygame.display.set_caption('Crazy Bomber Man')
    # 开始界面
    player=1   #这里player是1，因为只会返回这一个数字
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
        hero_sprite_group = pygame.sprite.Group()   #真实的玩家
        enemy1_sprite_group = pygame.sprite.Group() #对于玩家1而言的敌人
        enemy2_sprite_group = pygame.sprite.Group() #对于玩家2而言的敌人
        aihero_sprite_group = pygame.sprite.Group() #Ai玩家
        # -玩家Hero
        coordinate = map_parser.randomGetSpace(used_spaces)
        used_spaces.append(coordinate)
        hero1 = Hero(imagepaths=cfg.HERODKPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='DK')
        hero_sprite_group.add(hero1)
        enemy2_sprite_group.add(hero1)
        if player == 2:   #其实不用管，因为我们根本不会选这个选项
            coordinate = map_parser.randomGetSpace(used_spaces)
            used_spaces.append(coordinate)
            hero2 = Hero(imagepaths=cfg.HEROBATMANPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='BATMAN')
            hero_sprite_group.add(hero2)
            enemy1_sprite_group.add(hero2)
        else:
            # -电脑Hero两个，然后他们的行为都是随机数
            coordinate = map_parser.randomGetSpace(used_spaces)
            hero3=Hero(imagepaths=cfg.HEROBATMANPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='BATMAN')
            aihero_sprite_group.add(hero3)
            enemy1_sprite_group.add(hero3)
            enemy2_sprite_group.add(hero3)
            used_spaces.append(coordinate)
            coordinate = map_parser.randomGetSpace(used_spaces)
            hero4=Hero(imagepaths=cfg.HEROZELDAPATHS, coordinate=coordinate, blocksize=cfg.BLOCKSIZE, map_parser=map_parser, hero_name='ZELDA')
            aihero_sprite_group.add(hero4)
            enemy1_sprite_group.add(hero4)
            enemy2_sprite_group.add(hero4)
            used_spaces.append(coordinate)
        # -主循环
        screen = pygame.display.set_mode(map_parser.screen_size)
        clock = pygame.time.Clock()
        LOOP = True
        winner = 0
        log_sequence=[]    # 日志
        act=None
        Nopredict = 0
        while LOOP:
            if Nopredict == 0:
                Nopredict = 1
                dt = clock.tick(cfg.FPS)
                #第一步没有参数，我们就不跑了
            else:
                state=query_data(map_parser, hero1, enemy1_sprite_group, fruit_sprite_group, bomb_sprite_group, fire, act)['state'].reshape((1, 11, 13, 11))
                action_index = model.get_action(state)    #第二次运行以后开始有action
                actions_list = ["up", "down", "right", "left", "bomb", None]
                ouraction = actions_list[action_index]
                dt = clock.tick(cfg.FPS)   #作用？更新循环频率？
                if ouraction == 'up':
                    hero1.move('up')
                elif ouraction == 'down':
                    hero1.move('down')
                elif ouraction == 'left':
                    hero1.move('left')
                elif ouraction == 'right':
                    hero1.move('right')
                elif ouraction == 'bomb':
                    if hero1.bomb_cooling_count <= 0:
                        bomb_sprite_group.add(hero1.generateBomb(imagepath=cfg.BOMBPATH, digitalcolor=cfg.YELLOW, explode_imagepath=cfg.FIREPATH))
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
            #对于第一个人来说2也是敌人，之前已经加入
            log_sequence.append(query_data(map_parser, hero1, enemy1_sprite_group, fruit_sprite_group, bomb_sprite_group, fire, act))
            pygame.display.update()
            clock.tick(cfg.FPS)
        np.save('log/log'+str(episode)+'.npy',log_sequence)
        break


'''run'''
if __name__ == '__main__':
    n = 6
    IMG_SIZE = (11, 13)  #
    learning_rate = 0.00025
    dropout = 0
    replay_memory_size = 1e6
    minibatch_size = 64
    discount_factor = 0.99
    epsilon = 0.9
    epsilon_decrease_rate = 9e-7
    min_epsilon = 0.1
    training_count = 0
    episode = 0
    frame_counter = 0
    load = None
    train_agent = False
    evaluate_agent = False
    train_bool = True
    max_episodes = 100

    state_file = Path('crazy_bomberman_gym/data/bombermaaan.pickle')
    if state_file.exists():
        pickle_in = open(state_file, 'rb')
        learning_rate = pickle.load(pickle_in)
        dropout = pickle.load(pickle_in)
        replay_memory_size = pickle.load(pickle_in)
        minibatch_size = pickle.load(pickle_in)
        discount_factor = pickle.load(pickle_in)
        epsilon = pickle.load(pickle_in)
        epsilon_decrease_rate = pickle.load(pickle_in)
        min_epsilon = pickle.load(pickle_in)
        training_count = pickle.load(pickle_in)
        episode = pickle.load(pickle_in)
        frame_counter = pickle.load(pickle_in)
        pickle_in.close()

    network_input_shape = (11, IMG_SIZE[1], IMG_SIZE[0])
    DQA = DQAgent(n, network_input_shape, replay_memory_size=replay_memory_size, minibatch_size=minibatch_size,
                  learning_rate=learning_rate, discount_factor=discount_factor, dropout_prob=dropout, epsilon=epsilon,
                  epsilon_decrease_rate=epsilon_decrease_rate, min_epsilon=min_epsilon, load_path=load)
    # Restore state
    model_file = Path('crazy_bomberman_gym/data/bombermaaan.h5')
    if model_file.exists():
        DQA.DQN.model.load_weights(model_file)

    model_file = Path('crazy_bomberman_gym/data/bombermaaan_target.h5')
    if model_file.exists():
        DQA.DQN_target.model.load_weights(model_file)

    while True:
        main(cfg,DQA)
        # # 游戏跑完之后生成一个log文件
        # ls=os.lstdir()  #这里写一下文件路径（不同电脑不一样）
        # a=[x for x in ls if x[:3]=='log']    #文件的名字是logxxxxx.npy
        # path = './'+a[-1]
        # bomberman_train(path) #a里最后一个文件就是最新的log 拿去model做预测

