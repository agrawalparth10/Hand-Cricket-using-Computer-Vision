import pygame
from network import Network
import pickle
import numpy as np 
import cv2
import time
import pandas
import h5py
import tensorflow as tf

model  = tf.keras.models.load_model('/Users/parth/Desktop/Hand Cricket/handgesturemodel.h5')

video = cv2.VideoCapture(0)

t = 0
first_frame = None

pygame.font.init()

width = 700
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Hand Cricket")


class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render(self.text, 1, (255,255,255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


def redrawWindow(win, game, p):
    win.fill((128,128,128))

    if not(game.connected()):
        font = pygame.font.SysFont("comicsans", 80)
        text = font.render("Waiting for Player...", 1, (255,0,0), True)
        win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
    else:
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Your Move", 1, (0, 255,255))
        win.blit(text, (80, 200))

        text = font.render("Opponents", 1, (0, 255, 255))
        win.blit(text, (380, 200))

        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)
        player1_score = game.check_score(0)
        player2_score = game.check_score(1)
        text3 = font.render(str(player1_score), 1, (0,0,0))
        text4 = font.render(str(player2_score), 1, (0,0,0))
        win.blit(text3, (80, 100))
        win.blit(text4, (380, 100))

        if game.bothWent():
            text1 = font.render(str(move1), 1, (0,0,0))
            text2 = font.render(str(move2), 1, (0, 0, 0))
        else:
            if game.p1Went and p == 0:
                text1 = font.render(str(move1), 1, (0,0,0))
            elif game.p1Went:
                text1 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text1 = font.render("Waiting...", 1, (0, 0, 0))

            if game.p2Went and p == 1:
                text2 = font.render(str(move2), 1, (0,0,0))
            elif game.p2Went:
                text2 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text2 = font.render("Waiting...", 1, (0, 0, 0))

        if p == 1:
            win.blit(text2, (100, 350))
            win.blit(text1, (400, 350))
        else:
            win.blit(text1, (100, 350))
            win.blit(text2, (400, 350))

        for btn in btns:
            btn.draw(win)

    pygame.display.update()


btns = [Button("1", 50, 500, (0,0,0)), Button("2", 250, 500, (255,0,0)), Button("3", 450, 500, (0,255,0))]
def main():
    run = True
    clock = pygame.time.Clock()
    n = Network()
    player = int(n.getP())
    print("You are player", player)

    t = 0

    while run:
        clock.tick(60)

        t = t + 1   

        check,frame = video.read()
        roi = frame[100:500,100:500]
        gray = cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray,(21,21),0)
        cv2.imshow("thresh",gray)
        if t == 5:
            first_frame = gray
            continue

        try:
            game = n.send("get")
        except:
            run = False
            print("Couldn't get game")
            break

        if game.bothWent():
            redrawWindow(win, game, player)
            # pygame.time.delay(2000)
            try:
                game = n.send("reset")
            except:
                run = False
                print("Couldn't get game")
                break

            if game.game_finish():
                font = pygame.font.SysFont("comicsans", 90)
                if (game.winner() == 1 and player == 1) or (game.winner() == 0 and player == 0):
                    text = font.render("You Won!", 1, (255,0,0))
                elif game.winner() == -1:
                    text = font.render("Tie Game!", 1, (255,0,0))

                else:
                    text = font.render("You Lost...", 1, (255, 0, 0))
                win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            # change this
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in btns:
                    if btn.click(pos) and game.connected():
                        if player == 0:
                            if not game.p1Went:
                                buffer = 0
                                prediction = {0:0,1:0,2:0,3:0,4:0,5:0}
                                while(buffer < 30):
                                    check,frame = video.read()
                                    roi = frame[100:500,100:500]
                                    gray = cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
                                    gray = cv2.GaussianBlur(gray,(21,21),0)
                                    delta_frame = cv2.absdiff(first_frame,gray)
                                    thresh_delta = cv2.threshold(delta_frame,30,255,cv2.THRESH_BINARY)[1]
                                    thresh_delta = cv2.dilate(thresh_delta,None,iterations = 0)

                                    (_,cnts,_) = cv2.findContours(thresh_delta.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                                    for contours in cnts:
                                        if cv2.contourArea(contours) < 1000:
                                            continue
                                        (x,y,w,h) = cv2.boundingRect(contours)
                                        cv2.rectangle(roi,(x,y),(x+w,y+h),(0,255,0),3)

                                    # cv2.imshow("thresh",thresh_delta)
                                    thresh_delta = cv2.resize(thresh_delta,(128,128))
                                    stacked_img = np.stack((thresh_delta,)*3, axis=-1)
                                    stacked_img = stacked_img.reshape((1,stacked_img.shape[0],stacked_img.shape[1],stacked_img.shape[2]))
                                    val = model.predict(stacked_img)
                                    buffer += 1
                                    prediction[np.argmax(val)] += 1
                                    print(val)
                                    print(prediction[np.argmax(val)])

                                print(prediction)
                                max_val = 0
                                val_predict = 0
                                for i in range(6):
                                    if (max_val < prediction[i]):
                                        max_val = prediction[i]
                                        val_predict = i
                               
                                print("{} {}".format(val_predict,max_val))
                                n.send(str(val_predict))
                        else:
                            if not game.p2Went:
                                n.send(btn.text)

        redrawWindow(win, game, player)

def menu_screen():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        win.fill((128, 128, 128))
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (255,0,0))
        win.blit(text, (100,200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main()

while True:
    menu_screen()
