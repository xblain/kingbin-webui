from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.db import connection
from PIL import Image
import shutil
import time

from django.core.cache import cache

import os
from pathlib import Path

import requests
from django.conf import settings

imagecheck = ['img0','img1','img2','img3','img0_0','img0_1','img0_2','img0_3',]
deleteimages= ['_0','_1','_2','_3','_0_0','_1_0','_2_0','_3_0']

@user_passes_test(lambda u: u.is_staff)
@user_passes_test(lambda u: u.is_active)
def edituser(request, id):
    if id == 128643044843978752:
        return HttpResponseRedirect('/')
    if request.user.is_staff:
        if(request.method=="POST"):
            if request.POST.get("is_active") == 'on':
                is_active = True
            else:
                is_active = False
            if request.POST.get("is_staff") == 'on':
                is_staff = True
            else:
                is_staff = False

            cursor = connection.cursor()

            raw_query = """UPDATE public.discordlogin_discorduser SET is_active={}, is_staff={} WHERE id= {}""".format(is_active,is_staff,id)
            cursor.execute(raw_query)

            response = redirect('/administration/users/#dash')
            return response

        


        cursor = connection.cursor()

        raw_query = """SELECT id, discord_tag, is_active, is_staff FROM public.discordlogin_discorduser WHERE id= {}""".format(id)
        cursor.execute(raw_query)
        rows = cursor.fetchall()
    
    return render(request, "edituser.html",{'data':rows})

@user_passes_test(lambda u: u.is_staff)
@user_passes_test(lambda u: u.is_active)
def editbotuser(request, id):
    if id == 128643044843978752:
        return HttpResponseRedirect('/')
    
    return render(request, "botuser.html")

