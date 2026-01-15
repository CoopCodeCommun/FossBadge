from celery import shared_task
from django.contrib.auth import get_user_model

from core.helpers import Mailer
from core.helpers.utils import generate_login_url
from fossbadge.celery import app
from core.models import User
import django

#

@shared_task
def send_login_mail(recipient_email):
    """
    Send a login email to a user
    """
    User = get_user_model()
    user = User.objects.get(email=recipient_email)

    # Generate the login url to be sent
    login_link = generate_login_url(user)

    # HTML email things
    template = 'emails/login.html'
    context = {
        'login_link': login_link,
    }

    mail = Mailer(
        'Demande de connexion',
        f'Voici votre lien',
        user.email,
        html_template=template,
        context=context
    )
    mail.send()
    return True
