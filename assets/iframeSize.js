window.addEventListener('message', event => {
  if (event.origin.startsWith('https://bczarnecki.com')) { 
      return document.body.scrollHeight;
  } else {
      return; 
  } 
}); 