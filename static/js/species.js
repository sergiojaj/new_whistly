function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener('DOMContentLoaded', function(){
  var btn = document.getElementById('species-suggest-btn');
  var status = document.getElementById('species-suggest-status');
  var list = document.getElementById('species-suggestions');
  var pictureInput = document.getElementById('id_picture');
  var speciesInput = document.getElementById('id_species');
  if (!btn || !pictureInput || !speciesInput) return;

  var HF_ENABLED = !!(window.HF_ENABLED);
  var POPULAR_SPECIES = [
    'House Sparrow','American Robin','Northern Cardinal','Blue Jay','European Starling',
    'Mourning Dove','Black-capped Chickadee','Mallard','Great Blue Heron','Barn Swallow',
    'Pigeon','Hummingbird','Goldfinch','Magpie','Crow','Raven','Woodpecker','Wren','Warbler'
  ];

  btn.addEventListener('click', function(){
    list.innerHTML = '';
    var file = pictureInput.files && pictureInput.files[0];
    if (!file) { status.textContent = 'Add a photo first to analyze'; return; }

    if (!HF_ENABLED) {
      status.textContent = 'AI suggestions are off. Try these popular species:';
      var ul = document.createElement('ul');
      POPULAR_SPECIES.forEach(function(name){
        var li = document.createElement('li');
        li.textContent = name;
        li.style.cursor = 'pointer';
        li.addEventListener('click', function(){ speciesInput.value = name; });
        ul.appendChild(li);
      });
      list.appendChild(ul);
      return;
    }

    status.textContent = 'Analyzing photo…';
    var form = new FormData();
    form.append('image', file);
    fetch('/api/suggest/species/', {
      method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') }, body: form
    })
    .then(function(r){ if (!r.ok) throw new Error('Request failed'); return r.json(); })
    .then(function(data){
      status.textContent = '';
      if (!data.suggestions || !data.suggestions.length) {
        status.textContent = 'No confident match. Select a popular species below:';
        var ul = document.createElement('ul');
        POPULAR_SPECIES.forEach(function(name){
          var li = document.createElement('li');
          li.textContent = name; li.style.cursor='pointer';
          li.addEventListener('click', function(){ speciesInput.value = name; });
          ul.appendChild(li);
        });
        list.appendChild(ul);
        return;
      }
      var top = data.suggestions[0].label; if (top) speciesInput.value = top;
      var ul = document.createElement('ul');
      data.suggestions.forEach(function(s){
        var li = document.createElement('li');
        var score = s.score ? ' (' + (s.score*100).toFixed(1) + '%)' : '';
        li.textContent = s.label + score;
        li.style.cursor = 'pointer';
        li.addEventListener('click', function(){ speciesInput.value = s.label; });
        ul.appendChild(li);
      });
      list.appendChild(ul);
    })
    .catch(function(){
      status.textContent = 'AI service unreachable. Popular species:';
      var ul = document.createElement('ul');
      POPULAR_SPECIES.forEach(function(name){
        var li = document.createElement('li');
        li.textContent = name; li.style.cursor='pointer';
        li.addEventListener('click', function(){ speciesInput.value = name; });
        ul.appendChild(li);
      });
      list.appendChild(ul);
    });
  });
});
