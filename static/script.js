document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/podcasts')
        .then(response => response.json())
        .then(data => {
            const podcastListDiv = document.getElementById('podcast-list');
            if (Object.keys(data).length === 0) {
                podcastListDiv.innerHTML = '<p>No podcasts generated yet. Run main.py and refresh.</p>';
                return;
            }

            for (const category in data) {
                const categoryHeader = document.createElement('h2');
                categoryHeader.className = 'category-header';
                categoryHeader.textContent = category;
                const podcastContainer = document.createElement('div');
                podcastContainer.className = 'podcast-container';

                categoryHeader.addEventListener('click', () => {
                    categoryHeader.classList.toggle('expanded');
                    if (podcastContainer.style.maxHeight) {
                        podcastContainer.style.maxHeight = null;
                    } else {
                        podcastContainer.style.maxHeight = '10000px';
                    }
                });

                podcastListDiv.appendChild(categoryHeader);
                podcastListDiv.appendChild(podcastContainer);

                data[category].forEach(podcast => {
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'podcast-item';
                    itemDiv.innerHTML = `
                        <p class="podcast-title">${podcast.title}</p>
                        <audio controls src="/podcasts/${podcast.category}/${podcast.filename}" id="audio-${podcast.filename}"></audio>
                        <button class="transcript-button">Show Transcript</button>
                        <div class="transcript-container"></div>
                        
                        <div class="voice-changer-box">
                            <label>Change Voice:</label>
                            <select class="voice-select" 
                                    data-category="${podcast.category}" 
                                    data-filename="${podcast.filename}">
                                <option value="female_in" selected>Female (India Accent) - DEFAULT</option>
                                <option value="random">Random Voice Cycle</option>
                                <option value="male_us">Male (US Accent)</option>
                                <option value="female_uk">Female (UK Accent)</option>
                                <option value="male_in">Male (India Accent)</option>
                                <option value="female_au">Female (Australia Accent)</option>
                            </select>
                            <button class="regenerate-button">Listen Right Away</button>
                            <span class="status-message"></span>
                        </div>
                    `;
                    podcastContainer.appendChild(itemDiv);
                });
            }

            addTranscriptEventListeners();
            addRegenerationListeners();

        })
        .catch(error => console.error('Error fetching podcasts:', error));
});

// --- NEW REGENERATION LOGIC (Handles the 'Listen Right Away' button) ---
function addRegenerationListeners() {
    document.querySelectorAll('.podcast-item').forEach(item => {
        const select = item.querySelector('.voice-select');
        const button = item.querySelector('.regenerate-button');
        const audio = item.querySelector('audio');
        const statusSpan = item.querySelector('.status-message');

        button.addEventListener('click', async () => {
            button.disabled = true;
            statusSpan.textContent = "Regenerating audio (may take 10-30s)...";
            statusSpan.style.color = 'yellow';

            const category = select.dataset.category;
            const filename = select.dataset.filename;
            const voiceKey = select.value;

            try {
                const response = await fetch('/api/regenerate_podcast', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        category: category,
                        filename: filename,
                        voice_key: voiceKey
                    })
                });

                const data = await response.json();

                if (data.success) {
                    statusSpan.textContent = "✅ Ready! Playing new version...";
                    statusSpan.style.color = '#28a745';
                    
                    // Force the browser to reload the audio source using a cache-busting timestamp
                    const newSrc = audio.src.split('?')[0] + '?' + new Date().getTime();
                    audio.src = newSrc;
                    
                    // Play the new audio immediately
                    audio.play().catch(e => {
                        console.error("Autoplay failed:", e);
                        statusSpan.textContent = "✅ Ready! Press Play.";
                    });
                } else {
                    statusSpan.textContent = `❌ Error: ${data.error || 'Check server logs.'}`;
                    statusSpan.style.color = 'red';
                }
            } catch (error) {
                statusSpan.textContent = `❌ Network Error. Is server.py running?`;
                statusSpan.style.color = 'red';
                console.error('Regeneration failed:', error);
            } finally {
                button.disabled = false;
                setTimeout(() => statusSpan.textContent = '', 8000); 
            }
        });
    });
}

function addTranscriptEventListeners() {
    document.querySelectorAll('.podcast-item').forEach(item => {
        const button = item.querySelector('.transcript-button');
        const audio = item.querySelector('audio');
        const transcriptContainer = item.querySelector('.transcript-container');
        let words = []; 
        let lastHighlightedIndex = -1;

        button.addEventListener('click', async () => {
            if (transcriptContainer.style.display === 'block') {
                transcriptContainer.style.display = 'none';
                button.textContent = 'Show Transcript';
                return;
            }
            
            const src = audio.getAttribute('src');
            const parts = src.split('/');
            const category = parts[2];
            const filename = parts[3];

            try {
                transcriptContainer.innerHTML = 'Loading transcript...';
                const response = await fetch(`/api/transcript/${category}/${filename}`);
                const data = await response.json();

                if (data.transcript) {
                    const rawWords = data.transcript.match(/\S+/g) || [];

                    words = rawWords.map(word => {
                        const span = document.createElement('span');
                        span.textContent = word + ' ';
                        return span;
                    });
                    
                    transcriptContainer.innerHTML = '';
                    words.forEach(span => transcriptContainer.appendChild(span));
                    
                    transcriptContainer.style.display = 'block';
                    button.textContent = 'Hide Transcript';
                } else {
                     transcriptContainer.innerHTML = data.error || 'Could not load transcript.';
                }

            } catch (error) {
                transcriptContainer.innerHTML = 'Network error loading transcript.';
                console.error('Error fetching transcript:', error);
            }
        });

        audio.addEventListener('timeupdate', () => {
            if (words.length === 0 || !audio.duration || transcriptContainer.style.display !== 'block') return;

            const progress = audio.currentTime / audio.duration;
            const currentIndex = Math.min(Math.floor(progress * words.length), words.length - 1);
            
            if (currentIndex !== lastHighlightedIndex) {
                
                if (lastHighlightedIndex >= 0 && words[lastHighlightedIndex]) {
                    words[lastHighlightedIndex].classList.remove('highlight');
                }
                
                if (currentIndex >= 0 && words[currentIndex]) {
                    words[currentIndex].classList.add('highlight');
                    
                    const containerRect = transcriptContainer.getBoundingClientRect();
                    const wordRect = words[currentIndex].getBoundingClientRect();

                    if (wordRect.top < containerRect.top || wordRect.bottom > containerRect.bottom) {
                        words[currentIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                }
                lastHighlightedIndex = currentIndex;
            }
        });
    });
}
