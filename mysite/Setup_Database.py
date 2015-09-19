from knapsack.models import *
from questionnaire.models import *
import random
from django.utils import timezone

# Reset data
UserGroup.objects.all().delete()
Round.objects.all().delete()
Box.objects.all().delete()
Stat.objects.all().delete()
Question.objects.all().delete()


question1=Question(text="How mentally demanding was the task?", explanation="", left="Very low", right="Very high")
question1.save()

question2=Question(text="How hurried or rushed was the pace of the task?", explanation="", left="Very low", right="Very high")
question2.save()

question3=Question(text="How successful were you in accomplishing what you were asked to do?", explanation="", left="Perfect", right="Failure")
question3.save()

question4=Question(text="How hard did you have to work to accomplish your level of performance?", explanation="", left="Very low", right="Very high")
question4.save()

question5=Question(text="How insecure, discouraged, irritated, stressed, and annoyed were you?", explanation="", left="Very low", right="Very high")
question5.save()

question6=Question(text="What box attribute did you mainly look for to reach your result?", explanation="", left="", right="")
question6.save()


question7=Question(text="If you read this question carefully, please respond with 1.", explanation="", left="", right="")
question7.save()

questions=Question.objects.all()

for question in questions:
	for i in range(1, 8):
		choice=Choice(question=question, nr=i, name=i)
		choice.save()

question=Question.objects.filter(text="What box attribute did you mainly look for to reach your result?")[0]
Choice.objects.filter(question=question).delete()
choice=Choice(question=question, nr=1, name="Size")
choice.save()
choice=Choice(question=question, nr=2, name="Colour")
choice.save()
choice=Choice(question=question, nr=3, name="Combination")
choice.save()
choice=Choice(question=question, nr=4, name="Other")
choice.save()


# Initialize deltas
# Current delta (relative)
delta=0

# Iterations
iteration=0

# Max Iterations for each round
maxIteration=100

# Min & Max Benefit
maxBenefit=80
minBenefit=1

# Following values just for updates shown in terminal while running the code
# Current delta (Abs)
deltaAbs=0
# current max delta (relative in Percent)
deltaMaxCurrent=0

# Creating 5 Usergroups with each 1 test round and 3 game rounds
for i in range(1, 6):
    usergroup = UserGroup(user_group=i)
    usergroup.save()
    for i in range(0, 4):
        round = Round(user_group=usergroup, kpOptimal=1, nr = i)
        round.save()

# Creating 5 Users, for testing purposes
user_code = ['', 'User1', 'User2', 'User3', 'User4', 'User5']
for i in range(1, len(user_code)):
    usergroup = UserGroup.objects.filter(user_group=i)
    user=RegUser(user_code=i, nr=usergroup[0], mturk_code=user_code[i])
    user.save()

# Setting up code
# Dummy Usergroup for creating a temporary round that is analyzed via the Greedy & Dynamic Algorithm
usergroupDummy = UserGroup(user_group=-1)
usergroupDummy.save()

# Log time when algorithm is started
start=timezone.now()

