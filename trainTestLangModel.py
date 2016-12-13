from computerLangModel import ComputerLangModel as CLP


model = CLP(ngram=5)


lineMax= 33820
prevSpeaker=""
i = 0
myref = False
hits=0
count=0
poses= 0
sentenceGuess=False
sentenceActual=False
numSentTest=0
lowerTestBound=min(8/10,8/10)
upperTestBound=lowerTestBound+.2
testingLines = []
for line in open("data/ds9scripts2.txt", encoding='latin-1'):
    if (i < int(lineMax * lowerTestBound) or i > int(lineMax*upperTestBound)) and i< lineMax:
        speaker , line = line.split(":")
        line = line.split()
        model.trainLine(speaker,line)
    elif i < lineMax:
        testingLines.append(line)
    else:
        break
    i += 1


for line in testingLines:
    numSentTest += 1
    speaker, line = line.split(":")
    line = line.split()
    if speaker == 'COMPUTER':
        model.read(model.compTalk)
        continue
    if speaker != prevSpeaker:
        model.read(model.newSpeak)
        prevSpeaker = speaker
    for w in line:
        if w == model.refChar:
            myref = not myref
        else:
            model.read(w)
            sentenceActual = sentenceActual or myref
            sentenceGuess = sentenceGuess or model.guessCurrentRef()
            if w in model.punct:
                if sentenceActual and sentenceGuess:
                    hits += 1
                    print(line)
                if sentenceActual:
                    count += 1
                if sentenceGuess:
                    poses += 1
                sentenceGuess = False
                sentenceActual = False

    sentenceGuess = False
    sentenceActual = False
    # old code word based
    # if myref and model.guessCurrentRef():
    #     hits+=1
    # if myref:
    #     count+=1
    # if model.guessCurrentRef():
    #     poses+=1
    myref = False


print(model.counts[('computer',',')])
print("Recall "+ str(hits/count))
print("Precision " + str(hits/poses))
print("Perentage Sentences Guessed "+ str(poses/numSentTest))
print("Percentgage Sentence Actual "+ str(count/numSentTest))