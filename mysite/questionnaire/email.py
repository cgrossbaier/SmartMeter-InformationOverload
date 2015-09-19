from django.template import loader, Context
from django.core.mail import send_mail

from djangoquest import settings

def send_welcome(user):
    return send_questionnaire_email(user, 'welcome_subject.txt', 'welcome.txt')

def send_questionnaire_email(user, template_subject, template_body):

    t = loader.get_template("questionnaire/email/" + template_body)
    s = loader.get_template("questionnaire/email/" + template_subject)
    c = Context({
        'user': user,
        'questionnaire_url': settings.QUESTIONNAIRE_URL,
        'admin_name': settings.ADMINS[0][0],
        'admin_email': settings.ADMINS[0][1]
        })


    try:
        # Send the email (with whitespace-stripped headers) using the rendered templates
        send_mail(s.render(c).rstrip(), t.render(c), settings.ADMINS[0][1],
                  [user.email])
        
    except Exception, inst:
        assert False, str(type(inst)) + " " + str(inst.args) + " " + str(inst)
        assert False, "Error: " + s.render(c) + " --- " + t.render(c) + " --- " + str(user.email) + " --- "
        return False
    
    return True    
    
