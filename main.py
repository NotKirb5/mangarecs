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
global_tag_count = {
    '0234a31e-a729-4e28-9d6a-3f87c4966b9e': 7800,
    '36fd93ea-e8b8-445e-b836-358f02b3d33d': 4746,
    '391b0423-d847-456f-aff0-8b0cfc03066b': 7500,
    '4d32cc48-9f00-4cca-9b5a-a839f0764984': 10000,
    '799c202e-7daa-44eb-9cf7-8a3c0441531e': 3823,
    '87cc87cd-a395-47af-b27a-93258283bbc6': 8400,
    'b13b2a48-c720-44a9-9c77-39c9979373fb': 8118,
    '0bc90acb-ccc1-44ca-a34a-b9f3a73259d0': 3330,
    '423e2eae-a7a2-4a8b-ac03-a8351462d71d': 10000,
    'e197df38-d0e7-43b5-9b09-2842d0c326dd': 10000,
    'e5301a23-ebd9-49dd-a0cb-2add944c7fe9': 8100,
    'f8f62932-27da-4fe4-8ee1-6779a8c5edba': 5436,
    'a3c67850-4684-404e-9b7f-c69850ee5da6': 4900,
    '81c836c9-914a-4eca-981a-560dad663e73': 552,
    'a1f53773-c69a-4ce5-8cab-fffcd90b1565': 5531,
    'cdc58593-87dd-415e-bbc0-2ec27bf404cc': 10000,
    '3de8c75d-8ee3-48ff-98ee-e20a65c86451': 3721,
    '256c8bd9-4904-4360-bf4f-508a76d67183': 5110,
    '33771934-028e-4cb3-8744-691e866a923e': 6124,
    '3b60b75c-a2d7-4860-ab56-05f391bb889c': 6800,
    '51d83883-4103-437c-b4b1-731cb73d786c': 2805,
    '81183756-1453-4c81-aa9e-f6e1b63be016': 958,
    'b1e97889-25b4-4258-b28b-cd7f4d28ea9b': 1410,
    'b9af3a63-f058-46de-a9a0-e0c13906197a': 10000,
    'eabc5b4c-6aff-42f3-b657-3e90cbd00b75': 9800,
    'ee968100-4191-4968-93d3-f82d72be7e46': 6827,
    'f4122d1c-3b44-44d0-9936-ff7502c39ad3': 10000,
    '07251805-a27e-4d59-b488-f0bfbec15168': 3124,
    '92d6d951-ca5e-429c-ac78-451071cbf064': 2783,
    'b29d6a3d-1569-4e7a-8caf-7557bc92cd5d': 3524,
    'da2d50ca-3018-4cc0-ac7a-6b7d472a29ea': 1807,
    '0a39b5a1-b235-4886-a747-1d05d216532d': 1092,
    'caaa44eb-cd40-4177-b930-79d3ef2afe87': 9600,
    'dd1f77c5-dea9-4e2b-97ae-224af09caf99': 1407,
    '2bd2e8d0-f146-434a-9b51-fc9ff2c5fe6a': 1048,
    '39730448-9a5f-48a2-85b0-a70db87b1233': 3207,
    'e64f6742-c834-471d-8d72-dd51fc02b835': 1250,
    '85daba54-a71c-4554-8a28-9901a8b0afad': 1009,
    '5ca48985-9a9d-4bd8-be29-80dc0303db72': 2103,
    'cdad7e68-1419-41dd-bdce-27753074a640': 4513,
    'f42fbf9e-188a-447b-9fdc-f19dc1e4d685': 1157,
    'ace04997-f6bd-436e-b261-779182193d3d': 3884,
    '5fff9cde-849c-4d78-aab0-0d52b2ee1d25': 2628,
    '631ef465-9aba-4afb-b0fc-ea10efe274a8': 485,
    '9467335a-1b83-4497-9231-765337a00b96': 917,
    'd7d1730f-6eb0-4ba6-9437-602cac38664c': 1011,
    'ac72833b-c4e9-4878-b9db-6c8a4a99444a': 2358,
    '320831a8-4026-470b-94f6-8353740e6f04': 251,
    '9438db5a-7e2a-4ac0-b39e-e0d95a34b8a8': 1887,
    '69964a64-2f90-4d33-beeb-f3ed2875eb4c': 3098,
    '3bb26d85-09d5-4d2e-880c-c34b974339e9': 1519,
    '9ab53f92-3eed-4e9b-903a-917c86035ee3': 1603,
    '891cf039-b895-47f0-9229-bef4c96eccd4': 1357,
    '7064a261-a137-4d3a-8848-2d385de3a99c': 578,
    'df33b754-73a3-4c54-80e6-1a74a8058539': 1275,
    'ea2bc92d-1c26-4930-9b7c-d5c0dc1b6869': 1496,
    '5920b825-4181-4a17-beeb-9918b0ff7a30': 9400,
    'fad12b5e-68ba-460e-b933-9ae8318f5b65': 559,
    '489dd859-9b61-4c37-af75-5b18e88daafc': 556,
    'f5ba408b-0e7a-484d-8d49-4e9125ac96de': 10000,
    '50880a9d-5440-4732-9afb-8f457127e836': 1612,
    'b11fda93-8f1d-4bef-b2ed-8803d3733170': 2134,
    '292e862b-2d17-4062-90a2-0356caa4ae27': 1547,
    'c8cbe35b-1b2b-4a3f-9c37-db84c4514856': 609,
    'aafb99c1-7f60-43fa-b75f-fc9502ce29c7': 2653,
    'd14322ac-4d6f-4e9b-afd9-629d5f4d8a41': 872,
    '3e2b8dae-350e-4ab8-a8ce-016e844b9f0d': 10000,
    '97893a4c-12af-4dac-b6be-0dffb353568e': 2259,
    '7b2ce280-79ef-4c09-9b58-12b7c23a9b78': 147,
    '8c86611e-fab7-4986-9dec-d1a2f44acdd5': 339,
    'ddefd648-5140-4e5f-ba18-4eca4071d19b': 302,
    '5bd0e105-4481-44ca-b6e7-7544da56b1a3': 570,
    '2d1f5d56-a1e5-4d0d-a961-2193588b08ec': 465,
    'acc803a4-c95a-4c22-86fc-eb6b582d82a2': 652,
    '65761a2a-415e-47f3-bef2-a9dababba7a6': 599,
    '31932a7e-5b8e-49a6-9f12-2afa39dc544c': 407}
