# Knapsack

# Django imports
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import random, string
from django.db import IntegrityError

# Local imports
from mysite import settings
from knapsack.models import *
from questionnaire.models import *

def start(request):
    # If logged_in, show index
    if check_login(request):
        u = get_user(request)
    else:
        usergroup = UserGroup.objects.filter(user_group=random.randint(1,5))
        id=len(RegUser.objects.all())+1
        # Create User with unique Id
        check=True
        while check==True:
            try:
                u=RegUser(user_code=str(id), nr=usergroup[0], mturk_code=makeSessionId(str(id)))
                u.ip=request.META['REMOTE_ADDR']
                u.save()
                check=False
            except IntegrityError:
                check=True
        request.session['logged_in'] = True
        request.session['user_code'] = u.user_code
        u.login=timezone.now()
        u.save()
    return render_to_response('knapsack/welcome.html', {'user': u}, context_instance=RequestContext(request))

def welcome(request, welcome_nr):
    # If logged_in, show index
    if check_login(request):
        u = get_user(request)
        if int(welcome_nr)==1:
            return render_to_response('knapsack/explanation.html', {'user': u}, context_instance=RequestContext(request))
        elif (int(welcome_nr)==2) or (int(welcome_nr)==3) or (int(welcome_nr)==4):
            user_group = UserGroup.objects.filter(user_group=u.nr.user_group)
            # Round is identified by the usergroup and the round number
            round = Round.objects.filter(user_group=user_group, nr=0)
            box_utility = Box.objects.filter(round=round[0])
            # exampleBoxes
            exampleBoxes = list()
            for i in range(1,5):
                exampleBoxes.append(box_utility[i])
            # ColorScale
            colorScale=list()
            for i in range(0,256):
                box=Box.objects.filter(round=round[0], colour=i)
                if len(box)>0:
                    colorScale.append(box[0])
            colorScale.reverse()
            bestBenefitBox = colorScale[0]
            if int(welcome_nr)==2:
                widthBox= 150 / len(colorScale)
                return render_to_response('knapsack/explanation2Benefit.html', {'box_utility': box_utility, 'user': u, 'colorScale': colorScale, 'widthBox': widthBox, 'exampleBoxes': exampleBoxes}, context_instance=RequestContext(request))
            elif int(welcome_nr)==3:
                return render_to_response('knapsack/explanation3Benefit.html', {'user': u, 'bestBenefitBox' : bestBenefitBox}, context_instance=RequestContext(request))
            else:
                # Tryout
                # Pass the information to the HTML-document
                return render_to_response('knapsack/tryoutBenefit.html', {'box_utility': box_utility, 'user': u, 'round': round[0], 'colorScale': colorScale} )
        elif int(welcome_nr)==6:
                    return render_to_response('knapsack/welcomeEnd.html', {'user': u}, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect("/welcome/")
    else:
        return HttpResponseRedirect("/welcome/")

def check_login(request):
    # Return True, if logged in, else FALSE
    if request.session.get('logged_in'):
        return request.session['logged_in']
    return False


def index(request, round_nr):
    if check_login(request):
        # User
        u = get_user(request)
        # Round Length
        round_length=len(Round.objects.filter(user_group=u.nr))
        
        # Log Time of Start
        if int(round_nr) == 1:
            u.gameStart=timezone.now()
            u.save()
        # End of knapsack, go to questionnaire
        if int(round_nr) >= round_length:
            return HttpResponseRedirect("/questionnaire/")
        
        # Go to next round
        else:
            # Round is identified by the usergroup and the round number
            round = Round.objects.filter(user_group=u.nr, nr=round_nr)
            # For each round, there is a defined box set
            box_utility = Box.objects.filter(round=round[0])
            # ColorScale
            colorScale=list()
            for i in range(0,256):
                box=Box.objects.filter(round=round[0], colour=i)
                if len(box)>0:
                    colorScale.append(box[0])
            colorScale.reverse()
            # Pass the information to the HTML-document
            return render_to_response('knapsack/indexBenefit.html', {'box_utility': box_utility, 'user': u, 'round': round[0], 'colorScale': colorScale}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/welcome/")

def get_user(request):
    # Get User by filtering "user_code"
    user = RegUser.objects.filter(user_code = request.session['user_code'])
    if len(user) > 0:
        return user[0]
    return False

def save(request, round_nr):
    payout = 0
    results = {'payout': payout}
    if request.method == u'GET':
        GET = request.GET
        # Get Id of box
        id = int(GET[u'id'])
        # Get Add or Remove of box
        kind = GET[u'kind']
        # Get User code
        user_code = GET[u'user_code']
        # Get current payout
        payout = GET[u'payout']
        
        # Identify Box by Id        
        box=Box.objects.filter(id=id)
        # Identify Round via box
        round = box[0].round
        # Identify User via User Code
        user=RegUser.objects.filter(user_code=user_code)
        
        # Identify whether event is add or remove the box from the knapsack
        if GET[u'kind'] == u'add':
            add=True
        else:
            add=False
        # Create Stat event with the information passed by Json
        stat = Stat(add=add, created = timezone.now(), user = user[0], box = box[0], round=round, payout=payout)
        stat.save()
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

def full(request, round_nr):
    payout = 0
    results = {'payout': payout}
    if request.method == u'GET':
        GET = request.GET
        # Identify User via User Code
        user=get_user(request)
        # Identify Round via box
        round = Round.objects.filter(user_group=user.nr, nr=int(round_nr))
        # Create Stat event with the information passed by Json
        stat = Stat.objects.filter(user=user, round=round).order_by('-created')[0]
        stat.full=True
        stat.save()
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

def savePayout(request):
    code = ""
    # results is the value which is passed via Jason
    results = {'code': code}
    if request.method == u'GET':
        GET = request.GET
        # User
        user = RegUser.objects.filter(user_code=GET[u'usercode'])[0]
        # Get payout
        payout = float(GET[u'payout'])
        # Save Payout
        user.payout=min(payout,0.63)
        code = user.mturk_code
        user.save()
    json = simplejson.dumps(code)
    return HttpResponse(json, mimetype='application/json')




@login_required
def test(request, user_group):
    # User Group
    usergroup=UserGroup.objects.filter(user_group=int(user_group))
    # Example User
    user = RegUser.objects.filter(nr=usergroup)
    request.session['logged_in'] = False
    request.session['logged_in'] = True
    request.session['user_code'] = user[0].user_code
    # Round is identified by the usergroup and the round number
    round = Round.objects.filter(user_group=usergroup, nr=1)
    # For each round, there is a defined box set
    box_utility = Box.objects.filter(round=round[0])
    # ColorScale
    colorScale=list()
    for i in range(0,256):
        box=Box.objects.filter(round=round[0], colour=i)
        if len(box)>0:
            colorScale.append(box[0])
    colorScale.reverse()
    
    # Pass the information to the HTML-document
    return render_to_response('knapsack/tryoutBenefit.html', {'box_utility': box_utility, 'user': user[0], 'round': round[0], 'colorScale': colorScale}, context_instance=RequestContext(request))
        

def makeSessionId(st):
	import md5, time, base64
	m = md5.new()
	m.update('this is a test of the emergency broadcasting system')
	m.update(str(time.time()))
	m.update(str(st))
	return string.replace(base64.encodestring(m.digest())[:-3], '/', '$')

@login_required
def statistics(request):
    return render_to_response('knapsack/statistics.html', context_instance=RequestContext(request))


@login_required
def export_round(request):
    
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export_round.csv'
    
    # Delimiter ',' for German Excel
    writer = csv.writer(response, dialect=csv.excel, delimiter=',')
    
    column_list = ["User Group", "Round", "KpOptimal", "delta"]
    writer.writerow(column_list)
    
    # List of Stat
    users = RegUser.objects.all().order_by('nr')
    # User
    for user in users:
        rounds = Round.objects.filter(user_group=user.nr).order_by('nr')
        # Round
        for round in rounds:
            answer_list = [u'%s' % (user.nr), u'%s' % (round.nr), u'%s' % (round.kpOptimal), u'%s' % (round.delta)]
            writer.writerow(answer_list)
    return response

@login_required
def export_box(request):
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export_box.csv'
    
    # Delimiter ',' for German Excel
    writer = csv.writer(response, dialect=csv.excel, delimiter=',')
    
    # time of download
    writer.writerow([timezone.now()])
    writer.writerow([])
    
    column_list = ["User Group","Round","Box ID", "Benefit", "Cost", "Colour"]
    writer.writerow(column_list)
    
    # List of Stat
    usergroups = UserGroup.objects.all().order_by('user_group')
    # User
    for usergroup in usergroups:
        rounds = Round.objects.filter(user_group=usergroup).order_by('nr')
        # Round
        for round in rounds:
            boxes=Box.objects.filter(round=round)
            for box in boxes:
                answer_list = [u'%s' % (usergroup.user_group), u'%s' % (round.nr), u'%s' % (box.id), u'%s' % (box.benefit), u'%s' % (box.cost), u'%s' % (box.colour)]
                writer.writerow(answer_list)
    return response

@login_required
def export_stat(request):
    
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export_stat.csv'
    
    # Delimiter ',' for German Excel
    writer = csv.writer(response, dialect=csv.excel, delimiter=',')
    column_list = ["User", "User Group", "Round", "Current Payout", "Time", "Add", "Id", "Benefit", "Cost", "Full"]
    writer.writerow(column_list)
    
    # List of Stat
    users = RegUser.objects.all().order_by('nr')
    # User
    for user in users:
        rounds = Round.objects.filter(user_group=user.nr).order_by('nr')
        # Round
        for round in rounds:
            answer_pre = [u'%s' % (user.user_code), u'%s' % (user.nr), u'%s' % (round.nr)]
            stats = Stat.objects.filter(user=user, round=round).order_by('created')
            if len(stats) > 0:
                # Stat
                for stat in stats:
                    answer_str = ""
                    # Payout, Time, Remove / Add, Id is saved in CSV-file
                    answer_str = [u'%s' % (stat.payout), u'%s' % (stat.created), u'%s' % (stat.add), u'%s' % (stat.box.id), u'%s' % (stat.box.benefit), u'%s' % (stat.box.cost), u'%s' % (stat.full)]
                    answer_list = answer_pre + answer_str
                    writer.writerow(answer_list)
    return response

@login_required
def export_user(request):
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export_user.csv'
    
    # Delimiter ',' for German Excel
    writer = csv.writer(response, dialect=csv.excel, delimiter=',')
    column_list = ["User", "User Group", "Payout", "IP", "Login", "GameStart", "GameEnd","QuestionanireStart","QuestionanireEnd", "Logout"]
    writer.writerow(column_list)
    # List of Users
    users = RegUser.objects.all().order_by('nr')
    for user in users:
        answers = [u'%s' % (user.user_code), u'%s' % (user.nr), u'%s' % (user.payout), u'%s' % (user.ip), u'%s' % (user.login), u'%s' % (user.gameStart), u'%s' % (user.gameEnd), u'%s' % (user.questionnaireStart), u'%s' % (user.questionnaireEnd), u'%s' % (user.logout)]
        writer.writerow(answers)
    
    return response

@login_required
def export_payout(request):
    
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export_user.csv'
    
    # Delimiter ',' for German Excel
    writer = csv.writer(response, dialect=csv.excel, delimiter=',')
    column_list = ["MturkCode", "Payout"]
    writer.writerow(column_list)
    # List of Users
    users = RegUser.objects.all().order_by('nr')
    for user in users:
        answers = [u'%s' % (user.mturk_code), u'%s' % (user.payout)]
        writer.writerow(answers)
    
    return response

