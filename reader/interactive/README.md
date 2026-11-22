# Thinking in AWS browser practice

Open `index.html` in a browser. Keep all four supporting files in the same directory: `practice.css`, `models.js`, `practice.js`, and the HTML file. No installation, AWS account, network connection, or build step is required. Predictions stay in the page and disappear when you close or reload it.

The three exercises help you follow a request, reason about retries, and compare recovery promises. Predict first, inspect the result, then change one condition. Read the assumptions beside each activity and return to the named chapters for the full explanation.

For a local HTTP preview, run `python3 -m http.server 8764 --bind 127.0.0.1 --directory reader/interactive` from the repository root and open `http://127.0.0.1:8764`. Stop the server with Control-C when finished.

Check the teaching models with `node --test reader/interactive/models.test.cjs` from the repository root. These checks establish model behavior, not AWS behavior or reader comprehension.

The hosted entry point is https://bmozi.net/books/thinking-in-aws. Paperback and Kindle readers use the same activities. Existing GitHub companion paths and edition-pinned links remain supported. The online entry is optional; the files in this folder also work offline.
