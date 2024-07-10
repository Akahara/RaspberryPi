#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import pygame
import pygame.freetype
import pygame.gfxdraw
import traceback
import shutil
import math
import socket
import psutil
import glob
import time


IS_PIE = 'WONDER_PI' in os.environ

class LocalMachine:
    local_ip = None

    def get_local_ip():
        # TODO use cached ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        LocalMachine.local_ip = s.getsockname()[0]
        s.close()
        return LocalMachine.local_ip


class Display:
    REFRESH_RATE = 30
    FRAME_RATE = 1
    PRIMARY_COLOR = (163,  43,  43)
    DARKER_COLOR = ( 86,  22,  22)
    INDIVIDUAL_SCREEN_DURATION = 8

    screen = None
    screen_rect = pygame.Rect(0, 0, 0, 0)
    large_text_scale = 0
    large_font = None
    small_font = None
    boot_time = time.time()

    def __init__(self):
        pygame.init()
        print("Pygame init")
        info = pygame.display.Info()
        print(f"Screen is {info.current_w}x{info.current_h}")
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN) if IS_PIE else pygame.display.set_mode((640, 320))
        self.screen_rect = self.screen.get_rect()
        self.large_text_scale = int(self.screen_rect.height*.2)
        self.large_font = pygame.freetype.Font(os.path.join('res', 'Bruce Forever.ttf'), self.large_text_scale)
        self.small_font = pygame.freetype.Font(os.path.join('res', 'UbuntuMono-Regular.ttf'), self.large_text_scale)

    def run_loop(self):
        current_frame = -1
        done = False
        clock = pygame.time.Clock()
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        done = True
                if event.type == pygame.QUIT:
                    done = True
            if done:
                break

            if (current_frame := current_frame+1) % (Display.REFRESH_RATE // Display.FRAME_RATE) == 0:
                self.screen.fill((30, 30, 30))
                self.run_frame()
                pygame.display.flip()
            clock.tick(Display.REFRESH_RATE)
        pygame.quit()

    def run_frame(self):
        frame_funcs = [frame_large_current_time, frame_system_stats, frame_photo]
        try:
            ts = time.time()
            frame_funcs[int((ts - Display.boot_time) / Display.INDIVIDUAL_SCREEN_DURATION) % len(frame_funcs)]()
        except Exception as e:
            message = traceback.format_exc() + '\n' + repr(e)
            print(message, file=sys.stderr)
            rect = self.text_rect(message)
            scale = min(self.screen_rect.width / rect.width, self.screen_rect.height / rect.height, 1)
            self.rect(pygame.Rect(0, 0, rect.width*scale + 10, rect.height*scale + 10), (0,0,0,125))
            self.text(message, (0, 0), size=self.large_text_scale * scale)

    def text(self, text, pos, font=None, size=0, color=PRIMARY_COLOR):
        if font is None:
            font = self.small_font
        lines = text.splitlines()
        y = pos[1]
        for line in lines:
            rect = font.get_rect(line, size=size)
            rect.left = pos[0]
            rect.top = y
            font.render_to(self.screen, rect, line, color, size=size)
            y += rect.height

    def text_rect(self, text, font=None, size=0):
        if font is None:
            font = self.small_font
        lines = text.splitlines()
        w, h = (0, 0)
        for line in lines:
            rect = font.get_rect(line, size=size)
            w = max(w, rect.width)
            h += rect.height
        return pygame.Rect(0, 0, w, h)
    
    def rect(self, rect, color=PRIMARY_COLOR):
        if len(color) == 4:
            s = pygame.Surface(rect.size)
            s.set_alpha(color[3])
            s.fill(color)
            self.screen.blit(s, rect.topleft)
        else:
            pygame.draw.rect(self.screen, color, rect)

    def arc(self, x, y, r, start=0, stop=2*math.pi, color=PRIMARY_COLOR):
        points = [(x,y)]
        n = round(r*abs(stop-start)/20)
        if n < 2:
            n = 2
        for i in range(n):
            delta = i/(n-1)
            phi0 = start + (stop-start)*delta
            x0 = round(x+r*math.cos(phi0))
            y0 = round(y+r*math.sin(phi0))
            points.append((x0,y0))
        pygame.draw.polygon(self.screen, color, points)


def display_bottom_right_time():
    text = datetime.now().strftime("%H:%M")
    text_size = display.large_text_scale * .3
    rect = display.text_rect(text, font=display.large_font, size=text_size)
    rect.bottomright = display.screen_rect.bottomright
    rect.bottom -= 10
    rect.right -= 10
    display.text(text, rect.topleft, font=display.large_font, size=text_size)
    return rect

def frame_large_current_time():
    text1 = datetime.now().strftime("%H:%M")
    rect1 = display.text_rect(text1, font=display.large_font)
    rect1.center = display.screen_rect.center
    display.text(text1, rect1.topleft, font=display.large_font)

    text2 = " :" + datetime.now().strftime("%S")
    text2_scale = display.large_text_scale * .4
    rect2 = display.text_rect(text2, font=display.large_font, size=text2_scale)
    rect2.bottomleft = rect1.bottomright
    display.text(text2, rect2.topleft, font=display.large_font, size=text2_scale)

def frame_system_stats():
    margin = 20
    left = 20

    disk_usage = shutil.disk_usage('/')
    disk_usage_frac = disk_usage.used / disk_usage.total
    cpu_usage = psutil.cpu_percent()/os.cpu_count()
    ram_usage = psutil.virtual_memory()

    text = f"User       {os.getlogin():>16}\n" +\
           f"Local ip   {LocalMachine.get_local_ip():>16}\n" +\
           f"\n" +\
           f"Disk space {bytes_to_string(disk_usage.total):>16}\n" +\
           f"Disk used  {bytes_to_string(disk_usage.used):>16}\n" +\
           f"Disk free  {bytes_to_string(disk_usage.free):>16}\n" +\
           f"\n" +\
           f"CPU usage  {cpu_usage:>16.2%}\n" +\
           f"RAM usage  {ram_usage.percent/100:>16.2%}\n" +\
           f"RAM capacity {bytes_to_string(ram_usage.total):>14}\n" +\
           ""
    text_size = display.large_text_scale * .3
    display.text(text, (left + margin, margin), size=text_size)
    display.rect((left, 0, 2, display.screen_rect.height))
    
    rect1 = display_bottom_right_time()

    pie_size = display.screen_rect.height - 3 * margin - rect1.height
    pie_rect = pygame.Rect((0, 0), (pie_size, pie_size))
    pie_rect.topright = display.screen_rect.topright
    pie_rect.top += margin
    pie_rect.right -= margin
    display.arc(pie_rect.centerx, pie_rect.centery, pie_size/2, disk_usage_frac * math.tau, math.tau, Display.PRIMARY_COLOR)
    display.arc(pie_rect.centerx, pie_rect.centery, pie_size/2, 0, disk_usage_frac * math.tau, Display.DARKER_COLOR)
    
def frame_photo():
    left = 20
    margin = 20
    display.rect((left, 0, 2, display.screen_rect.height))
    display_bottom_right_time()

    img_bounds = pygame.Rect(left + margin, margin, (display.screen_rect.width - margin*2) * .7, (display.screen_rect.height - margin*2) * .7)

    image_name = 'no picture files'
    picture_files = glob.glob('pictures/**/*.jpg')
    display.rect(img_bounds, (5, 5, 5, 100))
    if len(picture_files) > 0:
        latest_file = max(picture_files, key=os.path.getmtime)
        image_name = latest_file
        img = pygame.image.load(latest_file).convert()
        img_rect = img.get_rect()
        img_rect.center = img_bounds.center
        img_rect = img_rect.fit(img_bounds)
        img = pygame.transform.scale(img, img_rect.size)
        display.screen.blit(img, img_rect)

    display.text(image_name, (left + margin, img_bounds.bottom + margin), size=display.large_text_scale*.25)

    total_pictures_space = sum(os.path.getsize(f) for f in picture_files)
    stats_text = f"Total pictures\n" +\
                 f"{len(picture_files)}\n" +\
                 f"\n" +\
                 f"Total disk space\n" +\
                 f"{bytes_to_string(total_pictures_space)}\n" +\
                 f"\n" +\
                 f"Avg image space\n" +\
                 f"{'-' if len(picture_files) == 0 else bytes_to_string(total_pictures_space / len(picture_files))}"
    stats_text_pos = (img_bounds.right + margin, img_bounds.top)
    stats_text_size = display.large_text_scale*.25
    display.text(stats_text, stats_text_pos, size=stats_text_size)


def bytes_to_string(count):
    exts = ['b', 'Kb', 'Mb', 'Gb']
    for e in exts:
        if count < 1024:
            return f'{round(count, 2)}{e}'
        count /= 1024
    return f'{count:.2g}Tb'


print("Running Interface!")
display = Display()
display.run_loop()
