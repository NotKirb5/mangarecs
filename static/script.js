const input = document.getElementById('mangainput');
const suggestions = document.getElementById('suggestions');
const liked = document.getElementById('liked');
let controller = null; // for aborting previous requests
let mangadata = {
  'liked': [],
  'disliked': []
}


let storeddata = localStorage.getItem('mangaData')



async function syncdata(){
  if (storeddata){
    const obj = JSON.parse(storeddata)
    mangadata.liked = obj.liked
    mangadata.disliked = obj.disliked
    for (let i = 0; i<obj.liked.length;i++){
      const title = obj.liked[i]
      const resp = await fetch(`/api/singlemanga?title=${obj.liked[i]}`)
      const data = await resp.json()
      console.log(data.data)
      const manga = data.data
      const mangaid = manga.id
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
      div.className = 'mangasuggest'
      div.innerHTML = `

        <div class="manganame">${title}</div>
        <img src="${cover}" alt="${title}" class="coverthumbnail">
      `;
      div.onclick = () => {
        liked.removeChild(div)
        mangadata.liked = mangadata.liked.filter(e => e !== title)
        localStorage.setItem('mangaData',mangadata)
      };
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

async function searchmanga(query){
  if (!query) {
      suggestions.innerHTML = '';
      return;
    }

    // cancel previous fetch if user types quickly
    if (controller) controller.abort();
    controller = new AbortController();

    try {
      const response = await fetch(`/api/mangasearch?title=${encodeURIComponent(query)}`);
      const data = await response.json();
      const results = data.data || [];

      suggestions.innerHTML = '';

      for (manga of results){
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
        const res = await fetch(`api/mangacover?cover=${encodeURIComponent(coverid)}&id=${encodeURIComponent(manga.id)}`)
        const coverdata = await res.json()
        const cover = coverdata.url
        console.log(cover)
        const div = document.createElement('div');
        div.className = 'mangasuggest'
        div.innerHTML = `

          <div class="manganame">${title}</div>
          <img src="${cover}" alt="${title}" class="coverthumbnail">
        `;
        div.onclick = () => {
          const newdiv = document.createElement('div');
          newdiv.className = 'mangasuggest'
          newdiv.innerHTML = `

          <div class="manganame">${title}</div>
          <img src="${cover}" alt="${title}" class="coverthumbnail">
        `;
          liked.appendChild(newdiv)
          mangadata.liked.push(title)
          suggestions.removeChild(div)
          if (mangadata.disliked.includes(title)){
          mangadata.disliked = mangadata.disliked.filter(e => e !== title)
        }
          localStorage.setItem('mangaData',JSON.stringify(mangadata))
        };
        suggestions.appendChild(div);
      };

      if (results.length === 0) {
        suggestions.innerHTML = '<div style="padding:8px;color:#777;">No results found</div>';
      }

    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Error fetching MangaDex data:', err);
      }
    }
}


input.addEventListener('input', async () => {
  const query = input.value.trim();
  debounce(() => searchmanga(query))
});


async function getRecommendations(){
  const response = await fetch(`/api/mangarecs?manga=${JSON.stringify(mangadata)}`)
  const data = await response.json()
  console.log(data)
}

