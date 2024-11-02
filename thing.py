import random


def thingGroup(images, w, h):
    return (
        Thing(
            "player",
            images,
            [f"pl{i}" for i in range(1, 8)],
            switchTime=7,
            x1=w // 2 - 50,
            y1=h - 225,
            w=100,
            h=100,
        ),
        Thing(
            "background",
            images,
            [f"background{i}" for i in range(11)],
            switchTime=600,
            x1=0,
            y1=0,
            w=w,
            h=h,
        ),
        Thing(
            "ground",
            images,
            ["ground"],
            switchTime=1,
            x1=-50,
            y1=h - 125,
            w=w + 100,
            h=50,
        ),
    )


def jiGroup(images, fps, w, h):
    return [
        Ji(images, fps, tp[1], tp[0], w, h, tp[2],tp[3])
        for tp in zip(
            ["fly", "hide", "big", "bag"],
            [10, 20, 30, 5],
            [100, 50, 100, 50],
            [0, 0.05, 0.05, 0.1],
        )
    ]


def loadmusic(tp: int, pygame):
    if tp:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(r"bgm.mp3")
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()
        pygame.mixer.music.load("bgm2.mp3")
        pygame.mixer.music.play(-1)


def big_small(self, big):
    self.player.rect.w *= big
    self.player.rect.h *= big
    self.player.rect.x2 = self.player.x1 + self.player.rect.w
    self.player.rect.y2 = self.player.y1 + self.player.rect.h


class Rect:
    def __init__(
        self, x1: int, y1: int, x2: int = 0, y2: int = 0, w: int = 0, h: int = 0
    ):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2 if x2 else self.x1 + w
        self.y2 = y2 if y2 else self.y1 + h
        self.w = w if w else self.x2 - self.x1
        self.h = h if h else self.y2 - y1

    def peng(self, other):
        return bool(
            (self.x1 <= other.x1 <= self.x2 or self.x1 <= other.x2 <= self.x2)
            and (self.y1 <= other.y1 <= self.y2 or self.y1 <= other.y2 <= self.y2)
        )

    def move(self, x, y):
        self.x1 += x
        self.x2 += x
        self.y1 += y
        self.y2 += y


class Thing:
    def __init__(
        self,
        tp,
        images,
        imageList,
        switchTime=20,
        x1: int = 0,
        y1: int = 0,
        x2: int = 0,
        y2: int = 0,
        w: int = 0,
        h: int = 0,
    ):
        self.tp = tp
        self.images = dict()
        self.imageList = imageList
        for image in self.imageList:
            self.images[image] = images[image]
        self.imageTot = len(self.imageList)
        self.tck = 0
        self.imageNow = 0
        self.switchTime = switchTime
        if x2 == 0:
            self.rect = Rect(x1, y1, w=w, h=h)
        else:
            self.rect = Rect(x1, y1, x2=x2, y2=y2)
        self.ndp = False
        self.updateRectVars()

    def tick(self):
        self.tck += 1
        self.imageNow = self.tck // self.switchTime
        self.imageNow %= self.imageTot

    def image(self):
        return self.images[self.imageList[self.imageNow]]

    def peng(self, other, fillter=False):
        if type(other) == list:
            idx = 1
            for thing in other:
                if self.rect.peng(thing.rect):
                    if thing.tp == "guan" or not fillter:
                        return idx
                idx += 1
            return False
        else:
            return self.rect.peng(other.rect)

    def move(self, x, y):
        self.rect.move(x, y)
        self.updateRectVars()

    def updateRectVars(self):
        self.x1 = int(self.rect.x1)
        self.y1 = int(self.rect.y1)
        self.x2 = int(self.rect.x2)
        self.y2 = int(self.rect.y2)
        self.w = int(self.rect.w)
        self.h = int(self.rect.h)


class Ji:
    def __init__(self, images, fps, score, tp, w, h, size, rand=0.3):
        self.jiover = 300
        self.last = -3000
        self.ticktot = 0
        self.isbeing = False
        self.images = images
        self.fps = fps
        self.score = score
        self.jihight = lambda: random.randint(150, 300)
        self.tp = tp
        self.inf = 1000000000000000000000000000000000000000000
        self.w = w
        self.h = h
        self.size = size
        self.random = rand

    def canmake(self, score):
        return (
            random.random() < self.random
            and self.ticktot % self.fps * 10 == 0
            and score > self.score
            and not self.isbeing
        )

    def needpop(self, thing):
        return thing.tp == self.tp and self.isbeing

    def make(self):
        height = self.jihight()
        return Thing(
            self.tp,
            self.images,
            [self.tp],
            self.inf,
            self.w,
            self.h - 125 - height,
            w=self.size,
            h=self.size,
        )

    def sheng(self):
        return 5 - (self.ticktot - self.last) // 60

    def needover(self):
        return self.ticktot - self.last == self.jiover

    def tick(self):
        self.ticktot += 1

    def being(self):
        self.isbeing = True
        self.last = self.ticktot

    def over(self):
        self.isbeing = False

    def reset(self):
        self.isbeing = False
        self.last = -3000
        self.ticktot = 0
