document.addEventListener('DOMContentLoaded', function() {
  chrome.storage.local.get(['lastImageUrl'], function(data) {
    if (!data.lastImageUrl) {
      document.getElementById('loading').innerText = "Right-click an image first!";
      return;
    }

    fetch('http://localhost:5000/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url: data.lastImageUrl })
    })
    .then(response => response.json())
    .then(result => {
      if (result.error) throw new Error(result.error);

      document.getElementById('loading').classList.add('hidden');
      document.getElementById('results').classList.remove('hidden');
      
      document.getElementById('score').innerText = result.confidence_score + "%";
      document.getElementById('ai-prob').innerText = result.ai_likelihood + "%";
      document.getElementById('c2pa').innerText = result.c2pa_status;
      document.getElementById('metadata').innerText = result.metadata_found ? "Found" : "Stripped";
      document.getElementById('verdict').innerText = result.verdict;
      
      // Color coding the verdict
      const v = document.getElementById('verdict');
      if (result.confidence_score < 50) {
        v.style.color = "#dc3545"; // Red
        v.style.backgroundColor = "#f8d7da";
      } else {
        v.style.color = "#28a745"; // Green
        v.style.backgroundColor = "#d4edda";
      }
    })
    .catch(err => {
      document.getElementById('loading').innerText = "Connection Error. Is the Python backend running?";
      console.error(err);
    });
  });
});