@user_passes_test(lambda u: u.is_superuser)
@user_passes_test(lambda u: u.is_active)
def edititem(request, id = -1):
    if request.user.is_staff:
        cursor = connection.cursor()

        raw_query = """SELECT * FROM public.discordlogin_itemdb WHERE id = {}""".format(id)
        cursor.execute(raw_query)
        item = cursor.fetchall()

        raw_query = """SELECT id, name FROM public.discordlogin_itemdb
                    ORDER BY id"""
        cursor.execute(raw_query)
        items = cursor.fetchall()

        data={}
        data['item'] = item
        data['items'] = items
        data['message'] = {}
        itemsupdating = []

        for i in data['item']:
            dirname = os.path.dirname(__file__)
            dirname = Path(str(dirname)).parent.absolute()
            filename = os.path.join(dirname, "home/static/assets/homes/items/" + str(id) + "_0.png")
            if os.path.isfile(filename):
                l = i + ("HasImage",)
                itemsupdating.append(l)
            else:
                l = i + ("NoImage",)
                itemsupdating.append(l)

        data['item'] = itemsupdating
    
    if request.user.is_superuser:
        ids = []
        for i in items:
            if i[0] != id:
                ids.append(str(i[0]))
        
        if(request.method=="POST"):
            
            #check if deletebbutton pressed
            if request.POST.get("deleteitem") != None:
                cursor = connection.cursor()
                raw_query = """DELETE FROM public.discordlogin_itemdb WHERE id= %s"""
                cursor.execute(raw_query, ([id]))

                dirname = os.path.dirname(__file__)
                dirname = Path(str(dirname)).parent.absolute()
                for i in deleteimages:
                    filename = os.path.join(dirname, "home/static/assets/homes/items/" + str(id) + i + ".png")
                    os.path.isfile(filename)
                    if os.path.isfile(filename):
                        newname = os.path.join(dirname, "home/static/assets/homes/items/backup/" + str(id) +"_"+ str(i)[3:] +"_" + time.strftime("%Y%m%d-%H%M%S") + ".png")
                        os.rename(filename, newname)
                return HttpResponseRedirect('/administration/')
            #Check if values are valid
            try: 
                int(request.POST.get("id"))
                int(request.POST.get("credits"))
                int(request.POST.get("money"))
                int(request.POST.get("category"))
                int(request.POST.get("sellprice"))
                int(request.POST.get("upgradeamount"))
            except:
                return
            try:
                if int(request.POST.get("limit")) < 0 or int(request.POST.get("limit")) > 2147483647:
                    return
            except:
                
                if request.POST.get("limit") == "":
                    pass
                else:
                    return
            validbehaviours = ["none", "420","FRN","STR","CMP","FSH","UPG","INT","WAL","CRD","FLR","WPN","BCK"]
            if str(request.POST.get("behaviour")) not in validbehaviours:
                return
            
            #Check if values in range
            while int(request.POST.get("id")) not in [-100, -200]:
                print(int(request.POST.get("id")))
                if int(request.POST.get("id")) < 0 or len(request.POST.get("name")) < 3 or int(request.POST.get("credits")) < 0 or int(request.POST.get("money")) < 0 or int(request.POST.get("category")) < -1 or int(request.POST.get("sellprice")) < 0 or int(request.POST.get("upgradeamount")) < -1:
                    return
                break
                
            if int(request.POST.get("id")) > 1000000000 or int(request.POST.get("credits")) > 1000000000000000000 or int(request.POST.get("money")) > 1000000000000000000 or int(request.POST.get("category")) > 1000000000000000000 or int(request.POST.get("sellprice")) > 1000000000000000000 or int(request.POST.get("upgradeamount")) > 1000000000:
                return

            if len(request.POST.get("name")) > 100 or len(request.POST.get("description")) > 300 or len(request.POST.get("emoji")) > 100 or len(request.POST.get("behaviour")) > 3:
                if len(request.POST.get("behaviour")) > 3:

                    if request.POST.get("behaviour") != "none":
                        return
                else:
                    return

            #Check if upgradeto is valid
            li = []
            for i in data["items"]:
                if id != i[0]:
                    li.append(i[0])
            if int(request.POST.get("upgradeto")) not in li:
                return

            #####AFTER VALUES HAVE BEEN VALIDATED#####
            #Same ID, Update Item or new item
            if request.POST.get("id") == str(id) or request.path == "/administration/additem":
                if request.POST.get("forsale") == "on":
                    forsalebool = True
                else:
                    forsalebool = False

                if request.POST.get("tradeable") == "on":
                    tradebool = True
                else:
                    tradebool = False
                
                if request.POST.get("sell") == "on":
                    sellbool = True
                else:
                    sellbool = False
                
                if request.POST.get("upgrade") == "on":
                    upgradebool = True
                else:
                    upgradebool = False

                if request.POST.get("placeable") == "on":
                    placebool = True
                else:
                    placebool = False

                try:
                    limit = int(request.POST.get("limit"))
                except:
                    limit = None

                if request.POST.get("behaviour") == "none":
                    behaviour = None
                else:
                    behaviour = request.POST.get("behaviour")
            
                

                cursor = connection.cursor()
                if request.path == "/administration/additem" or request.path == "/administration/additem/":
                    raw_query = """INSERT INTO public.discordlogin_itemdb(name, description,credits,
                                money,emoji,category,forsale,tradeable,"limit",behaviour,
                                sellable,sellprice,upgradeable,upgradeto,upgradeamount,placeable,reward,
                                storage,storagesecurity, fishitemtype, fishrarity,
                                id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    
                else:
                    raw_query = """UPDATE public.discordlogin_itemdb SET name= %s, description=%s,credits=%s,
                                money=%s,emoji=%s,category=%s,forsale=%s,tradeable=%s,"limit"=%s,behaviour=%s,
                                sellable=%s,sellprice=%s,upgradeable=%s,upgradeto=%s,upgradeamount=%s,placeable=%s,reward=%s,
                                storage=%s, storagesecurity=%s, fishitemtype=%s, fishrarity=%s
                                WHERE id= %s"""
                cursor.execute(raw_query, (request.POST.get("name"),request.POST.get("description"),int(request.POST.get("credits")),int(request.POST.get("money")),
                request.POST.get("emoji"),request.POST.get("category"),forsalebool,tradebool,limit,behaviour,sellbool, int(request.POST.get("sellprice")),upgradebool,
                int(request.POST.get("upgradeto")),int(request.POST.get("upgradeamount")), placebool, request.POST.get("reward"), request.POST.get("storage"), 
                request.POST.get("storagesecurity"), request.POST.get("fishitemtype"), request.POST.get("fishrarity"), request.POST.get("id")))
                for i in request.FILES:
                    if i in imagecheck:
                        print(request.FILES[i])
                        img = Image.open(request.FILES[i])
                        width, height = img.size
                        if width == 194 and height < 720:
                            dirname = os.path.dirname(__file__)
                            dirname = Path(str(dirname)).parent.absolute()
                            filename = os.path.join(dirname, "home/static/assets/homes/items/" + request.POST.get("id") +"_"+ str(i)[3:] + ".png")
                            os.path.isfile(filename)
                            print("does " + request.POST.get("id") +"_"+ str(i)[3:] + ".png file exists? " + str(os.path.isfile(filename))) 
                            if os.path.isfile(filename):
                                newname = os.path.join(dirname, "home/static/assets/homes/items/backup/" + request.POST.get("id") +"_"+ str(i)[3:] +"_" + time.strftime("%Y%m%d-%H%M%S") + ".png")
                                os.rename(filename, newname)
                                img.save(filename, format=None)
                            else:
                                img.save(filename, format=None)
                            


                print("Item Updated, ID Unchanged")
                print(request.POST)

                return HttpResponseRedirect('/administration/#'+request.POST.get("id"))
                


            
            elif request.POST.get("id") in ids:
                print("id is already in use")
                y = list(data['item'][0])
                y[0] = request.POST.get("id")
                y[1] = request.POST.get("name")
                y[2] = request.POST.get("description")
                y[3] = request.POST.get("credits")
                y[4] = request.POST.get("money")
                y[5] = request.POST.get("emoji")
                y[6] = request.POST.get("category")
                if request.POST.get("forsale") == None:
                    y[7] = False
                else:
                    y[7] = True
                print(request.POST.get("tradeable"))
                if request.POST.get("tradeable") == None:
                    y[8] = False
                else:
                    y[8] = True
                y[9] = request.POST.get("limit")
                data['item'][0] = tuple(y)
                data['message']['id'] = 'This ID is already in use!'
            else:
                print("moving item to new id")
                #update file names
                dirname = os.path.dirname(__file__)
                dirname = Path(str(dirname)).parent.absolute()
                folder = os.path.join(dirname, "home/static/assets/homes/items/")
                for filename in os.listdir(folder):
                    if filename.startswith(str(id)+"_"):
                        print(filename)
                        updatedfilename = filename.replace(str(id)+"_",request.POST.get("id")+"_",1)
                        print(updatedfilename)
                        #os.rename(folder+filename, folder+updatedfilename)
                #update database references
                
                


        return render(request, "edititem.html",{'data':data})


@user_passes_test(lambda u: u.is_staff)
@user_passes_test(lambda u: u.is_active)
def botadministration(request: HttpRequest):
    if request.user.is_staff:
        cursor = connection.cursor()
        print(request.POST)
        raw_query = """SELECT id, discord_tag, is_active, last_login, is_staff, is_superuser FROM public.discordlogin_discorduser
        ORDER BY is_superuser DESC, is_staff DESC, is_active DESC, last_login DESC """
        cursor.execute(raw_query)
        rows = cursor.fetchall()
        raw_query = 'SELECT id, name, credits, money, emoji, category, forsale, tradeable,sellable,sellprice, upgradeable, upgradeto, "limit", behaviour, placeable  FROM public.discordlogin_itemdb '
        if request.POST.get("sortname"):
            raw_query = raw_query+"ORDER BY name ASC,id ASC  "
        elif request.POST.get("sortcredits"):
            raw_query = raw_query+"ORDER BY credits ASC,id ASC  "

        elif request.POST.get("sortmoney"):
            raw_query = raw_query+"ORDER BY money ASC,id ASC  "

        elif request.POST.get("sortcategory"):
            raw_query = raw_query+"ORDER BY category ASC,id ASC  "

        elif request.POST.get("sortsale"):
            raw_query = raw_query+"ORDER BY forsale DESC,id ASC  "

        elif request.POST.get("sorttrade"):
            raw_query = raw_query+"ORDER BY tradeable DESC,id ASC  "

        elif request.POST.get("sortsell"):
            raw_query = raw_query+"ORDER BY sellable DESC,sellprice ASC,id ASC  "

        elif request.POST.get("sortupgrade"):
            raw_query = raw_query+"ORDER BY upgradeable DESC,upgradeto ASC,id ASC  "

        elif request.POST.get("sortlimit"):
            raw_query = raw_query+'ORDER BY "limit" ASC,id ASC  '

        elif request.POST.get("sortbehaviour"):
            raw_query = raw_query+ "ORDER BY behaviour ASC,id ASC  "

        else:
            raw_query = raw_query+"ORDER BY id ASC  "
        cursor.execute(raw_query)
        items = cursor.fetchall()

        raw_query = """SELECT user_id, registered  FROM public.discord_stats
        ORDER BY user_id ASC  """
        cursor.execute(raw_query)
        botrows = cursor.fetchall()


        data = {}
        data['rows'] = rows
        data['botrows'] = botrows
        data['items'] = items
        itemsupdating = []

        for i in data['items']:
            dirname = os.path.dirname(__file__)
            dirname = Path(str(dirname)).parent.absolute()
            filename = os.path.join(dirname, "home/static/assets/homes/items/" + str(i[0]) + "_0.png")
            if os.path.isfile(filename):
                l = i + ("HasImage",)
                itemsupdating.append(l)
            else:
                l = i + ("NoImage",)
                itemsupdating.append(l)

        data['items'] = itemsupdating
        username = []
        for i in botrows:     
            l = i + (get_user(i[0]),)  
            time.sleep(0.03)
            username.append(l)
        data['botrows'] = username
        return render(request, "botadministration.html",{'data':data})

@user_passes_test(lambda u: u.is_staff)
@user_passes_test(lambda u: u.is_active)
def itemadministration(request: HttpRequest):
    if request.user.is_staff:
        cursor = connection.cursor()
        raw_query = 'SELECT id, name, description, money, credits, emoji, category, forsale, tradeable,sellable,sellprice, upgradeable, upgradeto, "limit", behaviour, placeable, reward, storage  FROM public.discordlogin_itemdb '

        cursor.execute(raw_query)
        items = cursor.fetchall()



        data = {}
        data['items'] = items
        itemsupdating = []

        for i in data['items']:
            dirname = os.path.dirname(__file__)
            dirname = Path(str(dirname)).parent.absolute()
            filename = os.path.join(dirname, "home/static/assets/homes/items/" + str(i[0]) + "_0.png")
            if os.path.isfile(filename):
                l = i + ("HasImage",)
                itemsupdating.append(l)
            else:
                l = i + ("NoImage",)
                itemsupdating.append(l)

        data['items'] = itemsupdating
        print(itemsupdating)
        return render(request, "itemadministration.html",{'data':data})

def get_user(id):
    response = requests.get(f'https://discord.com/api/v8/users/{id}', headers={
        'Authorization': f'Bot {settings.DISCORD_AUTH_KEY}'
    })
    guild = response.json()
    print(guild)
    user = guild['username'] + '#' + guild['discriminator']
    return user