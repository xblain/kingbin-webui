import requests
import json
import os

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.db import connection
from django.conf import settings




# Create your views here.
def home(request: HttpRequest):
    guild =  get_guilds(request)
    dict={}
    dict['guilds']=str(0)
    dict['users']=str(0)
    for i in range(0,len(guild)):
        dict['guilds'] = int(dict['guilds']) + 1
        print(guild[i])
        dict['users'] = int(dict['users']) + int(get_guild_users(request, int(guild[i]['id'])))
    print(dict)
    return render(request, "home_page.html",{'guild':dict})
    
def get_guilds(request):
    response = requests.get('https://discord.com/api/v6/users/@me/guilds', headers={
        'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'
    })
    guild = response.json()
    return guild

def get_guild_users(request, id):
    cursor = connection.cursor()

    raw_query = """SELECT id, discord_tag, is_active, last_login, is_staff, is_superuser FROM public.discordlogin_discorduser
    ORDER BY is_superuser DESC, is_staff DESC, is_active DESC, last_login DESC """
    cursor.execute(raw_query)
    rows = cursor.fetchall()
    return len(rows)