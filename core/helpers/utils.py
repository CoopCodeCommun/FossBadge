import os

from django.contrib.auth import get_user_model
from django.urls import reverse
from core.helpers import TokenHelper
from django.conf import settings

def get_or_create_user(email, password=None, send_mail=False, set_active=False):
    from core.tasks import send_login_mail
    User = get_user_model()
    # TODO check si on laisse ça comme ça pour set le username
    # Si oui il faudrait ne pas afficher les utilisateurs qui n'ont pas mis de prénom
    # Ou meme faire un flag pour que le user puisse choisir si son profile est public ou non
    user, created = User.objects.get_or_create(email=email, username=email)

    if settings.DEBUG and not settings.DEBUG_SEND_EMAIL:
        user.is_active=True
        user.save()
        return user

    if created:
        if password:
            user.set_password(password)

        user.is_active = set_active
        user.save()



    if send_mail:
        # Send an email with celery
        send_login_mail.delay(user.email)


    return user

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