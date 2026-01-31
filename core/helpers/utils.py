import os

from django.contrib.auth import get_user_model
from django.urls import reverse
from core.helpers import TokenHelper
from django.conf import settings

from core.models import Structure
from core.tasks import send_login_mail, send_invite_mail


def get_or_create_user(email, password=None, send_mail=False, set_active=False):
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

def invite_user_to_structure(email, role, structure):
    """
    Invite a user to a structure.
    """
    user = get_or_create_user(email)

    if role in Structure.ROLES[0] :
        structure.admins.add(user)
    elif role in Structure.ROLES[1] :
        structure.editors.add(user)
    elif role in Structure.ROLES[2] :
        structure.users.add(user)

    # New user
    if not user.last_login:
        send_invite_mail.delay(email, role, structure.pk, True)
    # Existing user
    else:
        send_invite_mail.delay(email, role, structure.pk)
