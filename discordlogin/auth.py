from django.contrib.auth.backends import BaseBackend
from .models import DiscordUser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.hashers import check_password

class SettingsBackend(BaseBackend):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
    """

    def authenticate(self, request, username=None, password=None):
        login_valid = (settings.ADMIN_LOGIN == username)
        pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because only the password from settings.py is checked.
                user = User(username=username)
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class DiscordAuthenticationBackend(BaseBackend):
    def authenticate(self, request, user) -> DiscordUser:
        findUser = DiscordUser.objects.filter(id=user['id'])
        if len(findUser) == 0:
            print('No User Found... Saving..')
            newUser = DiscordUser.objects.createNewDiscordUser(user)
            findUser = DiscordUser.objects.filter(id=user['id'])
        print(findUser)
        return findUser

    def get_user(self, userId):
        try:
            return DiscordUser.objects.get(pk=userId)
        except DiscordUser.DoesNotExist:
            return None