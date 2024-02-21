from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template import Context, loader


def send_registration_email(to_mail,name):
    try:
        subject, from_email, to_email = "VO Registration", EMAIL_HOST_USER, to_mail
        template = loader.get_template('registration_mail.html', using='post_office')
        # context = {"name": name, "href": project_href},
        context = {"data": {"name": name}}
        html = template.render(context)
        email_message = EmailMultiAlternatives(subject, html, from_email, [to_email])
        email_message.content_subtype = 'html'
        template.attach_related(email_message)
        email_message.send()
    except Exception as e:
        print('error in sending mail',e)