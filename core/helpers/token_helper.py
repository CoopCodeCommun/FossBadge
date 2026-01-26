from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages

class TokenHelper:
    """
    Class for generating tokens
    """
    token_max_age = 3600 * 72 # 3 days

    @staticmethod
    def generate_user_token(user):
        """
        Generate a token based on a user
        """
        User = get_user_model()

        # Create a signer and create a token with it
        signer = TimestampSigner()
        token = urlsafe_base64_encode(signer.sign(f"{user.pk}").encode('utf8'))

        ### VERIFICATION SIGNATURE AVANT D'ENVOYER
        user_pk = signer.unsign(urlsafe_base64_decode(token).decode('utf8'), max_age=TokenHelper.token_max_age)
        designed_user = User.objects.get(pk=user_pk)
        assert user == designed_user

        return token

    @staticmethod
    def unsign_user_token(token):

        User = get_user_model()
        signer = TimestampSigner()

        user_pk = signer.unsign(urlsafe_base64_decode(token).decode('utf8'), max_age=TokenHelper.token_max_age)
        designed_user = User.objects.get(pk=user_pk)

        return user_pk

    @staticmethod
    def is_user_token_valid(token):
        """
        Verify a token based on a user
        """
        User = get_user_model()

        signer = TimestampSigner()
        try:
            user_pk = signer.unsign(urlsafe_base64_decode(token).decode('utf8'), max_age=TokenHelper.token_max_age)
            user = User.objects.get(pk=user_pk)

            return user_pk
        except SignatureExpired:
            return None


    @staticmethod
    def is_token_valid(token, excepted_str):
        """
        Verify a token
        """
        try:
            signer = TimestampSigner()
            token_res = signer.unsign(urlsafe_base64_decode(token).decode('utf8'), max_age=TokenHelper.token_max_age)

            assert token_res == excepted_str

            return True, ""
        except SignatureExpired:
            return False, "Le token est expiré"
        except AssertionError:
            return False, "Pas de correspondance"