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
    notrefChar='<nc>'
    newSpeak ='<ns>'
    compTalk = '<ct>'
    punct = {".","?","!"}
    def __init__(self, ngram = 3, tgram = 3):
        self.state=()
        self.counts = {}
        self.ref = False
        self.ngram = ngram
        self.prevSpeaker=""
        self.tagcounts = {}
        self.tagState = ()
        self.tgram = tgram

    def read(self, word):
        if len(self.state) >= self.ngram:
            self.state = self.state[1:] +(word,)
        else:
            self.state = self.state + (word,)

    def readTag(self, tag):
        if len(self.tagState) >= self.tgram:
            self.tagState = self.tagState[1:] +(tag,)
        else:
            self.tagState = self.tagState + (tag,)

    def trainLine(self, speaker, line):
        if speaker == 'COMPUTER':
            #print(line)
            self.read(self.compTalk)
            self.readTag(self.compTalk)
            return
        if self.prevSpeaker != speaker:
            self.read(self.newSpeak)
            self.readTag(self.newSpeak)
            #self.addToCounts(self.state)
        self.prevSpeaker=speaker
        for w in line:
            if w == self.refChar:
                self.ref = not self.ref
                #print("Ref Found")
            else:
                self.read(w)
                self.addToCounts(self.state)
                self.addToTagCounts(self.tagState,w)
                if self.ref:
                    self.readTag(self.refChar)
                else:
                    self.readTag(self.notrefChar)

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

    def addToTagCounts(self, tagState, word):
        if tagState not in self.tagcounts:
            self.tagcounts[tagState]={}
            self.tagcounts[tagState][self.refChar] = 0
            self.tagcounts[tagState][self.notrefChar] = 0
        if word not in self.tagcounts[tagState]:
            self.tagcounts[tagState][word] = State()
        if self.ref:
            self.tagcounts[tagState][word].c += 1
            self.tagcounts[tagState][self.refChar] += 1
        else:
            self.tagcounts[tagState][word].n += 1
            self.tagcounts[tagState][self.notrefChar] += 1

        if len(tagState) > 1:
            self.addToTagCounts(tagState[1:], word)

    def guessCurrentRef(self):
        pC = self.percentRefRec(self.state) * self.percentRefRecTag(self.tagState,self.state[len(self.state)-1]) #* self.refBasedOnTageState(self.tagState, self.refChar)
        pN = self.percentNRefRec(self.state) * self.percentNRefRecTag(self.tagState,self.state[len(self.state)-1]) #* self.refBasedOnTageState(self.tagState, self.notrefChar)

        if pN >= pC:
            return False
        else:
            return True

    def refBasedOnTageState(self, tagState, refT ):
        if len(tagState) == 0:
            return 1
        if tagState in self.tagcounts:
            return self.tagcounts[tagState][refT]/(self.tagcounts[tagState][self.refChar]+self.tagcounts[tagState][self.notrefChar])
        else:
            return self.refBasedOnTageState(tagState[1:], refT)


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
    # def percentRefRec(self, state):
    #     if len(state) == 0:
    #         return .5
    #     if state in self.counts:
    #         return  self.counts[state].percentC() #+ self.percentRefRec(state[1:])
    #     else:
    #         return self.percentRefRec(state[1:])

    def percentRefRecTag(self, tagState, word):
        if len(tagState) == 0:
            return 1
        if tagState in self.tagcounts and word in self.tagcounts[tagState]:
            return self.tagcounts[tagState][word].percentC()
        else:
            return self.percentRefRecTag(tagState[1:],word)

    def percentNRefRec(self, state):
        if len(state) == 0:
            return 0
        if state in self.counts:
            return len(state) * (1-self.counts[state].percentC()) + self.percentNRefRec(state[1:])
        else:
            return self.percentNRefRec(state[1:])
    # def percentNRefRec(self, state):
    #     if len(state) == 0:
    #         return .5
    #     if state in self.counts:
    #         return (1-self.counts[state].percentC()) #+ self.percentNRefRec(state[1:])
    #     else:
    #         return self.percentNRefRec(state[1:])

    def percentNRefRecTag(self, tagState, word):
        if len(tagState) == 0:
            return 1
        if tagState in self.tagcounts and word in self.tagcounts[tagState]:
            return (1 - self.tagcounts[tagState][word].percentC())
        else:
            return self.percentRefRecTag(tagState[1:],word)