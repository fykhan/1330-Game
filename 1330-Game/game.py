import math
import os
import time
import curses

# how to use colors:
#1 https://docs.python.org/2/library/curses.html#curses.init_color
#2 https://docs.python.org/2/library/curses.html#curses.init_pair
#3 win.addstr(x, y, str, curses.color_pair(your_pair))
#4 (optional) https://sceweb.sce.uhcl.edu/helm/WEBPAGE-Python/documentation/howto/curses/node7.html

# unicode references:
# http://www.unicode.org/charts/PDF/U2580.pdf
# https://unicode.org/emoji/charts/full-emoji-list.html
# https://commons.wikimedia.org/wiki/File:Unicode_Braille_table.svg

# text to ascii art:
# https://patorjk.com/software/taag/#p=display&f=Small%20Slant&t=LEVEL%20SELECT

# NOTE
# need to call getinput() after addstr() to actually display the modified screen
# addstr() writes to a output buffer while getkey() flushes the buffer
# source: https://stackoverflow.com/questions/47644727/python-curses-not-showing-printed-text-untill-getkey-is-called

badguy = '\U0001F92C'
#badguy = '𓀠'     #  𓀠   웃 ꆜ ጰ

def printBoard(board, win):
    '''
    Prints board, also print enemy red
    updateboard(board to be printed, curses window for debugging)
    '''
    global badguy
    for ind, i in enumerate(board[::-1]):
        win.addstr(ind, 0, ''.join(i))
        for j in range(len(i)):
            if i[j] == badguy: win.addstr(ind, j, badguy, curses.color_pair(2))

def updateboard(filename, board, win):
    '''
    Inserts the level layout into the original board. 
    updateboard(file to be inserted, board, curses window for debugging)
    '''
    global badguy
    temp = []
    f= open(filename)
    for i in f.readlines()[::-1]:
        temp.append(list(i)[:-1])
        #win.addstr(1, 0, str(temp[-1]), curses.A_REVERSE)
        #getinput(win)
        #time.sleep(2)
    #print(n[0])
    r = len(temp)
    c = max([len(t) for t in temp])
    res = board.copy()
    for i in range(r):
        for j in range(c):
            try:
                #print(f'board: {board[i][j]}, n: {n[i][j]}')
                if temp[i][j] == 'X':
                    res[i][j] = badguy
                else:
                    res[i][j] = temp[i][j]
            except IndexError:
                res[i][j] = ' '
    return res

def init(win, mspf):                
    '''
    Initializes the curses window
    init(curses window, milliseconds per frame (time between each successive frame))
    '''
    curses.use_default_colors()     #transparent background
    win.timeout(mspf)               #for how long win.getkey() waits for an input before terminating
                                    #since screen flushes with getkey(), the fps is also determined by this
    win.clear()                     #clear window
    curses.curs_set(0)              #disable blinking cursor
    curses.init_pair(1, 3, -1)      #initialize color pair 1 as orange text, transparent background
    curses.init_pair(2, 1, -1)      #initialize color pair 2 as red text, transparent background

def getinput(win):                 
    '''
    gets input, made so the NoInput exception dont have to be handled every time
    init(curses window, milliseconds per frame (time between each successive frame))
    '''
    k = None                        #returns None if no input is detected (normally an exception occurs)
    try:
        k = win.getkey()            #getkey() returns a string corresponding to key pressed
    except Exception as e:
        pass
    return k

