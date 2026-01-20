const input = document.getElementById('mangainput');
const suggestions = document.getElementById('suggestions');
const liked = document.getElementById('liked');
const recbox = document.getElementById('recs');
const recbutton = document.getElementById('recbutton');
let controller = null; // for aborting previous requests
let mangadata = {
  'liked': [],
  'disliked': []
}
let fetchingdata = false

let storeddata = localStorage.getItem('mangaData')

input.addEventListener('focus', () => {
  suggestions.classList.add('active');
});


input.addEventListener('blur', () => {
  // Small delay to allow clicking dropdown items
  setTimeout(() => {
    suggestions.classList.remove('active');
  }, 200);
});


async function syncdata(){
  if (storeddata){
    const obj = JSON.parse(storeddata)
    mangadata.liked = obj.liked
    mangadata.disliked = obj.disliked
    for (let i = 0; i<obj.liked.length;i++){
      const mangaid = obj.liked[i]
      const resp = await fetch(`/api/fetchmanga?id=${mangaid}`)
      const data = await resp.json()
      console.log(data.data)
      const manga = data.data
      const title = manga.attributes.title[Object.keys(manga.attributes.title)[0]]
      let coverid = null //manga.relationships[1].id
      for (let i = 0;i< manga.relationships.length;i++){
         if (manga.relationships[i].type == 'cover_art'){

          coverid = manga.relationships[i].id
          break
          }
      }
      const res = await fetch(`api/mangacover?cover=${encodeURIComponent(coverid)}&id=${encodeURIComponent(mangaid)}`)
      const coverdata = await res.json()
      const cover = coverdata.url
      console.log(cover)
      const div = document.createElement('div');
      div.className = 'manga'
      div.innerHTML = `

        <div class="manganame" onclick="">${title}</div>
        <div class="overlay"></div>
        <img src="${cover}" alt="${title}" class="coverthumbnail">
      `;
      div.onclick =  () => {window.open(`https://mangadex.org/title/${mangaid}`,'_blank')}
      liked.appendChild(div);
    };

    }
  
}

syncdata()
let debounceTimeout;

function debounce(func, delay = 300) {
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(func, delay);
}


async function createcard(id,title,coverid){
  const res = await fetch(`api/mangacover?cover=${encodeURIComponent(coverid)}&id=${encodeURIComponent(id)}`)
  const coverdata = await res.json()
  const cover = coverdata.url
  const innerhtml = `

          <div class="manganame">${title}</div>
          <div class="overlay"></div>
          <img src="${cover}" alt="${title}" class="coverthumbnail">
        `;
  return innerhtml

}


async function searchmanga(query){
  if (!query) {
      suggestions.innerHTML = '';
      if (controller) controller.abort();
      return;
    }
  if (query == ''){
    suggestions.innerHTML = '';
    if (controller) controller.abort();
    return;
  }
    // cancel previous fetch if user types quickly
    if (controller) controller.abort();
    controller = new AbortController();

    try {
      const response = await fetch(`/api/mangasearch?title=${encodeURIComponent(query)}&liked=${encodeURIComponent(mangadata.liked)}`);
      const data = await response.json();

      suggestions.innerHTML = '';
      for (manga of data){
        const id = manga.id
        const title = manga.attributes.title.en || Object.values(manga.attributes.title)[0];
        if (mangadata.liked.includes(title)){
        continue
        }
        let coverid = null //manga.relationships[1].id
        for (let i = 0;i< manga.relationships.length;i++){
          if (manga.relationships[i].type == 'cover_art'){

          coverid = manga.relationships[i].id
          break
          }
        }
        const div = document.createElement('div');
        div.className = 'options'
        div.innerHTML = `
            <p>${title}</p>
        `;
        div.onclick = async() => {
          const newdiv = document.createElement('div');
          newdiv.className = 'manga'
          newdiv.innerHTML = await createcard(id,title,coverid)
                  
          newdiv.onclick =  () => {window.open(`https://mangadex.org/title/${id}`,'_blank')}
          liked.appendChild(newdiv)
          mangadata.liked.push(id)
          suggestions.removeChild(div)
          input.value = ''
          if (mangadata.disliked.includes(title)){
          mangadata.disliked = mangadata.disliked.filter(e => e !== title)
        }
          localStorage.setItem('mangaData',JSON.stringify(mangadata))
        };
        suggestions.appendChild(div);
      };

      if (data.length === 0) {
        suggestions.innerHTML = '<div style="padding:8px;color:#777;">No results found</div>';
      }

    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Error fetching MangaDex data:', err);
        suggestions.innerHTML = '';
        if (controller) controller.abort();
        suggestions.classList.remove('active')
      }
    }
}


input.addEventListener('input', async () => {
  const query = input.value.trim();
  debounce(() => searchmanga(query))
});


async function getRecommendations(){
  if (!fetchingdata){
    fetchingdata = true
    recbutton.innerText = 'Fetching ...'
    recbox.innerHTML = ''
    const response = await fetch(`/api/mangarecs?manga=${JSON.stringify(mangadata)}`)
    const data = await response.json()
    console.log(data)
    for (let i = 0;i<data.sortedlist.length;i++){
      const manga = await fetch(`/api/fetchmanga?id=${encodeURIComponent(data.sortedlist[i])}`)
      const mangadata = await manga.json()
      console.log(mangadata)
      let coverid = ''
      for (let i = 0;i< mangadata.data.relationships.length;i++){
         if (mangadata.data.relationships[i].type == 'cover_art'){

          coverid = mangadata.data.relationships[i].id
          break
          }
      }

      const div = document.createElement('div')
      const res = await fetch(`api/mangacover?cover=${encodeURIComponent(coverid)}&id=${encodeURIComponent(data.sortedlist[i])}`)
      const coverdata = await res.json()
      const cover = coverdata.url
      div.className = 'manga'
      const title = mangadata.data.attributes.title[Object.keys(mangadata.data.attributes.title)[0]]
      div.classList.toggle('rec')
      div.innerHTML = `

           <div class="manganame">${title}</div>
          <div class="overlay"></div>
          <img src="${cover}" alt="${title}" class="coverthumbnail">
        `;
      
      div.onclick =  () => {window.open(`https://mangadex.org/title/${encodeURIComponent(data.sortedlist[i])}`,'_blank')}
      recbox.appendChild(div)
    }
    fetchingdata = false
    recbutton.innerText = 'Find Recmendations'
  }
 
}

