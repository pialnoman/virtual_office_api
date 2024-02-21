from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template import Context, loader


def send_wbs_create_email(to_mail,name, description):
    try:
        subject, from_email, to_email = "New WBS", EMAIL_HOST_USER, to_mail
        template = loader.get_template('wbs_create_mail.html', using='post_office')
        # context = {"name": name, "href": project_href},
        context = {"data": {"name": name, "description": description}}
        html = template.render(context)
        email_message = EmailMultiAlternatives(subject, html, from_email, [to_email])
        email_message.content_subtype = 'html'
        template.attach_related(email_message)
        email_message.send()
    except Exception as e:
        print('error in sending mail', e)
