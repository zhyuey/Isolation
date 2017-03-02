import random, pygame, sys
from pygame.locals import *

FPS = 30  # frames per second, the general speed of the program
WINDOWWIDTH = 600  # size of window's width in pixels
WINDOWHEIGHT = 600  # size of windows' height in pixels
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

    DISPLAYSURF.fill(BGCOLOR)
    drawBoard(mainBoard, playerTurn)
    move_cnt = 0

    last_move_X = None
    last_move_O = None

    while True:  # main game loop
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR)
        if playerTurn == 'O':
            drawBoard(mainBoard, 'O', legal_moves_O, last_move_O, last_move_X)
        else:
            drawBoard(mainBoard, 'O', legal_moves_X, last_move_X, last_move_O)

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
                    legal_moves_O = get_legal_moves(mainBoard, (boxx, boxy))
                    last_move_O = (boxx, boxy)
                elif playerTurn == 'X' and (boxx, boxy) in legal_moves_X:
                    mainBoard[boxx][boxy] = playerTurn
                    legal_moves_X = get_legal_moves(mainBoard, (boxx, boxy))
                    last_move_X = (boxx, boxy)
                else:
                    continue
                drawXO(playerTurn, boxx, boxy)

                move_cnt += 1
                if playerTurn == 'X':
                    playerTurn = 'O'
                else:
                    playerTurn = 'X'

                # Algorithm that check the game is over
                if hasWon(mainBoard):
                    pass
                if hasDraw(mainBoard):
                    pass
                    # -----------------------------
        # Redraw the screen and wait a clock tick.
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


def drawBoard(board, playerTurn, legal_moves=[], last_move_own=None, last_move_opp=None):
    # Draws all of the boxes in their covered or revealed state.
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
