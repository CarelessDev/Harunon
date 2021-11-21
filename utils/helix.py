from typing import List
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
    rand = randint(0, 3)
    if rand < 1:
        bp = r+o+o
    elif rand < 2:
        bp = o+r+r
    elif rand < 3:
        bp = p+g+g
    else:
        bp = g+p+p
    return t(char)+bp+t(char)


def makeHelix(text: str) -> List[str]:
    lines = 1
    helix = text3(text[0])
    toSend = []

    for i in range(len(text[1:])):
        i = i + 1
        lines += 1

        if i % 6 < 1:
            helix += "\n" + text3(text[i])
        elif i % 6 < 2:
            helix += "\n" + text4(text[i])
        elif i % 6 < 3:
            helix += "\n" + text2(text[i])
        elif i % 6 < 4:
            helix += "\n" + text1(text[i])
        elif i % 6 < 5:
            helix += "\n" + text2(text[i])
        else:
            helix += "\n" + text4(text[i])

        if lines >= 5:
            toSend.append(helix)
            lines = 0
            helix = ""

    if lines > 0:
        toSend.append(helix)

    return toSend
