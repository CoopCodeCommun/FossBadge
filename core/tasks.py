import os

from celery import shared_task
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.helpers import Mailer, TokenHelper
from fossbadge.celery import app
from core.models import User, Structure
import django

#

def generate_login_url(user, base_url=None):
    """
    Generate a login url based on a user and return it
    """
    token = TokenHelper.generate_user_token(user)

    if base_url is None:
        base_url = get_base_url()

    url_path = reverse("core:user-login-from-email")

    connexion_url = f"https://{base_url}{url_path}?token={token}"
    return connexion_url

def get_base_url():
    """
    Return the base url of the application
    """
    base_url = os.environ.get("DOMAIN")
    return base_url

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

    # Create and send the mail
    mail = Mailer(
        'Demande de connexion',
        f'Voici votre lien',
        user.email,
        html_template=template,
        context=context
    )
    mail.send()
    return True

@shared_task
def send_invite_mail(recipient_email, role, structure_pk, new_user=False):
    """
    Send an invitation mail for a structure to an existing user.
    """

    User = get_user_model()
    user = User.objects.get(email=recipient_email)
    structure = Structure.objects.get(pk=structure_pk)

    # Get the tuple corresponding to the role
    role_tuple = [item for item in Structure.ROLES if role in item][0]
    # Generate the structure link
    structure_link = f"https://{get_base_url()}{reverse('core:structure-detail', kwargs={'pk': structure.pk})}"

    # HTML email things
    template = 'emails/structure_invite.html'
    context = {
        'structure': structure,
        'role' : role_tuple[1].lower(),
        'structure_link' : structure_link
    }

    # If it's a new user, we change the template and context
    if new_user:
        template = 'emails/structure_invite_new_user.html'
        context["login_link"] = generate_login_url(user)

    # Create and send the mail
    mail = Mailer(
        f'Invitation dans {structure.name}',
        f'Vous avez été invité dans {structure.name}',
        user.email,
        html_template=template,
        context=context
    )
    mail.send()
    return True