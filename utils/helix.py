from random import randint

b = ":black_large_square:"
r = ":red_square:"
o = ":orange_square:"
p = ":purple_square:"
g = ":green_square:"

def t(char):
    return ":regional_indicator_"+char+":"

def text1(char):
    return b+b+t(char)+b+b

def text2(char):
    return b+t(char)+b+t(char)+b

def text3(char):
    return t(char)+b+b+b+t(char)

def text4(char):
    bp = ""
    rand = randint(0,3)
    if rand < 1:
        bp = r+o+o
    elif rand < 2:
        bp = o+r+r
    elif rand < 3:
        bp = p+g+g
    else:
        bp = g+p+p
    return t(char)+bp+t(char)

