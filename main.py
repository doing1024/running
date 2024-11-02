import game

if __name__ == "__main__":
    game = game.Game()
    while True:
        game.tick()
        game.tryover()
        game.movedown()
        game.addlevel()
        game.makethings()
        game.show()
        game.setthings()
        game.flip()
        game.checkEvent()