def bar(win, x, y, lenn, sec, f, skinselect):             
    '''
    implements the power bar 
    bar(curses window, x and y coordinates of left edge of the bar, length of the bar, 
    number of sections of the bar, number of frames between each update (speed of the bar),
    and the appearance of the bar)
    '''
    c, l, d, Skin = 0, 1, 1, "\U0001f535\U0001f7e2\U0001f7e1\U0001f7e0\U0001f534"
    #c is the frame count, l is the current length, d is if its increasing or decreasing
    if skinselect == 'funni':
        Skin = "\U0001f642\U0001f604\U0001f606\U0001f602\U0001f923"
    elif skinselect == 'colorblind':
        Skin = "\U00000030\U00000031\U00000032\U00000033\U00000034"
    elif skinselect == 'love':
        Skin = "\U0001F499\U0001F49A\U0001F49B\U0001F9E1\U00002764"
    fullbar, curbar = "", [" "] * lenn #the full bar, which is used to update the current bar
    for i in range(sec): fullbar += Skin[i] * (lenn // sec)
    cur = 0 #current length
    while True:
        win.addstr(x, y, ''.join(curbar))
        #win.addstr(x + 1, y, '') 
        inp = getinput(win)
        if inp != None:
            curses.napms(500)
            return cur
        c += 1
        if c % f == 0:
            curbar[cur] = fullbar[cur] if d == 1 else ' '
            cur += d
        if cur == lenn - 1: d = -1
        if cur == 1: d = 1

def modify_meter(grid, ang):
    '''
    modifies the input grid to show the specificed angle with some maths
    modify_meter(boolean grid to be modified, angle)
    '''
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            grid[i][j] = abs(ang - (90 if j == 0 else math.degrees(math.atan(i / j)))) <= 1
                        #^checks if close to the angle
            grid[i][j] = grid[i][j] and i ** 2 + j ** 2 <= len(grid) ** 2
                        #^checks if distance to origian less than len(grid) to make it circular
    grid.reverse()      #reverse the grid since the rows are numbers 0 1 2 downwards

def arr_to_braille(grid):
    '''
    converts boolean 2d list to braille unicode chracters
    arr_to_braille(boolean grid)
    '''
    b = [[]]
    for i in range(0, len(grid), 4):
        if i != 0: b += [[]]
        for j in range(0, len(grid[0]), 2):
            o = ord('\u2800')   #braille characters are 256 characters after 2800 (including 2800)
            for k, (x, y) in enumerate(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (3, 0), (3, 1))):
                #enumerate over the dots and flip the bits that corresponds to the bits
                o += 2 ** k * grid[i + x][j + y]
            b[i // 4] += [chr(o)]
    return b

def meter(win, y, x, lenn, speed, subang):
    '''
    implements the rotating meter indicating the angle
    meter(curses window, x and y coordinates of meter origin, length of the meter in terms of character height, 
    number of frames between each update (speed of the bar), how much the angle changes every time)
    '''
    grid = [[0] * lenn * 4 for i in range(lenn * 4)]
    c, d, ang = 0, -1, 90
    while True:
        inp = getinput(win)
        if inp != None:
            curses.napms(500)
            return ang
        if c % speed == 0:
            ang += subang * d
            modify_meter(grid, ang)
            b = arr_to_braille(grid)
            b[-1][0] = '\u25ef'
            for ind, i in enumerate(b):
                try:
                    #win.addstr(y + ind, x, ''.join(list(map(str, map(int, i)))))
                    win.addstr(y + ind, x, ''.join(i))
                except curses.error:
                    pass
        c += 1
        if ang == 90: d = -1
        elif ang == 0: d = 1

def postobra(x, y, s):
    '''
    converts float position to braille character for less jagged trajectory
    postobra(x and y coordinate, size because only 1 dot was hard to see)
    '''
    yy, xx = math.floor((y - math.floor(y)) * 4), math.floor((x - math.floor(x)) * 2)
    bra = ['\u2840\u2880', '\u2804\u2820', '\u2802\u2810', '\u2801\u2808']
    #corresponds to ['⡀⢀', '⠄⠠', '⠂⠐', '⠁⠈']
    if s == 2:
        bra = ['\u28c0\u2880', '\u28e4\u28a0', '\u2836\u2830', '\u281b\u2818']
        #corresponds to ['⣀⢀', '⣤⢠', '⠶⠰', '⠛⠘']
    return bra[yy][xx]


def won(board, win):
    '''
    check if theres any enemy left
    won(board, curses window)
    '''
    global badguy
    #win.addstr(0, 10, 'checcking winning...')
    getinput(win)
    count = 0
    for i in board:
        for j in i:
            if j==badguy:
                count+=1
    
    #win.addstr(1, 10, 'count: ' + str(count))
    if count == 0:
        return True
    else:
        return False

def explode(win, board, x, y):
    global badguy
    e = (' ▀███▀ ', '███████', ' ▄███▄ ')
    c = ('2222222', '2211122', '2222222')
    res = board.copy()
    for i in range(3):
        for j in range(7):
            nx, ny = x - 1 + i, y - 3 + j
            if nx >= 0 and nx < len(board) and ny >= 0 and ny < len(board[0]):
                win.addstr(20 - nx, ny, e[i][j], curses.color_pair(int(c[i][j])))
                if e[i][j] != ' ' and board[i][j] == badguy: res[i][j] = ' '
    getinput(win)
    curses.napms(500)
    printBoard(board, win)
    win.addstr(20, 0, '\u2580' * 100)
    return res

def projectile(angle, power, win, n):
    global badguy
    printBoard(n, win)
    #win.addstr(0, 20, 'press q to quit')
    win.addstr(1, 0, 'Angle:')
    #angle = [15,30,45,60][bar(win, 21, 0, 20, 4, 1, 'love') // 5]
    angle = meter(win, 15, 0, 5, 2, 3)
    win.addstr(1, 0, 'Power:')
    power = bar(win, 21, 0, 20, 5, 4, 'funni') * 1.5
    if angle == -1 or power == -1.5:
        return
    #n = [[' ' for j in range(100)] for i in range(20)]
    #n = updateboard('level.txt', n)
    x = 0
    y = 0
    t = 0
    angle = math.radians(angle)
    n[y][x] = '\u2840'
    win.addstr(22, 0, 'angle: ' + str(round(math.degrees(angle))) + ', power: ' + str(power), curses.color_pair(1))
    while True:
        #os.system('clear')
        printBoard(n, win)
        try:
            n[int(y)][int(x)] = ' '
        except IndexError:
            pass
        getinput(win)
        #print(t,x,y)
        t += 0.05
        x = (power*t*math.cos(angle))
        y = ((power*t*math.sin(angle)) - 0.5*9.8*math.pow(t, 2))
        #win.addstr(11, 0, str(x) + ' ' + str(y) + '  ' + str(int(x)) + ' ' + str(int(y)) + '    ') #debug
        ix, iy = int(x), int(y)
        try:
            if n[iy][ix] == '|' or n[iy][ix] == '-':
                n[iy][ix] = ' '
                break
            if n[iy][ix] == '#':
                #n = explode(win, n, iy, ix)
                if won(n, win):
                    return []
                break
            hit = False
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if iy + i < 0 or iy + i >= len(n) or ix + j < 0 or ix + j >= len(n): continue
                    if n[iy + i][ix + j] == badguy:
                        n[iy + i][ix + j] = ' '
                        hit = True
            if hit:
                #n = explode(win, n, iy, ix)
                if won(n, win):
                    return []
                break
            n[int(y)][int(x)] = postobra(x, y, 2)
        except IndexError:
            pass
        if y<0:
            #n = explode(win, n, 0, ix)
            n[int(y)][int(x)] = ' '
            if won(n, win):
                return []
            break

    return n

def titlescreen(win):
    title = ["              //===========================================================================================\\\\",
    "             //=============================================================================================\\\\",
    "            ///                                                                                              \\\\\\",
    "           ///    ██___ ██___██_ __████__ ██████__ ██____██_ __█████___ __███___ ██______ ██______ _█████__   \\\\\\",
    "          |||   ██_██__ ███__██_ _██__██_ ██___██_ _██__██__ __██__██__ _██_██__ ██______ ██______ ██___██__   |||",
    "          |||__██___██_ ████_██_ ██______ ██___██_ __████___ __█████___ ██___██_ ██______ ██______ _███_____   |||",
    "          |||__███████_ ██_████_ ██__███_ ██████__ ___██____ __██___██_ ███████_ ██______ ██______ ___███___   |||",
    "          |||__██___██_ ██__███_ _██__██_ ██___██_ ___██____ __██___██_ ██___██_ ██____█_ ██____█_ ██___██__   |||",
    "           \\\\\\_██___██_ ██___██_ __████__ ██___██_ ___██____ __██████__ ██___██_ ███████_ ███████_ _█████___  ///",
    "            \\\\\\                                                                                              ///",
    "             \\\\============================================================================================ //",
    "              \\\\===========================================================================================//",
    "",
    "                           ",
    "                           ",
    "                  ⢀⣀⣤⣤⣶⣶⣿⣿⠿⠳⣙⡛⢿⡻⣿⢶⣶⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿██◣⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿ ◢██⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀                   ",
    "⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿████◣⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿◢████⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀                   ",
    "⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿█████◣⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿◢█████⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀",
    "⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿███████◣⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿◢███████⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀",
    "⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿█████████◣⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿◢█████████⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀",
    "⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀",
    "⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀",
    "⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆",
    "⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿",
    "⠿⢿⣿⣿⣿⣿⣯⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿",
    "⣿⣿⣿⣿⣿⣿⣿⣿⢿⣟⣿⣿⣿⡿██████████████████████⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿",
    "⣿⣿⣿⡹⣯⣽⣽⣿⣿⣷⣼⣿███⢿⣻⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿███⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿",
    "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿██⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿███⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⣿⣿",
    "⠠⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃",
    "⠀⣿⣿⣿⣿⣿⢿⣿⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣼⣿⣟⢷⣿⣟⣿⣿⣿⣿⣿⡿⠀⠀",
    "⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣻⣿⣿⣿⣿⣿⣿⠃⠀⠀",
    "⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣻⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀ ⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣻⣿⣿⢿⣿⡿⠟⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠙⡛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣲⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠏⡹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡹⠏⠃⠀",
    "                ⠙⠒⢬⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢾⡹⠏⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ",
    "                    ⠚⠚⠿⠷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠴⠞⠚"]
    for i in range(win.getmaxyx()[0]):
        if i == len(title): break
        win.addstr(i, 0, title[i])
    win.addstr(20, 80, "press any key to start", curses.A_REVERSE)
    while getinput(win) == None:
        #if detect any input then return
        #actually maybe add some options to choose like 'play' 'quit' etc
        pass

def playlevel(level, win):
    win.addstr(20, 0, '\u2580' * 100)
    N = [[' ' for j in range(100)] for i in range(20)]
    n = updateboard(level, N, win)
    printBoard(n, win)
    while True:
        n = projectile(0, 0, win, n)
        if n==[]:
            win.addstr(5, 10, ''' __   _____  _   _   ____ ___ ____    ___ _____ _ 
            \ \ / / _ \| | | | |  _ \_ _|  _ \  |_ _|_   _| |
             \ V / | | | | | | | | | | || | | |  | |  | | | |
              | || |_| | |_| | | |_| | || |_| |  | |  | | |_|
              |_| \___/ \___/  |____/___|____/  |___| |_| (_)           press any key''')

            while getinput(win) == None:
                pass
            break

def levelselect(win):
    win.clear()
    files = sorted([f for f in os.listdir('.') if os.path.isfile(f) and len(f) > 4 and f[-4:] == '.txt'])
    win.addstr(0, 5, '''
      / /  / __/ | / / __/ /    / __/ __/ /  / __/ ___/_  __/
     / /__/ _/ | |/ / _// /__  _\ \/ _// /__/ _// /__  / /   
    /____/___/ |___/___/____/ /___/___/____/___/\___/ /_/    ''')
    for i, f in enumerate(files):
        win.addstr(i+5, 25, f)
    getinput(win)
    pos = 0
    win.addstr(16, 0, 'Press arrow up / down to go up or down and Enter to select. Press q to quit.')
    win.addstr(pos + 5, 20, '===>')
    while True:
        c = getinput(win)
        if c == 'KEY_UP':
            pos = (pos + 9) % 10
            for i in range(5, 16):
                win.addstr(i, 20, '    ')
            win.addstr(pos + 5, 20, '===>')
        elif c == 'KEY_DOWN':
            pos = (pos + 1) % 10
            for i in range(5, 16):
                win.addstr(i, 20, '    ')
            win.addstr(pos + 5, 20, '===>')
        elif c == '\n':
            break
        elif c == 'q':
            curses.endwin()
    return files[pos]

def main(win):
    init(win, 10) #10 ms per frame, or 100 fps
    if win.getmaxyx()[0] < 25 or win.getmaxyx()[1] < 100:
        win.addstr(0, 0, 'error: terminal screen too small')
        win.addstr(1, 0, 'please enlarge your browser window and pull up the terminal subwindow')
        win.addstr(2, 0, 'you can also zoom out (ctrl minus) in your browser screen')
        win.addstr(3, 0, 'if still doesnt work please open a new terminal from the >_ button on top')
        win.addstr(4, 0, 'press ctrl-c to exit')
        getinput(win)
        time.sleep(100)
        return
    try:
        titlescreen(win)
        while True:
            level = levelselect(win)
            playlevel(level, win)
    except curses.error:
        win.addstr(0, 0, 'error: something went wrong')
        win.addstr(1, 0, 'try using a new terminal from the >_ button on top')
        win.addstr(2, 0, 'press ctrl-c to exit')
        getinput(win)
        time.sleep(100)
        
if __name__ == '__main__':
    curses.wrapper(main)