'Colour according to Benefit'
# Uniform Benefit
for roundNumber in range(0, 4):
    'Round: '+str(roundNumber+1)
    # Resetting delta values for each round
    delta=0
    deltaMaxCurrent=0
    deltaAbs=0
    # run algorithm until maxIteration is reached
    for iteration in range (0,maxIteration):
        # Setup dummy round
        Round.objects.filter(user_group=usergroupDummy).delete()
        round = Round(user_group=usergroupDummy, kpOptimal=1, nr = 2)
        round.save()
        # Create 100 boxes
        for iterator in range(1, 101):
            # Create Cost in range between 20 and 80
            cost=random.uniform(20, 80)
            benefit=random.uniform(minBenefit, maxBenefit)
            box1 = Box(round=round, benefit=benefit, colour=255, cost=cost)
            box1.save()
        # Search for optimal knapsack
        # Dynamic programming solution
        boxesCurrent = Box.objects.filter(round=round)
        n = len(boxesCurrent)
        u = n
        R= [ 695*[0] for p in range(n+2) ]
        valueKnapsackOptDynamic=0
        for box in boxesCurrent:
            for j in range(0, 695):
                if (box.cost+2<=j):
                    R[u][j]= max(box.benefit+R[u+1][j-box.cost-2], R[u+1][j])
                else:
                    R[u][j]=R[u+1][j]
            u = u-1
        valueKnapsackOptDynamic=R[1][694]
        # Greedy solution
        limit=694
        ratioCurrent = list()
        for box in boxesCurrent:
            ratioCurrent.append([box.benefit/float(box.cost), box.benefit, box.cost])
        ratioCurrent.sort()
        ratioCurrent.reverse()
        knapsackOpt=list()
        sizeKnapsackOpt=0
        valueKnapsackOptGreedy=0
        for ratioElement in ratioCurrent:
            if (sizeKnapsackOpt+ratioElement[2]+2<= limit):
                knapsackOpt.append(ratioElement)
                sizeKnapsackOpt += (ratioElement[2] + 2)
                valueKnapsackOptGreedy += ratioElement[1]
        # Calculate Deltas
        deltaAbs=valueKnapsackOptDynamic - valueKnapsackOptGreedy
        delta= (valueKnapsackOptDynamic/ float(valueKnapsackOptGreedy) -1)*100
        # If current delta is greater then deltaMaxCurrent, save delta, boxes, ratio, kpOptimal and show progress
        if deltaMaxCurrent < delta:
            deltaMaxCurrent=delta
            boxes=boxesCurrent
            ratio=ratioCurrent
            kpOptimal=valueKnapsackOptDynamic
            'Iterationsschritt: ' + str(iteration) +', Aktuelles Delta: ' + str(deltaMaxCurrent) + '/ ' + str(deltaAbs)
    # Use the same boxes to setup the round for each Usergroup
    # field 'boxes' holds the boxes of the optimal round
    # field 'ratio' holds the ratios of the optimal round
    # Calculate range of ratio
    spread=1
    rangeBenefit=maxBenefit-minBenefit
    # 2 Colors
    sizeStep=float(spread)/2
    currentUserGroup=1
    user_group= UserGroup.objects.filter(user_group=currentUserGroup)[0]
    round= Round.objects.filter(nr =roundNumber, user_group=user_group)[0]
    for box in boxes:
        if (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep):
            box1 = Box(round=round, benefit=box.benefit, colour=0,  cost=box.cost)
        else:
            box1 = Box(round=round, benefit=box.benefit, colour=255,  cost=box.cost)
        box1.save()
    # 3 Colors
    sizeStep=float(spread)/3
    currentUserGroup=2
    user_group= UserGroup.objects.filter(user_group=currentUserGroup)[0]
    round= Round.objects.filter(nr =roundNumber, user_group=user_group)[0]
    for box in boxes:
        if (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep):
            box1 = Box(round=round, benefit=box.benefit, colour=0,  cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*2):
            box1 = Box(round=round, benefit=box.benefit, colour=127,  cost=box.cost)
        else:
            box1 = Box(round=round, benefit=box.benefit, colour=255,  cost=box.cost)
        box1.save()
    # 7 Colors
    sizeStep=float(spread)/7
    currentUserGroup=3
    user_group= UserGroup.objects.filter(user_group=currentUserGroup)[0]
    round= Round.objects.filter(nr =roundNumber, user_group=user_group)[0]
    for box in boxes:
        if (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep):
            box1 = Box(round=round, benefit=box.benefit, colour=0,  cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*2):
            box1 = Box(round=round, benefit=box.benefit, colour=43, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*3):
            box1 = Box(round=round, benefit=box.benefit, colour=85,  cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*4):
            box1 = Box(round=round, benefit=box.benefit, colour=128, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*5):
            box1 = Box(round=round, benefit=box.benefit, colour=170, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*6):
            box1 = Box(round=round, benefit=box.benefit, colour=213, cost=box.cost)
        else:
            box1 = Box(round=round, benefit=box.benefit, colour=255,  cost=box.cost)
        box1.save()
    # 11 Colors
    sizeStep=float(spread)/11
    currentUserGroup=4
    user_group= UserGroup.objects.filter(user_group=currentUserGroup)[0]
    round= Round.objects.filter(nr =roundNumber, user_group=user_group)[0]
    for box in boxes:
        if (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep):
            box1 = Box(round=round, benefit=box.benefit, colour=0,  cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*2):
            box1 = Box(round=round, benefit=box.benefit, colour=26, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*3):
            box1 = Box(round=round, benefit=box.benefit, colour=51, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*4):
            box1 = Box(round=round, benefit=box.benefit, colour=77, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*5):
            box1 = Box(round=round, benefit=box.benefit, colour=102, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*6):
            box1 = Box(round=round, benefit=box.benefit, colour=128, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*7):
            box1 = Box(round=round, benefit=box.benefit, colour=153, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*8):
            box1 = Box(round=round, benefit=box.benefit, colour=179, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*9):
            box1 = Box(round=round, benefit=box.benefit, colour=204, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*10):
            box1 = Box(round=round, benefit=box.benefit, colour=230, cost=box.cost)
        else:
            box1 = Box(round=round, benefit=box.benefit, colour=255, cost=box.cost)
        box1.save()
    # 15 Colors
    sizeStep=float(spread)/15
    currentUserGroup=5
    user_group= UserGroup.objects.filter(user_group=currentUserGroup)[0]
    round= Round.objects.filter(nr =roundNumber, user_group=user_group)[0]
    for box in boxes:
        if (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep):
            box1 = Box(round=round, benefit=box.benefit, colour=0,  cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*2):
            box1 = Box(round=round, benefit=box.benefit, colour=18, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*3):
            box1 = Box(round=round, benefit=box.benefit, colour=36, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*4):
            box1 = Box(round=round, benefit=box.benefit, colour=54, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*5):
            box1 = Box(round=round, benefit=box.benefit, colour=72, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*6):
            box1 = Box(round=round, benefit=box.benefit, colour=90, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*7):
            box1 = Box(round=round, benefit=box.benefit, colour=108, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*8):
            box1 = Box(round=round, benefit=box.benefit, colour=126, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*9):
            box1 = Box(round=round, benefit=box.benefit, colour=144, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*10):
            box1 = Box(round=round, benefit=box.benefit, colour=162, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*11):
            box1 = Box(round=round, benefit=box.benefit, colour=180, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*12):
            box1 = Box(round=round, benefit=box.benefit, colour=198, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*13):
            box1 = Box(round=round, benefit=box.benefit, colour=216, cost=box.cost)
        elif (float(box.benefit-minBenefit)/rangeBenefit)<=(0+sizeStep*14):
            box1 = Box(round=round, benefit=box.benefit, colour=234, cost=box.cost)
        else:
            box1 = Box(round=round, benefit=box.benefit, colour=255,  cost=box.cost)
        box1.save()
    # Optimal Value and the delta is saved for the round of each user group pairs
    for k in range(1,6):
        round=Round.objects.filter(nr =roundNumber, user_group=UserGroup.objects.filter(user_group=k))[0]
        round.kpOptimal=kpOptimal
        round.delta=deltaMaxCurrent
        round.save()
    'Round: '+str(roundNumber+1) + '; Delta: '+ str(deltaMaxCurrent) + ', Greedy percentage: '+ str(10000/(100+deltaMaxCurrent)) + '%'


# log finish
end=timezone.now()
# Show duration
'Duration: ' + str((end-start).seconds/60) + 'min'

j=0
for i in range(0,100):
    if random.randint(1,5)==5:
        j+=1
