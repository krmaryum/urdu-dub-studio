# Urdu Dub Studio — Build Walkthrough aur Practice

## Agar koi poochay, app kya karti hai?

“Main ne Urdu Dub Studio project par kaam kiya. User ijazat wali English video ka link deta hai. App video ki speech ko text mein badalti hai, us ka Roman Urdu tarjuma banati hai, aur Pakistani Urdu awaaz ko video ke saath jor deti hai. User dubbed video aur timestamps wala Roman Urdu transcript download kar sakta hai.”

## App ke andar chhotay steps

1. **Link dein.** Browser mein video ka link paste karein aur Start dubbing dabayen. Python ki Flask app processing shuru karti hai aur browser mein progress dikhati hai.
2. **Audio tayyar karein.** App video hasil karti hai aur FFmpeg se audio alag karti hai.
3. **Speech ko text mein badlein.** Transcription English bol-chal ko timestamps ke saath text banati hai. Lambi audio ko chhotay hisson mein process kiya jata hai.
4. **Tarjuma karein.** Local Ollama model English text ko Roman Urdu mein translate karta hai. DNS aur IP address jaise terms ko jahan munasib ho English mein rakhte hain.
5. **Nayi awaaz banayen.** Text-to-speech Fasih voice mein Urdu audio banata hai. App awaaz ko video ke waqt ke saath milati hai.
6. **Export karein.** App dubbed MP4 aur Roman Urdu transcript download ke liye deti hai. Original video download ka bhi alag option hai.

## Hum ne isay kaise chalaya aur release kiya?

1. **Local prototype.** WSL Ubuntu mein Python virtual environment aur FFmpeg ke saath Flask app chalai. Browser mein `http://localhost:8765` par test kiya.
2. **Docker Compose.** App aur Ollama ko services mein rakha. Model setup service translation model download karti hai. Docker volumes models ko agli baar ke liye rakhte hain.
3. **GitHub Actions.** Container checks ne x86-64 aur ARM64 builds check kiye. Release tag push karne par publish workflow ne image GitHub Container Registry par upload ki aur release ke saath `compose.yaml` attach ki.
4. **New-user test.** Alag WSL folder mein release ka Compose file download kiya, published image pull ki aur app chalai. v0.1.1 mein 240-minute default purani .env override hata kar verify kiya.
5. **Test evidence.** 28 minute 24 second ki dub export hui. Audio aur timestamps 10 aur 20 minute ke boundaries se aage chale. Pooray 4 ghantay ki dub ka end-to-end test abhi baqi hai.

## Practice ke sawal

In ke jawab apne alfaaz mein, ek ya do jumlon mein dein.

1. User **Start dubbing** dabata hai to app kya input leti hai aur aakhir mein kya files deti hai?
2. Transcription, translation aur text-to-speech mein kya farq hai?
3. Ollama, Fasih voice aur FFmpeg ka apna apna kaam kya hai?
4. Docker Compose se naye user ka setup kaise asaan hua?
5. GitHub Actions ne image kahan publish ki? Release tag ka kya kaam tha?
6. 240-minute default verify karne aur poori 4-hour dub test karne mein kya farq hai?
