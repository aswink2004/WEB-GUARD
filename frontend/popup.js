document.addEventListener('DOMContentLoaded', function () {
    let checkButton = document.getElementById('checkSpam');
    let checkSiteButton = document.getElementById('checkSite');

    if (checkButton) {
        checkButton.addEventListener('click', function () {
            let message = document.getElementById('messageInput').value;
            if (message) {
                fetch('http://127.0.0.1:5000/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                })
                .then(response => response.json())
                .then(data => {
                    let result = data.prediction;
                    document.getElementById('result').innerText = `The message is ${result}.`;
                })
                .catch(error => console.error('Error:', error));
            }
        });
    }

    if (checkSiteButton) {
        checkSiteButton.addEventListener('click', () => {
            document.getElementById('status').innerText = 'Loading... Please wait while we analyze the site.';

            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {

                let currentTab = tabs[0];
                let currentUrl = currentTab.url;

                fetch('http://127.0.0.1:5000/check-url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: currentUrl })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        chrome.scripting.executeScript({
                            target: { tabId: currentTab.id },
                            function: highlightSpamSentences,
                            args: [data.spamSentences]
                        });
                        document.getElementById('status').innerText = 'Website analysis complete. Spam content highlighted.';
                    } else {
                        document.getElementById('status').innerText = 'Failed to analyze the website.';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('status').innerText = 'Error occurred while analyzing.';
                });
            });
        });
    }
});

function highlightSpamSentences(spamSentences) {
    spamSentences.forEach(sentence => {
        let regex = new RegExp(`(${sentence})`, 'gi');
        document.body.innerHTML = document.body.innerHTML.replace(regex, '<span style="background-color: red;">$1</span>');
    });
}