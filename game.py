class Game:
    def __init__(self, id):
        self.p1Went = False
        self.p2Went = False
        self.ready = False
        self.id = id
        self.moves = [None, None]
        self.score = [0,0]
        self.batting = [True,False]
        self.finish = False

    # Player's move
    def get_player_move(self, p):
        return self.moves[p]

    # When player has made a move
    def play(self, player, move):
        self.moves[player] = int(move)
        if player == 0:
            self.p1Went = True
        else:
            self.p2Went = True

    # Game is connected
    def connected(self):
        return self.ready

    # Both have made a move
    def bothWent(self):
        return self.p1Went and self.p2Went

    # Game is finished
    def game_finish(self):
        return self.finish

    # Winner of the Game
    def winner(self):
        if(self.score[0] > self.score[1]):          # Player 1 wins
            return 0
        elif(self.score[0] < self.score[1]):        # Player 2 wins
            return 1
        else:
            return -1

    # Check which player is batting
    def check_batting(self):
        p1_batting = self.batting[0]
        p2_batting = self.batting[1]
        if(p1_batting and not p2_batting):
            return 0
        return 1

    # Check the score of each player
    def check_score(self,player):
        return self.score[player]


    # Updating Game Score
    def update_score(self):
        if(self.bothWent()):
            p1_move = self.moves[0]
            p2_move = self.moves[1]
            player_batting = self.check_batting()
            if (p1_move == p2_move):
                if(player_batting == 0):
                    self.batting[0] = False
                    self.batting[1] = True
                    return False
                else:
                    self.finish = True
                    return True
            else:
                if(player_batting == 0):
                    self.score[0] += p1_move
                    return True
                else:
                    self.score[1] += p2_move
                    if(self.check_score(0) < self.check_score(1)):
                        self.finish = True 
                        return True
                    return False               
         
    # Reset the Game
    def resetWent(self):
        self.p1Went = False
        self.p2Went = False