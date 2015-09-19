# Questionnaire

# Django imports
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.encoding import *

# Local imports
from mysite import settings
from knapsack.models import *
from questionnaire.models import *
from nicepass import nicepass

def welcome(request):
    # If logged_in, show index
    if check_login(request):
        user = get_user(request)
        # Log Game end time
        user.gameEnd=timezone.now()
        user.save()
        questionNr=len(Question.objects.all())
        return render_to_response('questionnaire/welcome.html', {'user': user, 'questionNr': questionNr}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/welcome/")

def detail(request, question_id):
    # If logged_in, show question
    if check_login(request):
        q = get_object_or_404(Question, pk=question_id)
        user = get_user(request)
        # If 1st Question, log Time
        if int(question_id)==1:
            user.questionnaireStart=timezone.now()
            user.save()
        return render_to_response('questionnaire/detail.html', {'question': q, 'user': user}, context_instance=RequestContext(request))
    # Else: Go to login-page
    else:
        return HttpResponseRedirect("/welcome/")


def vote(request, question_id):
    # If logged_in, show index
    if check_login(request):
        user = get_user(request)
        q = get_object_or_404(Question, pk=question_id)
        pn=Question.objects.count()
    
        try:
            selected_answer = q.choice_set.get(nr=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question form.
            return render_to_response('questionnaire/detail.html', {
                                  'question': q,
                                  'error_message': "You didn't select a choice.",
                                  }, context_instance=RequestContext(request))
        else:
            # Save answer to question and user
            answers = Answer.objects.filter(question = q, user = user)
            
            # If user already answered the question, answer will be overwritten
            if len(answers)>0:
                answer = answers[0]
            # If user has not answered the question yet
            else:
                answer = Answer()
                
            answer.question = q
            answer.user = user
            answer.answer = selected_answer
            answer.save()
        
            # End of questionnaire, logout
            if q.id>=pn:
            #Go to completion section
                # Log Time End of Questionnaire
                user.questionnaireEnd=timezone.now()
                user.save()
                return HttpResponseRedirect("/questionnaire/completed")
        
            # Go to next question
            else:
               return HttpResponseRedirect(reverse('questionnaire.views.detail', args=(q.id+1,)))
                   
    # Else: Go to login-page
    else:
        return HttpResponseRedirect("/welcome/")

def get_user(request):
    # Get User by filtering "user_code"
    user = RegUser.objects.filter(user_code = request.session['user_code'])
    if len(user) > 0:
        return user[0]
    return False


def completed(request):
    # If logged_in, show question
    if check_login(request):
        user = get_user(request)
        timeQuestionnaire = (timezone.now()-user.gameEnd).seconds
        error_message=u""
        if timeQuestionnaire < 15:
            error_message=u"yes"
        return render_to_response('questionnaire/completed.html', {'error_message': error_message, 'user':user, 'timeQuestionnaire':timeQuestionnaire}, context_instance=RequestContext(request))
    # Else: Go to login-page
    else:
        return HttpResponseRedirect("/welcome/")

def logout(request):
    if check_login(request):
        user=get_user(request)
        user.feedback=request.POST.get('feedback', '')
        # Log Time End of Questionnaire
        user.logout=timezone.now()
        user.save()
    
        # Set 'logged_in' to FALSE
        code=user.mturk_code
        usercode=user.user_code
        feedback=user.feedback
        
        round1=Round.objects.filter(user_group=user.nr, nr=1)[0]
        round2=Round.objects.filter(user_group=user.nr, nr=2)[0]
        round3=Round.objects.filter(user_group=user.nr, nr=3)[0]
    
        statsRound1 = Stat.objects.filter(user=user, round=round1).order_by('-created')
        statsRound2 = Stat.objects.filter(user=user, round=round2).order_by('-created')
        statsRound3 = Stat.objects.filter(user=user, round=round3).order_by('-created')
    
        payoutRound1=0
        payoutRound2=0
        payoutRound3=0
    
        if len(statsRound1)>0:
            payoutRound1=statsRound1[0].payout
        if len(statsRound2)>0:
            payoutRound2=statsRound2[0].payout
        if len(statsRound3)>0:
                payoutRound3=statsRound3[0].payout
                    
        if request.session != False:
            request.session['logged_in'] = False
        return render_to_response('questionnaire/logout.html',{'code': code, 'usercode': usercode, 'payoutRound1': payoutRound1, 'payoutRound2': payoutRound2, 'payoutRound3': payoutRound3 , 'feedback': feedback}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/welcome/")



def check_login(request):
    # Return True, if logged in, else FALSE
    if request.session.get('logged_in'):
        return request.session['logged_in']
    return False


@login_required
def export_answer(request):
    """
        Return a .csv-file containing all the answers submitted by the
        users.
        """
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export_answer.csv'
    
    writer = csv.writer(response, dialect=csv.excel, delimiter=',')
    questions=Question.objects.all()
    question_list = ["User", "User Group", "Question", "Answer"]
    writer.writerow(question_list)

    # User + Answers
    users = RegUser.objects.all().order_by('nr')
    for user in users:
        for question in questions:
            answer_list = [u'%s' % (user.user_code), u'%s' % (user.nr), u'%s' % (question.id)]
            answer = Answer.objects.filter(question = question, user = user)
            if len(answer) > 0:
                answer_list +=str(answer[0].answer.nr)
            writer.writerow(answer_list)
    return response

@login_required
def export_feedback(request):
    """
        Return a .csv-file containing all the answers submitted by the
        users.
        """
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export_feedback.csv'
    writer = csv.writer(response, dialect=csv.excel, delimiter=',')
    # User + Answers
    users = RegUser.objects.all().order_by('nr')
    # Feedback
    writer.writerow(["User", "User Group"])
    for user in users:
        feedback_list = [u'%s' % (user.user_code), u'%s' % (user.nr)]
        feedback_list += [(smart_str(user.feedback))]
        writer.writerow(feedback_list)
    
    return response
    