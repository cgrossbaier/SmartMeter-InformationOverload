from knapsack.models import *
from django.contrib import admin

class StatAdmin(admin.ModelAdmin):
    search_fields = ['user', 'add', 'created', 'box']
    list_display = ['user', 'add', 'created', 'box']

class RoundAdmin(admin.ModelAdmin):
    search_fields = ['user_group', 'kpOptimal', 'nr']
    list_display = ['user_group', 'kpOptimal', 'nr']


admin.site.register(Box)
admin.site.register(Stat, StatAdmin)
admin.site.register(Round, RoundAdmin)