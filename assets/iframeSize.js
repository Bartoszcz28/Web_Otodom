window.addEventListener('load', () => {
  parent.postMessage({ id: location.port, height: document.body.scrollHeight }, "https://bczarnecki.com")
});