#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------
# The Glitch
# Un semplice platform game privo di scorrimento
# Glitchato alla follia
# By Penaz
#--------------------------------------------------
#Imports
#--------------------------------------------------
import pygame
from pygame.locals import *
from sys import exit
import pickle
#--------------------------------------------------
#Inizializziamo Pygame, schermo, clock e titolo della finestra
#--------------------------------------------------
pygame.init()
screen=pygame.display.set_mode((640,480),0,32)
pygame.display.set_caption("The Glitch 0.0.1 SNAPSHOT")
clock=pygame.time.Clock()           #Il clock serve per evitare differenze prestazionali
#--------------------------------------------------
# Variabili
#--------------------------------------------------
todraw=pygame.sprite.Group()            #Gruppo di sprite da disegnare
plats=pygame.sprite.Group()             #Gruppo di piattaforme
doors=pygame.sprite.Group()             #Gruppo porte
glitches={"WallClimb":False,"StickyCeil":False,"MultiJump":False,"HighJump":False,"Invincibility":False,"PermBodies":False,"FeatherFall":False,"BouncySpikes":False,"Hover":True}
level=""
hovervalue=False
Entrance=None
#--------------------------------------------------
# Classe piattaforma
#--------------------------------------------------
class Platform(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)     #Inizializzo la superclasse Sprite
        self.image=pygame.Surface((20,20))      #L'immagine è un quadrato 20x20px
        self.image.fill((0,255,0))              #Il colore è rosso
        self.rect=self.image.get_rect()         #Ricavo il rect per le collisioni
        self.rect.x=x                           #Posizionamento orizzontale
        self.rect.y=y                           #Posizionamento verticale
        plats.add(self)                         #Aggiungo al gruppo piattaforme
    def update(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))     #Stampa su schermo l'immagine della piattaforma
#--------------------------------------------------
# Classe spike
#--------------------------------------------------
class Spike(Platform):
    def __init__(self,x,y):
        Platform.__init__(self,x,y)
        self.image.fill((255,0,0))
