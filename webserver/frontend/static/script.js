const INPUT_PLACEHOLDER   = 'Enter the track URL or ID';
const SPOTIFY_EMBED_THEME = 1; // 0-black, 1-colorful

const SPOTIFY_EMBED_FORMAT = `<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{track_id}?theme=${SPOTIFY_EMBED_THEME}" width="100%" \
height="90" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>`;

const EMPTY_INPUT_COLOR     = getComputedStyle(document.documentElement).getPropertyValue('--empty-input-color');
const NON_EMPTY_INPUT_COLOR = getComputedStyle(document.documentElement).getPropertyValue('--fg-color');



function url_submit() {
    // Update the status
    document.getElementById('status').innerHTML = 'Exracting track ID...<br>';

    // Get the csrf token
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    // Get the textbox content
    const url = document.getElementById("track-url-input").value;
    console.log(url)
    
    // Make the headers
    const headers = new Headers();
    headers.append('Content-Type', 'application/json');
    headers.append('X-CSRFToken', csrf_token);
    
    // Make the body
    let body = JSON.stringify({ track_url: url });

    // Make the request options
    const req_options = {
        headers: headers,
        body: body,
        method: 'POST',
        credentials: 'same-origin',
        // redirect: 'follow'
    };

    // Send the request
    console.log('Sending request to /api/get_track_id/');
    fetch('/api/get_track_id/', req_options)
        .then(response => response.json())
        .then(data => {
            if (data.status == 200) {
                console.log(data);
                console.log(data.status);
                process_track_id(data.track_id);
            }
            else {
                document.getElementById('status').innerHTML += `<span class="red-fg">(${data.status}) Error extracting track ID: ${data.message}</span><br>`;
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            document.getElementById('status').innerHTML += `<span class="red-fg">Fetch error extracting track ID: ${error}</span><br>`;
        });
}






function process_track_id(track_id) {
    // Update the status
    document.getElementById('status').innerHTML += `Extracted track ID: <span class="green-fg">${track_id}</span><br>`;
    document.getElementById('status').innerHTML += 'Getting similar tracks...<br>'

    // Get the csrf token
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;

    // Make the headers
    const headers = new Headers();
    // headers.append('Content-Type', 'application/json');
    headers.append('X-CSRFToken', csrf_token);

    // Make the body
    let body = JSON.stringify({ track_id: track_id });

    // Make the request options
    const req_options = {
        headers: headers,
        body: body,
        method: 'POST',
        credentials: 'same-origin',
        // redirect: 'follow'
    };

    // Send the request
    console.log('Sending request to /api/get_nearest_tracks/');
    fetch('/api/get_nearest_tracks/', req_options)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            console.log(data.status);
            
            if (data.status == 200) {
                // Delete the status div
                document.getElementById('status').innerHTML = '';
                // Embed the tracks returned by the API
                let html = ''
                for (let i = 0; i < Math.min(10, data.data.length); i++) {
                    html += SPOTIFY_EMBED_FORMAT.replace('{track_id}', data.data[i].track_id);
                }
                document.getElementById('related-tracks').innerHTML = html;
            }
            else {
                document.getElementById('status').innerHTML += `<span class="red-fg">(${data.status}) Error getting similar tracks: ${data.message}</span><br>`;
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            document.getElementById('status').innerHTML += `<span class="red-fg">Fetch error getting similar tracks: ${error}</span><br>`;
        });
}



function on_focus_out_track_url_input() {
    // Get the input value
    const elem = document.getElementById("track-url-input");
    let   val  = elem.value;

    // Change the text if the value is empty
    if (val == '') {
        document.getElementById("track-url-input").value = INPUT_PLACEHOLDER;
    }
    
    // Update val
    val = elem.value;
    // Change the color if the value is our placeholder
    document.getElementById('track-url-input').style.color = val == INPUT_PLACEHOLDER ? EMPTY_INPUT_COLOR : NON_EMPTY_INPUT_COLOR;
}

function on_focus_track_url_input() {
    // Get the input value
    const val = document.getElementById("track-url-input").value;

    // If the value is our placeholder, remove it and change the color
    if (val == INPUT_PLACEHOLDER) {
        document.getElementById("track-url-input").value       = '';
        document.getElementById("track-url-input").style.color = NON_EMPTY_INPUT_COLOR;
    }
}

on_focus_out_track_url_input();

