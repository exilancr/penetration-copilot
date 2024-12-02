
function penetrate() {
    console.log("Penetrating...");
    // Get current tab
    browser.tabs.query({ active: true, currentWindow: true })
        .then((tabs) => {
            let tab = tabs[0];
            console.log("Current tab: ", tab);

            fetch('http://localhost:5000/posting/uploadPrepare', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: tab.url,
                }),
            }).then(response => response.json())
                .then(data => {
                    let id = data.id;
                    waitPageLoad(id);
                    uploadContent(id, tab.id);
                })
                .catch(error => {
                    console.error('Error:', error);  // Handle any errors
                });
        });
}


function waitPageLoad(id, iteration = 0) {
    if (iteration > 10) {
        console.error("Too many iterations");
        return;
    }
    fetch('http://localhost:5000/posting/uploadStatus?' + new URLSearchParams({
        id: id
    }), {
        headers: {
            'Content-Type': 'application/json',
        },
        method: 'GET',

    }).then(response => response.json())
        .then(data => {
            console.log('Response:', data);
            if (data.status == "ok") {
                onContentUploaded(id);
            } else if (data.status == "waiting") {
                // Wait for 1 second and try again
                setTimeout(() => {
                    waitPageLoad(id, iteration + 1);
                }, 1000);
            } else {
                throw new Error("Unexpected status: " + data.status);
            }
        })
        .catch(error => {
            console.error('Error:', error);  // Handle any errors
        });
}


function uploadContent(id, tabId) {
    let code =
        `
fetch('http://localhost:5000/posting/upload', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        html: document.documentElement.outerHTML,
        id: '${id}',
        url: document.URL,
    }),
});
`;
    browser.tabs.executeScript(tabId, {
        code: code,
    }).catch((error) => {
        console.error("Error while uploading content: ", error);
    });
}

function onContentUploaded(id) {
    console.log("Content uploaded with ID: ", id);
}


browser.browserAction.onClicked.addListener(penetrate);



