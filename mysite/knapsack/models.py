from django.db import models 
from django.contrib.auth.models import User
from questionnaire.models import *

class Round(models.Model):
    user_group = models.ForeignKey(UserGroup, help_text = u"Determines the experiment group of the user")
    kpOptimal = models.IntegerField()
    delta = models.FloatField(u"Delta", default=0)
    nr = models.IntegerField(u"Round number", help_text = u"Determines the order of the rounds")
    def __unicode__(self):
        return u'User Group =%s Round=%s' % (self.user_group, self.nr)

class Box(models.Model):
    round= models.ForeignKey(Round, help_text = u"Determines Round")
    cost = models.IntegerField()
    benefit = models.IntegerField()
    colour = models.IntegerField()
    
    def __unicode__(self):
        return u'Box c=%s b=%s' % (self.cost, self.benefit)
    
    class Meta:
        verbose_name_plural = "Boxes"

class Stat(models.Model):
    round= models.ForeignKey(Round, help_text = u"Determines")
    add = models.BooleanField()
    full = models.BooleanField(default=False)
    created = models.DateTimeField()
    user = models.ForeignKey(RegUser)
    box = models.ForeignKey(Box)
    payout = models.FloatField()
    
    def __unicode__(self):
            return u'Stat user=%s Round=%s time=%s add=%s' % (self.user, self.round.nr, self.created, self.add)






