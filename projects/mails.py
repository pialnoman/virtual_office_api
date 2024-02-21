from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template import Context, loader


# def send_create_project_email(to_mail, name, project_href, project_detail, pm_mail):
#     try:
#         subject, from_email, to_email = "Project Assigned", EMAIL_HOST_USER, to_mail
#         template = loader.get_template('create_project_mail.html', using='post_office')
#         # context = {"name": name, "href": project_href},
#         context = {"data": {"name": name, "href": project_href, "description": project_detail}}
#         html = template.render(context)
#         print("Printing recipient emails: ", to_email)
#         email_message = EmailMultiAlternatives(subject, html, from_email, [to_email], cc=[pm_mail])
#         email_message.content_subtype = 'html'
#         template.attach_related(email_message)
#         email_message.send()
#     except Exception as e:
#         print('error in sending mail', e)


def send_create_project_email(to_mail, project_detail, pm_mail):
    try:
        subject, from_email, to_email = "Project Assigned", EMAIL_HOST_USER, to_mail
        template = loader.get_template('create_project_mail.html', using='post_office')
        # context = {"name": name, "href": project_href},
        context = {"data": {"name": "Engineers", "href": "currently avoiding", "description": project_detail}}
        html = template.render(context)
        # print("Printing recipient emails: ", to_email)
        email_message = EmailMultiAlternatives(subject, html, from_email, to_email, cc=pm_mail)
        email_message.content_subtype = 'html'
        template.attach_related(email_message)
        email_message.send()
    except Exception as e:
        print('error in sending mail', e)



def send_update_project_email(to_mail,name,project_href):
    try:
        subject, from_email, to_email = "Project Updated", EMAIL_HOST_USER, to_mail
        template = loader.get_template('create_project_mail.html', using='post_office')
        # context = {"name": name, "href": project_href},
        context = {"data": {"name": name, "href": project_href}}
        html = template.render(context)
        email_message = EmailMultiAlternatives(subject, html, from_email, [to_email])
        email_message.content_subtype = 'html'
        template.attach_related(email_message)
        email_message.send()
    except Exception as e:
        print('error in sending mail',e)