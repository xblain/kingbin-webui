from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from discordlogin.models import DiscordUser

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = DiscordUser
        fields = ('id', 'token')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = DiscordUser
        fields = ('id', 'token')