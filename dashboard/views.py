import requests
import json
import asyncio
import os

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from discordlogin.models import DiscordUser
from dashboard.models import DiscordGuild
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings


asyncio.set_event_loop(asyncio.new_event_loop())
# Create your views here.
@login_required(login_url='/oauth2/login')
@user_passes_test(lambda u: u.is_active)
def dashboard(request: HttpRequest):
    guilds = get_guilds(request)
    bguilds = []
    #print(bguilds)
    guildlist = []
    adminlist = {}
    ablelist = []
    disabledlist = []
    #for i in bguilds:
    #    guildlist.append(i['id'])
    for i in get_guildsbot(request):
        bguilds.append(i['id'])
    try:
        for i in guilds:
            if (i['permissions'] & 0x8) and i['id'] in str(bguilds):
                ablelist.append(i)
                checkIfGuildExist(request, i['id'])
            elif (i['permissions'] & 0x8):
                disabledlist.append(i)
    except:
        return redirect('../oauth2/login')

    adminlist['true']=ablelist
    adminlist['false']=disabledlist
    return render(request, "dash.html",{'guilds':adminlist})

    
@login_required(login_url='/oauth2/login')
@user_passes_test(lambda u: u.is_active)
def guilddash(request, id):
    userguilds = get_guilds(request)
    gid = 0
    guilddb = DiscordGuild.objects.get(pk = id)
    auth = False
    for i in userguilds:
        if (i['permissions'] & 0x8) and str(id) == i['id']:
            gid = id
    for i in get_guildsbot(request):
        if str(i['id']) == str(gid):
            checkIfGuildExist(request, i['id'])
            auth = True
            break
    if auth != True:
        return

    guild = get_guilds_detailed(request, id)
    guild['message_channel'] = []
    channels = get_guilds_channels(request, id)


    if(request.method=="POST"):
        if 'generalsave' in request.POST:
            if request.POST.get("localization") == 'NL':
                guilddb.language = 1
            else:
                guilddb.language = 0
            if request.POST.get("bot_enabled") == 'on':
                guilddb.enabled = True
            else:
                guilddb.enabled = False
            if request.POST.get("crib_enabled") == 'on':
                crib_list = []
                guilddb.crib_enabled = True
                for i in request.POST.getlist("crib_list"):
                    for x in channels:
                        if i == x['name']:
                            crib_list.append(x['id'])
                guilddb.crib_list = crib_list
            else:
                guilddb.crib_enabled = False
            if request.POST.get("sauce_enabled") == 'on':
                sauce_list = []
                guilddb.sauce_enabled = True
                for i in request.POST.getlist("sauce_list"):
                    for x in channels:
                        if i == x['name']:
                            sauce_list.append(x['id'])
                guilddb.sauce_list = sauce_list
            else:
                guilddb.sauce_enabled = False
            if request.POST.get("cartel_enabled") == 'on':
                cartel_list = []
                guilddb.cartel_enabled = True
                for i in request.POST.getlist("cartel_list"):
                    for x in channels:
                        if i == x['name']:
                            cartel_list.append(x['id'])
                guilddb.cartel_list = cartel_list
            else:
                guilddb.cartel_enabled = False
        if 'welcomesave' in request.POST:
            if request.POST.get("welcome_enabled") == 'on':
                guilddb.welcome_enabled = True
            else:
                guilddb.welcome_enabled = False
            guilddb.welcome_list = list(str(request.POST.getlist("welcome_list")).replace('\\r\\n', "..@.@.@..")[1:-1].split("..@.@.@.."))
            for i in request.POST.getlist("welcome_channel"):
                for x in channels:
                    if i == x['name']:
                        guilddb.welcome_channel = x['id']
        if 'cartelsave' in request.POST:
            if request.POST.get("attackcommand") == 'attack':
                guilddb.attack_choice = 0
            if request.POST.get("attackcommand") == 'prank':
                guilddb.attack_choice = 1
            guilddb.attack_list = list(str(request.POST.getlist("attack_list")).replace('\\r\\n', "..@.@.@..")[1:-1].split("..@.@.@.."))
        if 'getmessage' in request.POST:
            for x in channels:
                if request.POST.get("message_channel") == x['name']:
                    guilddb.message_channel = x['id']
                    guilddb.message_id = request.POST.get("message_id")
            response = requests.get(f'https://discord.com/api/v6/channels/{guilddb.message_channel}/messages/{guilddb.message_id}', headers={
                'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'
            })
            user = response.json()
            guild['message_id'] = request.POST.get("message_id")
            guild['message_channel'] = request.POST.get("message_channel")
            failed=0
            try:
                guild['embed_description'] = user['embeds'][0]['description']
            except:
                failed=failed+1
                pass
            try:
                guild['embed_title'] = user['embeds'][0]['title']
            except:
                pass
            try:
                guild['embed_image'] = user['embeds'][0]['image']['url']
            except:
                pass
            try:
                guild['embed_footer'] = user['embeds'][0]['footer']['text']
            except:
                pass
            try:
                guild['message_author'] = user['author']['name']
            except:
                failed = failed + 1
                pass
            try:
                guild['message_content'] = user['content']
            except:
                failed=failed+1
                if failed == 2:
                    guild['embed_description'] = "The current channel or message id is wrong."
                    guild['message_content'] = "The current channel or message id is wrong."
                try:
                    guild['message_channel'] = request.POST.get("message_channel")
                except:
                    pass
        if 'sendmessage' in request.POST:
            embed={}
            if request.POST.get("embed_description") != "":
                guild['embed_description'] = request.POST.get("embed_description")
                embed['description'] = guild['embed_description']
            if request.POST.get("embed_title") != "":
                guild['embed_title'] = request.POST.get("embed_title")
                embed['title'] = guild['embed_title']
            if request.POST.get("embed_image") != "":
                guild['embed_image'] = request.POST.get("embed_image")
                embed['image'] = {"url": guild['embed_image']}
            if request.POST.get("embed_footer") != "":
                guild['embed_footer'] = request.POST.get("embed_footer")
                embed['footer'] = {}
                embed['footer']['text'] = guild['embed_footer']
            if request.POST.get("message_content") != "":
                guild['message_content'] = request.POST.get("message_content")
                message_content = guild['message_content']
            else:
                message_content = ' '
            if request.POST.get("message_author") != None:
                guild['message_author'] = request.POST.get("message_author")
                embed['author']={}
                embed['author']['username'] = guild['message_author']
            if request.POST.get("message_channel") != "":
                guild['message_channel'] = request.POST.get("message_channel")


            for x in channels:
                if request.POST.get("message_channel") == x['name']:
                    message_channel = x['id']
                    message_id = request.POST.get("message_id")
                    print(message_channel)
            print(request.POST.get("message_id"))
            if request.POST.get("message_id") and request.POST.get("embed_description") != "":
                guild['message_id'] = request.POST.get("message_id")
                response = requests.patch('https://discord.com/api/v6/channels/'+message_channel+'/messages/'+message_id, headers={'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}, json={
                    "content": message_content,
                    "embed": embed
                })
                user = response.json()
                print(user)
                print('https://discord.com/api/v6/channels/'+message_channel+'/messages/'+message_id)
            elif request.POST.get("message_id") and request.POST.get("embed_description") == "":
                guild['message_id'] = request.POST.get("message_id")
                response = requests.patch('https://discord.com/api/v6/channels/'+message_channel+'/messages/'+message_id, headers={'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}, json={
                    "content": message_content
                })
                user = response.json()
                print(user)
                print('https://discord.com/api/v6/channels/'+message_channel+'/messages/'+message_id)
            elif request.POST.get("embed_description") != "":
                print("dit is de embed:"+request.POST.get("embed_description")+":")
                response = requests.post('https://discord.com/api/v6/channels/'+message_channel+'/messages', headers={'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}, json={
                    "content": message_content,
                    "embed": embed
                })
                user = response.json()
                print(user)
                print('https://discord.com/api/v6/channels/'+message_channel+'/messages')
            else:
                response = requests.post('https://discord.com/api/v6/channels/'+message_channel+'/messages', headers={'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}, json={
                    "content": message_content
                })
                user = response.json()
                print(user)
                print('https://discord.com/api/v6/channels/'+message_channel+'/messages')


        guilddb.save()

    crib_list_names = guilddb.crib_list
    sauce_list_names = guilddb.sauce_list
    cartel_list_names = guilddb.cartel_list
    welcome_channel_name = guilddb.welcome_channel
    try:
        for i in crib_list_names:
            for x in channels:
                if i == x['id']:
                    crib_list_names.append(x['name'])
    except:
        pass
    try:    
        for i in sauce_list_names:
            for x in channels:
                if i == x['id']:
                    sauce_list_names.append(x['name'])
    except:
        pass
    try: 
        for i in cartel_list_names:
            for x in channels:
                if i == x['id']:
                    cartel_list_names.append(x['name'])
    except:
        pass
    try: 
        checked=True
        for x in channels:
            if str(welcome_channel_name) == str(x['id']):
                welcome_channel_name=x['name']
                checked=False
        if checked:
                welcome_channel_name=channels[0]['name']
    except:
        pass
    guild['tchannel'] = {}
    guild['vchannel'] = {}
    guild['crib_list'] = crib_list_names
    guild['crib_enabled']= guilddb.crib_enabled
    guild['sauce_list'] = sauce_list_names
    guild['sauce_enabled']= guilddb.sauce_enabled
    guild['cartel_list'] = cartel_list_names
    guild['cartel_enabled']= guilddb.cartel_enabled
    guild['welcome_channel'] = welcome_channel_name
    guild['welcome_enabled']= guilddb.welcome_enabled
    guild['welcome_list']= "\n".join(guilddb.welcome_list)[1:-1]
    guild['attack_list']="\n".join(guilddb.attack_list)[1:-1]
    guild['attackcommand']=guilddb.attack_choice
    guild['localization'] = guilddb.language
    guild['db'] = guilddb
    for i in channels:
        if i['type'] == 0:
            guild['tchannel'][i['name']]=i['id']
        elif i['type'] == 2:
            guild['vchannel'][i['name']]=i['id']


    return render(request, "guild.html",{'guild':guild})
    

def get_guild(self, guildid, column):
    query = DiscordGuild.objects.get(id=guildid)
    return getattr(query, column)

def checkIfGuildExist(request, guildid):
    obj, created = DiscordGuild.objects.get_or_create(
    id=guildid,
    )

def get_guilds(request):
    t = DiscordUser.objects.get(id=request.user.id)
    response = requests.get('https://discord.com/api/v6/users/@me/guilds', headers={
        'Authorization': 'Bearer %s' %t.token
    })
    user = response.json()
    return user

def get_guildsbot(request):
    response = requests.get('https://discord.com/api/v6/users/@me/guilds', headers={
        'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'
    })
    user = response.json()
    return user
def get_guilds_detailed(request, guildid):
    response = requests.get('https://discord.com/api/v6/guilds/%s' % guildid, headers={
        'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'
    })
    user = response.json()
    return user

def get_guilds_channels(request, guildid):
    response = requests.get('https://discord.com/api/v6/guilds/%s/channels' % guildid, headers={
        'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'
    })
    user = response.json()
    return user
def updateguild(request, id):
   guild = DiscordGuild.objects.get(pk = id)
   guild.enabled = request.POST.get('bot_enabled')
   guild.save()
   return HttpResponse('updated')
