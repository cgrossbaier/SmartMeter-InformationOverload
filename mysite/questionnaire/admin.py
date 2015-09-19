from django.contrib import admin
from questionnaire.models import *

class RegUserAdmin(admin.ModelAdmin):
    list_display = ['user_code']
    search_fields = ['user_code']

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 5

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'nr', 'question']

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    search_fields = ['text']

class AnswerAdmin(admin.ModelAdmin):
    search_fields = ['user', 'question', 'answer']
    list_display = ['user', 'question', 'answer']

class UserGroupAdmin(admin.ModelAdmin):
    search_fields = ['user_group']
    list_display = ['user_group']

admin.site.register(RegUser, RegUserAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
