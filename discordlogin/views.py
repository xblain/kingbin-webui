import os
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from discordlogin.models import DiscordUser
import requests
from django.conf import settings
# Create your views here.
authUrlDiscord = f'https://discord.com/oauth2/authorize?client_id={settings.DISCORD_CLIENT_ID}&response_type=code&redirect_uri={settings.DISCORD_REDIRECT_URI}&scope=identify+guilds'


def home(request: HttpRequest) -> HttpRequest:
    return JsonResponse({'msg': 'Hello World'})

@login_required(login_url='/oauth2/login')
def getAuthenticatedUser(request: HttpRequest):
    user=request.user
    return JsonResponse(
            {'id':user.id,
            'avatar':user.avatar,
            'public_flags':user.public_flags,
            'flags':user.flags,
            'locale':user.locale,
            'mfa_enabled':user.mfa_enabled
            })

def discordLogin(request: HttpRequest):
    return redirect(authUrlDiscord)

def discordLogout(request):
    logout(request)
    return redirect('/')

def  discordLoginRedirect(request: HttpRequest):
    code = request.GET.get('code')
    user = exchange_code(code)
    discordUser = authenticate(request, user=user[0])
    try:
        discordUser = list(discordUser).pop()
    except:
        pass
    try:
        login(request,discordUser)
    except:
        pass
    #return redirect('/auth/user')
    id = str(discordUser).replace('DiscordUser object (', '').replace(')', '')
    t = DiscordUser.objects.get(id=id)
    t.token = str(user[1])  # change field
    t.refreshtoken = str(user[2])  # change field
    t.save() # this will update only'
    return redirect('/')


def exchange_code(code:str):
    data={
        'client_id': settings.DISCORD_CLIENT_ID,
        'client_secret': settings.DISCORD_CLIENT_SECRET,
        'grant_type':'authorization_code',
        'code': code,
        'redirect_uri': settings.DISCORD_REDIRECT_URI,
        'scope': 'identify guild'
    }
    headers={
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response=requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    #print(response)
    credentials = response.json()
    #print(credentials)
    accessToken = credentials['access_token']
    refreshToken = credentials['access_token']
    response = requests.get('https://discord.com/api/v6/users/@me', headers={
        'Authorization': 'Bearer %s' %accessToken
    })
    user = response.json()
    return [user, accessToken, refreshToken]
