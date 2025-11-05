import mangadex as md
import requests
import json
import time
from mangadex.errors import ApiError
import math
auth = md.Auth()

manga = md.Manga(auth=auth)

tag = md.Tag()
tagids = []
for i in tag.tag_list():
    tagids.append(i.tag_id)
manga_list = manga.get_manga_list() 



def getmangabyname(title):
    id = manga.get_manga_list(title=title)[0].manga_id
    r = requests.get(f'https://api.mangadex.org/manga/{id}?includes[]=cover_art')
    return json.loads(r.text)['data']


#https://api.mangadex.org/manga/${id}?includes[]=cover_art
#r = requests.get(f'https://api.mangadex.org/manga/{id}?includes[]=cover_art')
#data = json.loads(r.text)['data']
#tags = data['attributes']['tags']
#print(data['attributes']['title']['en'])
#for i in tags:
#    if i['id'] in tagids:
#        print(i['attributes']['name']['en'])
def hide():
    tagcount = {

    }

    with open('manga.json','r') as file:
        mangadata = json.load(file)
        for i in mangadata:
            print(i)
            id = manga.get_manga_list(title = i)[0].manga_id
            r = requests.get(f'https://api.mangadex.org/manga/{id}?includes[]=cover_art')
            data = json.loads(r.text)['data']
            tags = data['attributes']['tags']
            for i in tags:
                if i['id'] in tagids:
                    try:
                        tagcount[i['id']] += 1
                    except KeyError:
                        tagcount[i['id']] = 1

    print(tagcount)
    sortedlist = sorted(tagcount,key=tagcount.get,reverse=True)
    print(manga.get_manga_list(includedTags = sortedlist[:6]))


def namelist():
    names = []

    for i in manga_list:
        names.append(i.title)
    return names

#print(namelist())
def normalizetags(tag_weights,global_tag_counts):
    smoothed = {t: math.log(1 + w) for t, w in tag_weights.items()}
    if global_tag_counts:
        adjusted = {}
        for tag, weight in smoothed.items():
            # lower global frequency = higher rarity = higher influence
            rarity = 1 / math.log(2 + global_tag_counts.get(tag, 1))
            adjusted[tag] = weight * rarity
    else:
        adjusted = smoothed

    # --- 3️⃣ Normalize to [0, 1] range ---
    max_val = max(adjusted.values(), default=1)
    normalized = {t: w / max_val for t, w in adjusted.items()}

    return normalized


def cosinesimularity(user_weights,manga_tags):
    print(manga_tags)
    # Dot product: only include tags the manga has
    dot = sum(user_weights.get(tag, 0) for tag in manga_tags)
    # Magnitudes
    mag_user = math.sqrt(sum(w ** 2 for w in user_weights.values()))
    mag_manga = math.sqrt(len(manga_tags))  # number of tags approximates magnitude

    # Cosine similarity
    return dot / (mag_user * mag_manga) if mag_user and mag_manga else 0

def weightedtags():
    tagcount = {
    }
    likedmanga = 0
    with open('manga.json','r') as file:
        mangadata = json.load(file)
        for i in mangadata:
            print(i)
            likedmanga += 1
            id = manga.get_manga_list(title = i)[0].manga_id
            r = requests.get(f'https://api.mangadex.org/manga/{id}?includes[]=cover_art')
            data = json.loads(r.text)['data']
            tags = data['attributes']['tags']
            for i in tags:
                if i['id'] in tagids:
                    try:
                        tagcount[i['id']] += 1
                    except KeyError:
                        tagcount[i['id']] = 1

   
    mangalist={

    }
    globalcount={

    }
    tempcount = {

    }
    for i in tagcount:
        if tagcount[i] > max(1,int(.01* likedmanga)):
            tempcount[i] = tagcount[i]
        else:
            print(tagcount[i], i)
    tagcount = tempcount
    for i in tagcount:
        r = 0
        while True:
            try:
                mangas = manga.get_manga_list(includedTags=[i],limit=100,offset=r)
                try:
                   globalcount[i] += len(mangas)
                except KeyError:
                    globalcount[i] = len(mangas)
                
                if len(mangas) == 0:
                    print('no more mangas in' + str(i))
                    break
                for m in mangas:
                    print(m.title)
                    title = m.title[list(m.title.keys())[0]]
                    try:
                        mangalist[m.manga_id].append(i)
                    except KeyError:
                        mangalist[m.manga_id] = [i]
                r += 100
            except ApiError as e:
                print('api error happened prolly too much in the catagory')
                break
                
    tagcount = normalizetags(tagcount,globalcount)
    mangaweights = {

    }
    for i in mangalist:
        mangaweights[i] = cosinesimularity(tagcount,mangalist[i])

    sortedlist = sorted(mangaweights,key=mangaweights.get,reverse=True)
    with open('mangatags.json','w') as file:
        jsondata = {
            'tagdata':tagcount,
            'globalcount': globalcount,
            'sortedlist':sortedlist,
            'mangadata':mangaweights
    }
        json.dump(jsondata,file,indent=1)
    print(sortedlist)



def getRecs(data):
    tagcache = {}
    with open('mangacache.json','r') as file:
        tagcache = json.load(file)
    tagcount = {
    }
    likedmanga = []
    data = json.loads(data)
    for i in data['liked']:

        id = manga.get_manga_list(title = i)[0].manga_id
        likedmanga.append(id)
        r = requests.get(f'https://api.mangadex.org/manga/{id}?includes[]=cover_art')
        data = json.loads(r.text)['data']
        tags = data['attributes']['tags']
        for i in tags:
            if i['id'] in tagids:
                try:
                    tagcount[i['id']] += 1
                except KeyError:
                    tagcount[i['id']] = 1
    mangalist={

    }
    globalcount={

    }
    
    for i in tagcount:
        r = 0
        try:
            r = len(tagcache[i])
            globalcount[i] = len(tagcache)
            for m in tagcache[i]:
                print(m)
                try:
                    mangalist[m].append(i)
                except KeyError:
                    mangalist[m] = [i]
        except KeyError:
            pass
        while True:
            try:
                mangas = manga.get_manga_list(includedTags=[i],limit=100,offset=r)
                try:
                    globalcount[i] += len(mangas)
                except KeyError:
                    globalcount[i] = len(mangas)
                
                if len(mangas) == 0:
                    print('no more mangas in' + str(i))
                    break
                for m in mangas:
                    print(m.title)
                    try:
                        tagcache[i].append(m.manga_id)
                    except KeyError:
                        tagcache[i] = [m.manga_id]
                    title = m.title[list(m.title.keys())[0]]
                    try:
                        mangalist[m.manga_id].append(i)
                    except KeyError:
                        mangalist[m.manga_id] = [i]
                r += 100
            except ApiError as e:
                print('api error happened prolly too much in the catagory')
                break
    tagcount = normalizetags(tagcount,globalcount)
    mangaweights = {

    }
    for i in mangalist:
        mangaweights[i] = cosinesimularity(tagcount,mangalist[i])

    sortedlist = sorted(mangaweights,key=mangaweights.get,reverse=True)
    recdata = {
        'tagdata':tagcount,
        'globalcount': globalcount,
        'sortedlist':sortedlist,
        'mangadata':mangaweights
    }
    with open('mangacache.json','w') as file:
        json.dump(tagcache,file,indent=1)
    return recdata





