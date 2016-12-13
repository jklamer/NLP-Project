from computerLangModel import ComputerLangModel as CLP



recall=[]
precision=[]
perctGuessed=[]
perctActual=[]
lineMax= 33820

for fold in range(5):
    model = CLP(ngram=5)
    prevSpeaker=""
    i = 0
    myref = False
    hits=0
    count=0
    poses= 0
    sentenceGuess=False
    sentenceActual=False
    numSentTest=0
    lowerTestBound=min(fold*2/10,8/10)
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
        speaker, line = line.split(":")
        line = line.split()
        currSentence = []
        if speaker == 'COMPUTER':
            model.read(model.compTalk)
            continue
        if speaker != prevSpeaker:
            model.read(model.newSpeak)
            prevSpeaker = speaker
        for n, w in enumerate(line):
            if w == model.refChar:
                myref = not myref
            else:
                model.read(w)
                currSentence.append((w,model.guessCurrentRef()))
                sentenceActual = sentenceActual or myref
                #sentenceGuess = sentenceGuess or model.guessCurrentRef()
                if w in model.punct or (n == len(line) - 2 and line[len(line)-1] == model.refChar ) or n == len(line)-1 :
                    numSentTest += 1
                    sentenceGuess=model.sentenceCheck(currSentence)
                    if sentenceActual and sentenceGuess:
                        hits += 1
                        print(currSentence)
                    if sentenceActual:
                        if not sentenceGuess:
                            pass
                            #print(currSentence)
                        count += 1
                    if sentenceGuess:
                        poses += 1
                    sentenceGuess = False
                    sentenceActual = False
                    currSentence=[]

        sentenceGuess = False
        sentenceActual = False
        currSentence=[]
        # old code word based
        # if myref and model.guessCurrentRef():
        #     hits+=1
        # if myref:
        #     count+=1
        # if model.guessCurrentRef():
        #     poses+=1
        myref = False

    recall.append(hits/count)
    precision.append(hits/poses)
    perctGuessed.append(poses/numSentTest)
    perctActual.append(count/numSentTest)

beta=2
r= sum(recall)/len(recall)
p=sum(precision)/len(precision)
f=(1+beta*beta)*(p*r/(r+beta*beta*p))
#print(model.counts[('computer',',')])
print("Recall "+ str(sum(recall)/len(recall)))
print("Precision " + str(sum(precision)/len(precision)))
print("F{} {}".format(beta,f))
print("Perentage Sentences Guessed "+ str(sum(perctGuessed)/len(perctGuessed)))
print("Percentgage Sentence Actual "+ str(sum(perctActual)/len(perctGuessed)))