#--------------------------------------------------
# Classe EntranceDoor
#--------------------------------------------------
class EntranceDoor(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.Surface((20,20))
        self.image.fill((255,194,0))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        todraw.add(self)
    def update(self):
        screen.blit(self.image, (self.rect.x,self.rect.y))
#--------------------------------------------------
# Classe ExitDoor
#--------------------------------------------------
class ExitDoor(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.Surface((20,20))
        self.image.fill((0,79,192))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        todraw.add(self)
        doors.add(self)
    def update(self):
        screen.blit(self.image, (self.rect.x,self.rect.y))
def doorcollide():
    collision=pygame.sprite.spritecollide(player,doors,False)
    if collision:
        pass        #No-op
#--------------------------------------------------
# Classe giocatore
#--------------------------------------------------
class Player(pygame.sprite.Sprite):
    move_x=0            #Movimento orizzontale
    move_y=0            #Movimento Verticale
    onground=False      #Bool che rappresenta lo stato in aria/a terra del giocatore
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.Surface((10,10))      #È un quadrato 10x10px
        self.image.fill((255,255,255))          #Colore Bianco
        self.rect=self.image.get_rect()
        self.rect.x=Entrance.rect.x
        self.rect.y=Entrance.rect.y
        todraw.add(self)
    def update(self):
        self.rect.x+=self.move_x                #Muovi orizzontalmente
        xcoll()                                 #Controlla le eventuali collisioni destra/sinistra
        self.rect.y+=self.move_y                #Muovi verticalmente
        ycoll()                                 #Controlla le collisioni sopra/sotto
        #Le 4 operazioni precedenti vanno fatte in quest'ordine altrimenti potrebbero esserci dei problemi di movimento
        screen.blit(self.image, (self.rect.x, self.rect.y))
#--------------------------------------------------
# Classe Cadavere, per il PermBody Glitch
#--------------------------------------------------
class PlayerBody(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.Surface((10,10))
        self.image.fill((200,200,200))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        todraw.add(self)
        plats.add(self)
    def update(self):
        screen.blit(self.image,(self.rect.x,self.rect.y))
#----------------------------------------------------------------------------------------------------
# Le collisioni vengono controllate separatamente per ogni asse, altrimenti
# potrebbero esserci degli strani "teletrasporti"
#----------------------------------------------------------------------------------------------------
#--------------------------------------------------
# Controllo Collisione orizzontale
#--------------------------------------------------
def xcoll():
    collision=pygame.sprite.spritecollide(player, plats, False)     #Controllo la collisione e ricavo i blocchi con cui collido
    for block in collision:         #Per ogni blocco con cui collido
        if player.move_x>0:             #Se mi muovevo verso destra
            player.rect.right=block.rect.left       #Il lato destro del giocatore corrisponderà con quello sinistro del blocco
            if glitches["WallClimb"]:
                player.move_y=-1
        if player.move_x<0:                         #|
            player.rect.left=block.rect.right       #|Viceversa per il lato sinistro
            if glitches["WallClimb"]:
                player.move_y=-1
#--------------------------------------------------
# Controllo collisione verticale
#--------------------------------------------------
def ycoll():
        collision=pygame.sprite.spritecollide(player, plats, False)         #Controllo la collisione e ricavo i blocchi con cui collido
        player.onground=False           #Porto a falso la variabile "giocatore poggia sul terreno", necessario per le cadute dalle piattaforme
        for block in collision:     #Per ogni blocco con cui collido
            if player.move_y==0:            #Se non mi muovo
                player.onground=True        #Sono a terra
            if player.move_y<0:         #Se mi muovo verso l'alto
                player.rect.top=block.rect.bottom       #La parte alta del giocatore corrisponderà con quella bassa del blocco
                if glitches["StickyCeil"]:
                    player.move_y=-1
                else:
                    player.move_y=0     #serve per evitare che il giocatore si "appiccichi" temporaneamente al soffitto
                player.onground=False       #Il giocatore sta saltando
            if player.move_y>0:         #Se mi muovo verso il basso (sto cadendo)
                player.rect.bottom=block.rect.top       #La parte inferiore del giocatore corrisponderà a quella superiore del blocco
                player.onground=True                    #Il giocatore poggia su una superficie
            if isinstance(block,Spike):
                if glitches["Invincibility"]:
                    pass
                elif glitches["BouncySpikes"]:
                    player.rect.bottom=block.rect.top-1
                    if glitches["HighJump"]:
                        player.move_y=-18
                    else:
                        player.move_y=-9
                else:
                    playerDeath(glitches["PermBodies"])
#--------------------------------------------------
# Morte del giocatore
#--------------------------------------------------
def playerDeath(perm):
    global player
    if perm:
        PlayerBody(player.rect.x,player.rect.y)
    player.kill()
    player=Player()
#--------------------------------------------------
# Carica livello da file
#--------------------------------------------------
def load(filename):
    with open(filename+".lvl",'rb') as f:
        global level
        global glitches
        level, glitches = pickle.load(f)
#--------------------------------------------------
# Costruzione del livello
#--------------------------------------------------
def build():
    #----------------------------------------------------------------------------------------------------
    # Una semplice routine per costruire il livello, ogni "#" corrisponde
    # ad un blocco 20x20 pixel di terreno/piattaforma
    # I livelli vengono costruiti da destra a sinistra e dall'alto in basso
    #----------------------------------------------------------------------------------------------------
    myx=0
    myy=0
    level=[
            '###########################',
            '#E            #           #',
            '#            #######     X#',
            '#                      ####',
            '#   ##            ##      #',
            '#  ####      #########    #',
            '#########^^################']      #Lo schema del livello
    with open("test.lvl",'wb') as f:
        pickle.dump([level,glitches],f)
    for r in level:         #Per ogni riga
        for c in r:         #Per ogni carattere nella riga
            global Entrance
            if c==' ':      #Se è uno spazio
                pass        #Non faccio nulla
            elif c=="E":
                Entrance=EntranceDoor(myx,myy)
            elif c=="X":
                p=ExitDoor(myx,myy)
            elif c=='#':        #Se è un #
                p=Platform(myx,myy)     #Creo una piattaforma 20x20 nella posizione myx,myy
            elif c=="^":
                p=Spike(myx,myy)
            myx+=20         #Vado a destra di 20px
        myy+=20             #Vado giù di 20px
        myx=0           #Resetto myx
#--------------------------------------------------
#Simulazione di gravità, molto semplicistica
#--------------------------------------------------
def gravity():
    if not player.onground:     #Se il giocatore sta cadendo (non è a terra)
        if glitches["FeatherFall"]:
            player.move_y+=0.4
        else:
            player.move_y+=0.9          #Muovi il giocatore verso il basso
load("test")
build()         #Costruisci il livello
player=Player()     #Nuova istanza del giocatore
#--------------------------------------------------
#Ciclo di gioco
#--------------------------------------------------
while True:
    screen.fill((0,0,0))        #Colora di nero lo sfondo, altrimenti resteranno delle scie
    gravity()                   #Simula la gravità
    #--------------------
    #Ciclo eventi
    #--------------------
    for event in pygame.event.get():        #Per ogni evento in attesa
        if event.type==QUIT:  #Uscita
            exit()      #Esci
        if event.type==KEYDOWN: #Viene premuto un tasto
            if event.key==K_UP:   #Freccia Su
                if glitches["MultiJump"]:
                    player.move_y=-9
                    player.onground=False
                elif glitches["Hover"]:
                    hovervalue=True
                    player.onground=False
                else:
                   if player.onground:   #Salta solo se il giocatore è a terra
                        if glitches["HighJump"]:
                           player.move_y=-18
                        else:
                            player.move_y=-9        #Salta
                        player.onground=False   #Il giocatore non è più a terra
            if event.key==K_LEFT: #Freccia Sinistra
                player.move_x=-5        #Muovi a sinistra
            if event.key==K_RIGHT:   #Freccia Destra
                player.move_x=5         #Muovi a destra
            if event.key==K_DOWN:    #Freccia Giu
                if glitches["StickyCeil"]:  #Sticky Ceiling Glitch
                    player.move_y=0
        if event.type==KEYUP:  #Viene rilasciato un tasto
            if event.key==K_UP:
                if glitches["Hover"]:
                    hovervalue=False
            if event.key==K_LEFT:   #Freccia Sinistra
                player.move_x=0     #Interrompi il movimento orizzontale
            if event.key==K_RIGHT:  #Freccia Destra
                player.move_x=0     #Interrompi il movimento orizzontale
    if hovervalue:
        player.move_y-=1.5
    doorcollide()
    todraw.update()     #Aggiorna lo stato delle sprites da disegnare
    plats.update()      #Aggiorna lo stato delle piattaforme
    pygame.display.update()     #Aggiorna il display
    #Faccio in modo che il gioco non vada oltre i 30FPS
    clock.tick(30)      #Tick, 30fps
