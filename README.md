# NoBarriers - Translating Website

This is my (edzhangg)'s final project for CS50x. In NoBarriers :world_map:, users are able to translate to different languages using their voices and using text in order to overcome language barriers.

### How does it work?

Users would have to register before using this website. After registering, users can log in and start translating by using their voice, or typing phrases in.

### Functions of the Website

This website contains a few different parts: an option for users to translate using voice recognition, using text, and seeing the translations that they have saved (under saved translations) or have done in the past (history). *Users would have to allow the site access to their microphones before using the voice translation feature.* Users would be able to save a translation they like after they finished a translation, where a button is found at the bottom of the page. Users would also have an option to clear their saved translations and their history under Privacy Details, as well as changing their passwords.

### Languages Used:
* Python 3
* HTML
* CSS
* JavaScript (embedded in HTML file)

### What did I use to make this?

I used the **Speech Recognition API** (https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition) for JavaScript, as well as the **Flask, SQLite3 and Google Translate** (https://pypi.org/project/googletrans/) Libraries for Python. To put everything together and compile it, I used **Visual Studio Code**.