import autograd.numpy as np

class State:
    def __init__(self):
        self.c = 0
        self.n = 0
    def percentC(self):
        if self.c + self.n > 0:
            return self.c/(self.c+self.n)
    def __str__(self):
        return"C:{},NC:{}".format(self.c,self.n)


class ComputerLangModel:
    refChar = '<c>'
    newSpeak ='<ns>'
    compTalk = '<ct>'
    punct = {".","?","!"}
    def __init__(self, ngram = 3):
        self.state=()
        self.counts = {}
        self.ref = False
        self.ngram = ngram
        self.prevSpeaker=""

    def read(self, word):
        if len(self.state) >= self.ngram:
            self.state = self.state[1:] +(word,)
        else:
            self.state = self.state + (word,)

    def trainLine(self, speaker, line):
        if speaker == 'COMPUTER':
            #print(line)
            self.read(self.compTalk)
            return
        if self.prevSpeaker != speaker:
            self.read(self.newSpeak)
            self.addToCounts(self.state)
        self.prevSpeaker=speaker
        for w in line:
            if w == self.refChar:
                self.ref = not self.ref
                #print("Ref Found")
            else:
                self.read(w)
                self.addToCounts(self.state)

        self.ref = False

    def addToCounts(self, state):
        if state not in self.counts:
            self.counts[state] = State()
        if self.ref:
            self.counts[state].c += 1
        else:
            self.counts[state].n += 1
        if len(state) > 1:
            self.addToCounts(state[1:])


    def guessCurrentRef(self):
        pC = self.percentRefRec(self.state)
        pN = self.percentNRefRec(self.state)

        if pN >= pC:
            return False
        else:
            return True


    def sentenceCheck(self, sentence):
        numGuess=0
        for word, guess in sentence:
            if guess:
                numGuess+=1
        return numGuess/len(sentence) >= 0.2

    def percentRefRec(self, state):
        if len(state) == 0:
            return 0
        if state in self.counts:
            return len(state) * self.counts[state].percentC() + self.percentRefRec(state[1:])
        else:
            return self.percentRefRec(state[1:])

    def percentNRefRec(self, state):
        if len(state) == 0:
            return 0
        if state in self.counts:
            return len(state) * (1-self.counts[state].percentC()) + self.percentNRefRec(state[1:])
        else:
            return self.percentNRefRec(state[1:])