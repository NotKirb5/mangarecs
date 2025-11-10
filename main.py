import mangadex as md
import requests
import json
import time
from mangadex.errors import ApiError
import math
from sentence_transformers import SentenceTransformer
from numpy import dot
from numpy.linalg import norm
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
model = SentenceTransformer("all-MiniLM-L6-v2")

auth = md.Auth()
manga = md.Manga(auth=auth)
tag = md.Tag()
tagids = []
for i in tag.tag_list():
    tagids.append(i.tag_id)
manga_list = manga.get_manga_list() 

all_manga_descriptions = {

}
def cachemanga():
    for i in tagids:
        r=0
        while r<10000:
            try:
                mangas = manga.get_manga_list(includedTags=[i],limit=100,offset=r)
                if len(mangas)==0:
                    print(f'no more mangas in {i}')
                    break
                for m in mangas:
                    if len(list(m.description.keys())) == 0:
                        print(f'{m.title} has no description')
                        continue
                    elif m.manga_id in list(all_manga_descriptions.keys()):
                        print(f'{m.title} is a duplicate')
                    else:
                        desc = m.description[list(m.description.keys())[0]]
                        all_manga_descriptions[m.manga_id] = desc
                        print(f'adding {m.title}')
                    r+=100
            except ApiError:
                print(f'dreaded api error, trying again')
                time.sleep(1)
                    


    descriptions = [all_manga_descriptions[m] for m in all_manga_descriptions]

    print('embedding')
    embeddings = model.encode(descriptions, normalize_embeddings=True)
    np.save("manga_embeddings.npy", embeddings)
    json.dump(all_manga_descriptions, open("manga_meta.json", "w"))



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

def extract_keywords(text):
    # very basic tokenizer
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return set(words)

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




def bert(data):
    embeddings = np.load("manga_embeddings.npy")
    all_manga = json.load(open("manga_meta.json"))
    likeddesc = []
    likedids = []
    tagcount = {}
    data = json.loads(data)
    for i in data['liked']:

        id = manga.get_manga_list(title = i)[0].manga_id
        likedids.append(id)
        r = requests.get(f'https://api.mangadex.org/manga/{id}?includes[]=cover_art')
        data = json.loads(r.text)['data']
        if len(list(data['attributes']['description'].keys())) != 0:
            print(i,data['attributes']['description'][list(data['attributes']['description'].keys())[0]])
            likeddesc.append(data['attributes']['description'][list(data['attributes']['description'].keys())[0]])
        else:
            print(f'{i} has no description')
        tags = data['attributes']['tags']
        for i in tags:
            if i['id'] in tagids:
                try:
                    tagcount[i['id']] += 1
                except KeyError:
                    tagcount[i['id']] = 1

    #with open('manga.json','r') as f:
    #    mangas = json.load(f)
    #    for i in mangas:
    #        id = manga.get_manga_list(title = i)[0].manga_id
    #        r = requests.get(f'https://api.mangadex.org/manga/{id}?includes[]=cover_art')
    #        data = json.loads(r.text)['data']
    #        if len(list(data['attributes']['description'].keys())) != 0:

    #            print(i,data['attributes']['description'][list(data['attributes']['description'].keys())[0]])
    #            likeddesc.append(data['attributes']['description'][list(data['attributes']['description'].keys())[0]])
    #        else:
    #            print(f'{i} has no description')
    #        tags = data['attributes']['tags']
    #        for i in tags:
    #            if i['id'] in tagids:
    #                try:
    #                    tagcount[i['id']] += 1
    #                except KeyError:
    #                    tagcount[i['id']] = 1

    for i in likedids:
        if i in list(all_manga.keys()):
            index = list(all_manga.keys()).index(i)
            del all_manga[i]
            embeddings = np.delete(embeddings, index, axis=0)
    sortedlist = sorted(tagcount,key=tagcount.get,reverse=True)
    liked_vectors = model.encode(likeddesc, normalize_embeddings=True)
    user_vector = liked_vectors.mean(axis=0)

    scores = cosine_similarity([user_vector],embeddings)[0]

    # keyword shit
    manga_keywords = [extract_keywords(all_manga[m]) for m in all_manga]

    user_keywords = set().union(*[extract_keywords(desc) for desc in likeddesc])

    keyword_scores = []
    for kw in manga_keywords:
        overlap = len(user_keywords & kw)
        union = len(user_keywords | kw)
        jaccard = overlap / union if union else 0
        keyword_scores.append(jaccard)

    alpha = 0.9  # weight for BERT semantic similarity
    beta = 0.1   # weight for keyword overlap

    final_scores = alpha * scores + beta * np.array(keyword_scores)
    top_indices = np.argsort(final_scores)[::-1][:10]
    
    topmanga = []
    for i in top_indices:
        print(str(manga.get_manga_by_id(list(all_manga.keys())[i]).title) + '->' + str(final_scores[i]))
        topmanga.append(list(all_manga.keys())[i])
            
    return {'sortedlist':topmanga}
    #testedmangas = {}
   # for tag in sortedlist[:3]:
   # 
   #     r = 0
   #     while r<10000:
   #         try:
   #             for m in manga.get_manga_list(includedTags = [sortedlist[0]],limit = 100,offset=r):
   #                 if len(m.description.keys()) != 0:

   #                     new_vector = model.encode(m.description[list(m.description.keys())[0]],normalize_embeddings=True)
   #                     user_profile = np.mean(liked_vectors, axis=0)
   #                     user_profile /= np.linalg.norm(user_profile)  # normalize

   #                     # Cosine similarity
   #                     similarity = np.dot(user_profile, new_vector)
   #                     print(f"{m.title[list(m.title.keys())[0]]} Similarity: {similarity:.3f}")
   #                     testedmangas[m.title[list(m.title.keys())[0]]] = similarity
   #                 else:
   #                     print(f'no description for {m.title}')
   #             r+=100
   #         except ApiError:
   #             print(f'api rate limit lol {r}')

   # sortedmangas = sorted(testedmangas,key=testedmangas.get,reverse=True)
    
    #print(sortedmangas[:100])
    #with open('bertdata.json','w') as file:
    #    json.dump({'sorted':sortedlist,'data':testedmangas},file,indent=1)





