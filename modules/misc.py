'''
Function:
	定义其他必要模块
'''
import sys
import pygame
import time
import numpy as np


'''在屏幕指定位置显示文字'''
def showText(screen, font, text, color, position):
	text_render = font.render(text, True, color)
	rect = text_render.get_rect()
	rect.left, rect.top = position
	screen.blit(text_render, rect)
	return rect.right


'''按钮'''
def Button(screen, position, text, buttoncolor=(120, 120, 120), linecolor=(20, 20, 20), textcolor=(255, 255, 255), bwidth=200, bheight=50):
	left, top = position
	pygame.draw.line(screen, linecolor, (left, top), (left+bwidth, top), 5)
	pygame.draw.line(screen, linecolor, (left, top-2), (left, top+bheight), 5)
	pygame.draw.line(screen, linecolor, (left, top+bheight), (left+bwidth, top+bheight), 5)
	pygame.draw.line(screen, linecolor, (left+bwidth, top+bheight), (left+bwidth, top), 5)
	pygame.draw.rect(screen, buttoncolor, (left, top, bwidth, bheight))
	font = pygame.font.SysFont('Consolas', 30)
	text_render = font.render(text, 1, textcolor)
	rect = text_render.get_rect()
	rect.centerx, rect.centery = left + bwidth / 2, top + bheight / 2
	return screen.blit(text_render, rect)


'''游戏开始/关卡切换/游戏结束界面'''
def Interface(screen, cfg, mode='game_start', winner=0, log=None):
	pygame.display.set_mode(cfg.SCREENSIZE)
	font = pygame.font.SysFont('Consolas', 50)
	if mode == 'game_start':
		clock = pygame.time.Clock()
		while True:
			screen.fill((41, 36, 33))
			showText(screen, font, 'Crazy Bomber Man', (255, 0, 0), (100, 50))
			button_1 = Button(screen, (220, 150), '1 PLAYER')
			button_2 = Button(screen, (220, 250), '2 PLAYERS')
			button_3 = Button(screen, (220, 350), 'QUIT')
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					if button_1.collidepoint(pygame.mouse.get_pos()):
						return 1
					elif button_2.collidepoint(pygame.mouse.get_pos()):
						return 2
					elif button_3.collidepoint(pygame.mouse.get_pos()):
						pygame.quit()
						sys.exit()
			pygame.display.update()
			clock.tick(cfg.FPS)
	elif mode == 'game_switch':
		np.save('log'+str(time.strftime('%Y%m%d%H%M%S', time.localtime()))+'.npy',log) # 存储上一局日志
		clock = pygame.time.Clock()
		while True:
			screen.fill((41, 36, 33))
			if winner == 0:
				showText(screen, font, 'You win!', (255, 255, 0), (200, 50))
			elif winner == 1:
				showText(screen, font, 'Player 1 wins!', (255, 255, 0), (150, 50))
			elif winner == 2:
				showText(screen, font, 'Player 2 wins!', (255, 255, 0), (150, 50))
			button_1 = Button(screen, (220, 150), 'NEXT')
			button_2 = Button(screen, (220, 250), 'QUIT')
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					if button_1.collidepoint(pygame.mouse.get_pos()):
						return True
					elif button_2.collidepoint(pygame.mouse.get_pos()):
						pygame.quit()
						sys.exit()
			pygame.display.update()
			clock.tick(cfg.FPS)
	elif mode == 'game_end':
		np.save('log'+str(time.strftime('%Y%m%d%H%M%S', time.localtime()))+'.npy',log) # 存储上一局日志
		clock = pygame.time.Clock()
		while True:
			screen.fill((41, 36, 33))
			showText(screen, font, 'You lost!', (255, 255, 0), (200, 50))
			button_1 = Button(screen, (220, 150), 'RESTART')
			button_2 = Button(screen, (220, 250), 'QUIT')
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					if button_1.collidepoint(pygame.mouse.get_pos()):
						return True
					elif button_2.collidepoint(pygame.mouse.get_pos()):
						pygame.quit()
						sys.exit()
			pygame.display.update()
			clock.tick(cfg.FPS)
	else:
		raise ValueError('Interface.mode unsupport %s...' % mode)
