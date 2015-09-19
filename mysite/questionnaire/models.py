from django.db import models
from django.utils import timezone
import datetime

class UserGroup(models.Model):
    user_group = models.IntegerField(u"User group", help_text = u"Determines the user group")
    def __unicode__(self):
        return u'%s' % (self.user_group)

class RegUser(models.Model):
    user_code = models.CharField(u"User code", max_length=200, blank = True, unique = True, help_text = u'User code provided by MTURK to login')
    nr = models.ForeignKey(UserGroup, help_text = u"Determines the experiment group of the user")
    mturk_code = models.CharField(u"Code", max_length=200, help_text = u"Code for the User to put in MTurk", unique = True)
    ip = models.CharField(u"IP", max_length=200, default = u"0", )
    payout = models.FloatField(u"Payout", default=0)
    feedback = models.TextField(max_length=2000, unique=False, blank=True, default='')
    login = models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, 0, 0))
    gameStart = models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, 0, 0))
    gameEnd = models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, 0, 0))
    questionnaireStart = models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, 0, 0))
    questionnaireEnd = models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, 0, 0))
    logout = models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, 0, 0))
    
    class Meta:
        verbose_name = u'User'

    def __unicode__(self):
        return u'%s' % (self.nr)

class Question(models.Model):
    text = models.CharField(u"Question text", max_length=200)
    explanation = models.CharField(u"Explanation", max_length=200, help_text = u"Explains the choices")
    left = models.CharField(u"Left", max_length=200, help_text = u"Explains the left choice")
    right = models.CharField(u"Right", max_length=200, help_text = u"Explains the right choice")
        
    def __unicode__(self):
            return u'%s' % (self.text)

    def get_choices(self):
        choices = Choice.objects.filter(question = self).order_by('nr')
        if len(choices) == 0:
            return []
        return choices

class Choice(models.Model):
    question = models.ForeignKey(Question)
    nr = models.IntegerField(u"Choice number", help_text = u"Determines the order of the choices")
    name = models.CharField(u"Choice text", max_length=200)

    def __unicode__(self):
        return u'%s' % (self.name)

class Answer(models.Model):
    user = models.ForeignKey(RegUser, help_text = u"The user who supplied this answer")
    question = models.ForeignKey(Question, help_text = u"The question that this an answer to")
    answer = models.ForeignKey(Choice, help_text = u"The choice that this an answer to")
    

    def choice_str(self, secondary = False):
        choice_string = ""
        choices = self.question.get_choices()
        split_answers = self.answer.split()

        for choice in choices:
            for split_answer in split_answers:
                if str(split_answer) == str(choice.nr):
                    choice_string += str(choice.name) + " " 
        return choice_string

    def __unicode__(self):
        return u'%s %s %s' % (str(self.user), str(self.question), str(self.answer))



    
