# Urdu Dub Studio — Workshop Flow

## Roman Urdu

### YouTube link se dubbed video tak

1. **Link dein.** Apni ya ijazat wali English YouTube video ka link browser mein paste karein. Permission box check karein aur **Start dubbing** dabayen. Flask app processing shuru karti hai aur browser mein progress dikhati hai.
2. **Asal audio alag karein.** App video hasil karti hai. FFmpeg video mein pehle se maujood audio track alag nikalta hai.
3. **English speech ko likhein.** Transcription audio mein boli gayi baat ko English text mein badalti hai. Timestamps batate hain ke har hissa kis waqt bola gaya.
4. **Roman Urdu mein tarjuma karein.** App likha hua **English text** Ollama mein chalne wale model ko bhejti hai. Model **Roman Urdu tarjuma** wapas deta hai. Misal ke taur par, “The server is down” se “Server down hai.”
5. **Urdu awaaz banayen.** Text-to-speech Fasih voice se tarjume ko bol kar nayi Urdu audio banata hai.
6. **Audio ko video se milayen.** App nayi awaaz ko video ki timing ke saath jorti hai aur dubbed MP4 banati hai.
7. **Files download karein.** User dubbed MP4 aur timestamps wala Roman Urdu transcript download kar sakta hai. **Download original video** original file ke liye alag option hai.

### Workshop mein bolne ke liye

> User English YouTube link deta hai. FFmpeg asal audio track alag karta hai. App English speech ko likhti hai aur woh text Ollama wale model ko bhejti hai. Model Roman Urdu tarjuma deta hai. Fasih voice us tarjume ki Urdu audio banati hai. App nayi awaaz video ke saath jor kar dubbed MP4 aur Roman Urdu transcript deti hai.

## English

### From a YouTube link to a dubbed video

1. **Submit the link.** Paste the link to an English YouTube video you own or have permission to use. Check the permission box and select **Start dubbing**. The Flask app starts processing and shows progress in the browser.
2. **Extract the original audio.** The app retrieves the video. FFmpeg extracts the audio track already in the video.
3. **Transcribe the English speech.** Transcription converts the spoken words to written English. Timestamps show when each segment was spoken.
4. **Translate into Roman Urdu.** The app sends the **written English text** to the model running in Ollama. The model returns a **Roman Urdu translation**. For example, “The server is down” becomes “Server down hai.”
5. **Generate Urdu speech.** Text-to-speech uses the Fasih voice to turn the translation into new Urdu audio.
6. **Sync the audio to the video.** The app aligns the new voice with the video timing and exports a dubbed MP4.
7. **Download the files.** The user can download the dubbed MP4 and the timestamped Roman Urdu transcript. **Download original video** is a separate option for the original file.

### How to explain it in the workshop

> The user submits an English YouTube link. FFmpeg extracts the original audio track. The app transcribes the English speech and sends the text to the model running in Ollama, which translates it into Roman Urdu. The Fasih voice turns the translation into Urdu speech. The app syncs that speech with the video and provides a dubbed MP4 and a Roman Urdu transcript.