def cachemanga():
    for i in tagids:
        r=0
        attps = 0
        while r<100000:
            time.sleep(0.5)
            try:
                mangas = manga.get_manga_list(includedTags=[i],limit=100,offset=r)
                if len(mangas)==0:
                    print(f'no more mangas in {i}')
                    break
                for m in mangas:
                    metadata = {}
                    
                    if m.manga_id in list(all_manga_descriptions.keys()):
                        print(f'{m.title} is a duplicate')
                        all_manga_descriptions[m.manga_id]['tags'].append(i)
                        continue
                    if len(list(m.description.keys())) == 0:
                        print(f'{m.title} has no description')
                        metadata['description']=''
                    else:
                        desc = m.description[list(m.description.keys())[0]]
                        metadata['description'] = desc
                    metadata['tags'] = [i]
                    metadata['author'] = m.author_id
                    metadata['artist'] = m.artist_id
                    all_manga_descriptions[m.manga_id] = metadata
                    print(f'adding {m.title}')
                r+=100
            except ApiError:
                if attps<10:
                    print(f'dreaded api error, trying again {r} attempt: {attps}')
                    attps += 1
                    time.sleep(1)
                else:
                    print(f'ok apis fucked skipping {i}')
                    break
                    


    descriptions = [all_manga_descriptions[m]['description'] for m in all_manga_descriptions]

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
    authors = {}
    artists = {}
    data = json.loads(data)
    for i in data['liked']:

        id = i
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
        relate = data['relationships']
        for e in relate:
            if e['type'] == 'author':
                try:
                    authors[e['id']] += 1
                except KeyError:
                    authors[e['id']] = 1
            elif e['type'] == 'artist':
                try:
                    artists[e['id']] += 1
                except KeyError:
                    artists[e['id']] = 1

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
    tagcount = normalizetags(tagcount,global_tag_count)
    sortedlist = sorted(tagcount,key=tagcount.get,reverse=True)
    liked_vectors = model.encode(likeddesc, normalize_embeddings=True)
    user_vector = liked_vectors.mean(axis=0)

    scores = cosine_similarity([user_vector],embeddings)[0]

    # keyword shit
    manga_keywords = [extract_keywords(all_manga[m]['description']) for m in all_manga]

    user_keywords = set().union(*[extract_keywords(desc) for desc in likeddesc])

    keyword_scores = []
    for kw in manga_keywords:
        overlap = len(user_keywords & kw)
        union = len(user_keywords | kw)
        jaccard = overlap / union if union else 0
        keyword_scores.append(jaccard)

    tag_scores = []
    manga_ids = list(all_manga.keys())
    for manga_id in manga_ids:
        manga_tags = set(all_manga[manga_id].get('tags', []))  # adjust key name as needed
        user_tags = set(sortedlist[:20])  # use top N tags from user's liked manga
        
        # Calculate tag overlap (you can use Jaccard or weighted sum)
        overlap = len(manga_tags & user_tags)
        union = len(manga_tags | user_tags)
        tag_score = overlap / union if union else 0
        tag_scores.append(tag_score)
    

    # get author and artist 
    
    authorweight = .5
    artistweight = .5

    crativescores = []
    for id,mangadata in all_manga.items():
        mangaauthors = mangadata.get('author',[])
        mangaartists = mangadata.get('artists',[])
        
        authorscore = sum(authors.get(author,0) for author in mangaauthors) * authorweight
        artistscore = sum(artists.get(artist,0) for artist in mangaartists) * artistweight

        crativescores.append(authorscore + artistscore)


    # Combine all three scores
    alpha = 0.65   # semantic similarity weight
    beta = 0.05   # keyword overlap weight
    gamma = 0.20  # tag matching weight
    delta = 0.10
    final_scores = alpha * scores + beta * np.array(keyword_scores) + gamma * np.array(tag_scores) + delta * np.array(crativescores)

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




print(json.load(open('manga_meta.json')))
