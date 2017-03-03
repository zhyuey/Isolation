import random, pygame, sys
from pygame.locals import *

FPS = 30  # frames per second, the general speed of the program
WINDOWWIDTH = 430 # size of window's width in pixels
WINDOWHEIGHT = 500  # size of windows' height in pixels
BOXSIZE = 50  # size of box height & width in pixels
GAPSIZE = 10  # size of gap between boxes in pixels
BOARDWIDTH = 7  # number of columns of icons
BOARDHEIGHT = 7  # number of rows of icons

# Colorset
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (100, 0, 0)
GREEN = (0, 100, 0)
BLUE = (0, 0, 100)

BGCOLOR = WHITE
BOXCOLOR = BLACK
HIGHLIGHTCOLOR = GRAY
LINECOLOR = WHITE
LEGALCOLOR = RED
LASTCOLOR = GREEN
LASTCOLOR2 = BLUE

O = 'O'
X = 'X'


def possible_move(board, r, c):
    if r < 0 or r >= BOARDWIDTH:
        return False
    if c < 0 or c >= BOARDWIDTH:
        return False
    if board[r][c] != 'b':
        return False

    return True


def get_legal_moves(board, move):
    r, c = move
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2), (1, 2), (2, -1), (2, 1)]
    valid_moves = [(r + dr, c + dc) for dr, dc in directions if possible_move(board, r + dr, c + dc)]

    return valid_moves


legal_moves_O = []
legal_moves_X = []


def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0  # used to store x coordinate of mouse event
    mousey = 0  # used to store y coordinate of mouse event
    pygame.display.set_caption('Isolation - zhyuey')

    mainBoard = [['b' for x in range(BOARDHEIGHT)] for y in range(BOARDWIDTH)]
    playerTurn = 'O'
    legal_moves_O = [(r, c) for r in range(BOARDWIDTH) for c in range(BOARDHEIGHT)]
    legal_moves_X = []
    firstSelection = None  # stores the (x, y) of the first box clicked.
    move_cnt = 0

    DISPLAYSURF.fill(BGCOLOR)
    drawBoard(mainBoard, playerTurn)
    drawStatus(playerTurn)
    move_cnt = 0

    last_move_X = None
    last_move_O = None

    while True:  # main game loop
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR)
        if playerTurn == 'O':
            drawBoard(mainBoard, 'O', legal_moves_O, last_move_O, last_move_X)
            drawStatus('O', move_cnt, len(legal_moves_O) == 0)
        else:
            drawBoard(mainBoard, 'O', legal_moves_X, last_move_X, last_move_O)
            drawStatus('X', move_cnt, len(legal_moves_X) == 0)


        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # the mouse is currently over a box.
            if mainBoard[boxx][boxy] == 'b':
                drawHighlightBox(boxx, boxy)
            if mainBoard[boxx][boxy] == 'b' and mouseClicked:
                if playerTurn == 'O' and (boxx, boxy) in legal_moves_O:
                    mainBoard[boxx][boxy] = playerTurn
                    if move_cnt == 0:
                        legal_moves_X = legal_moves_O.copy()
                        legal_moves_X.remove((boxx, boxy))
                    else:
                        legal_moves_X = get_legal_moves(mainBoard, last_move_X)
                    legal_moves_O = get_legal_moves(mainBoard, (boxx, boxy))
                    last_move_O = (boxx, boxy)
                elif playerTurn == 'X' and (boxx, boxy) in legal_moves_X:
                    mainBoard[boxx][boxy] = playerTurn
                    legal_moves_X = get_legal_moves(mainBoard, (boxx, boxy))
                    last_move_X = (boxx, boxy)
                    legal_moves_O = get_legal_moves(mainBoard, last_move_O)
                else:
                    continue
                drawXO(playerTurn, boxx, boxy)

                move_cnt += 1
                if playerTurn == 'X':
                    playerTurn = 'O'
                else:
                    playerTurn = 'X'

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def getBoxAtPixel(x, y):
    # Draw Box on display surface
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def drawStatus(PlayerTurn, count = 0, lose = False):
    left, top = leftTopCoordsOfBox(0, BOARDHEIGHT)
    myfont = pygame.font.SysFont(None, 24)
    turnstr = PlayerTurn + "'s turn"
    label = myfont.render(turnstr, 1, (0, 0, 0))
    DISPLAYSURF.blit(label, (left, top))

    cntstr = "Count: " + str(count)
    labelcnt = myfont.render(cntstr, 1, (0, 0, 0))
    DISPLAYSURF.blit(labelcnt, (left, top + 25))

    if lose == True:
        losestr = PlayerTurn + " lose"
        labellose = myfont.render(losestr, 1, (200, 0, 0))
        DISPLAYSURF.blit(labellose, (left, top + 50))

    left, top = leftTopCoordsOfBox(2, BOARDHEIGHT)
    redstr = "Red: You can move to this position"
    labelred = myfont.render(redstr, 1, LEGALCOLOR)
    DISPLAYSURF.blit(labelred, (left, top))

    greenstr = "Green: Your last position"
    labelgreen = myfont.render(greenstr, 1, LASTCOLOR)
    DISPLAYSURF.blit(labelgreen, (left, top + 25))

    bluestr = "Blue: Your opponent's last position"
    labelblue = myfont.render(bluestr, 1, LASTCOLOR2)
    DISPLAYSURF.blit(labelblue, (left, top + 50))



def drawBoard(board, playerTurn, legal_moves=[], last_move_own=None, last_move_opp=None):
    # Draws all of the boxes in their covered or revealed state.
    # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error


    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if (boxx, boxy) == last_move_own:
                pygame.draw.rect(DISPLAYSURF, LASTCOLOR, (left, top, BOXSIZE, BOXSIZE))
                drawXO(board[boxx][boxy], boxx, boxy)
                continue
            elif (boxx, boxy) == last_move_opp:
                pygame.draw.rect(DISPLAYSURF, LASTCOLOR2, (left, top, BOXSIZE, BOXSIZE))
                drawXO(board[boxx][boxy], boxx, boxy)
                continue

            if board[boxx][boxy] == 'b':
                if (boxx, boxy) in legal_moves:
                    pygame.draw.rect(DISPLAYSURF, LEGALCOLOR, (left, top, BOXSIZE, BOXSIZE))
                else:
                    pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
                drawXO(board[boxx][boxy], boxx, boxy)


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + GAPSIZE
    top = boxy * (BOXSIZE + GAPSIZE) + GAPSIZE
    return (left, top)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left, top, BOXSIZE, BOXSIZE))


def drawXO(playerTurn, boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    if playerTurn == 'X':
        pygame.draw.line(DISPLAYSURF, LINECOLOR, (left + 3, top + 3), (left + BOXSIZE - 3, top + BOXSIZE - 3), 4)
        pygame.draw.line(DISPLAYSURF, LINECOLOR, (left + BOXSIZE - 3, top + 3), (left + 3, top + BOXSIZE - 3), 4)
    elif playerTurn == 'O':
        HALF = int(BOXSIZE / 2)
        pygame.draw.circle(DISPLAYSURF, LINECOLOR, (left + HALF, top + HALF), HALF - 3, 4)


def hasWon(board):
    # Returns True if player 1 or 2 wins
    return True


def hasDraw(board):
    # Returns True if all the boxes have been filled
    for i in board:
        if None in i:
            return False
    return True


if __name__ == '__main__':
    main()
