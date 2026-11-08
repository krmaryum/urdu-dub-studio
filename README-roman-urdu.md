# Urdu Dub Studio

English YouTube video ko bol chaal ki Pakistani Urdu mein dub karein aur waqt ke nishanon ke saath Roman Urdu transcript hasil karein. Aap asal video us ki audio ke saath bhi save kar sakte hain. App aap ke computer par chalti hai aur videos aur models download karne ke liye internet istemal karti hai.

[English guide](README.md)

## 1. Docker tayyar karein

- **Windows ya macOS:** Docker Desktop install karein, kholein aur engine start hone ka intezar karein. Windows par apne PC ke processor ke mutabiq installer chunain.
- **Ubuntu:** Docker Engine aur Compose plugin install karein. Terminal khol kar tasdeeq karein ke aap ka account Docker chala sakta hai.

Windows mein PowerShell ya macOS aur Linux mein Terminal kholein. Ye commands aik aik kar ke chalayein:

```text
docker info
docker compose version
```

Agar Docker connect na ho, pehle dekh lein ke Docker Desktop ya Docker service chal rahi hai.

[Docker Desktop ki installation](https://docs.docker.com/desktop/) · [Ubuntu par Docker Engine](https://docs.docker.com/engine/install/ubuntu/)

## 2. Setup ki file save karein

1. [Urdu Dub Studio Releases](https://github.com/krmaryum/urdu-dub-studio/releases) kholein.
2. Latest release ke neeche **Assets** kholein aur **compose.yaml** download karein.
3. Downloads mein **urdu-dub-studio** naam ka folder banayein aur `compose.yaml` us mein rakh dein. File ka naam bilkul yahi rakhein.
4. PowerShell ya Terminal mein folder kholein aur file check karein:

```text
cd ~/Downloads/urdu-dub-studio
docker compose config --quiet
```

Agar browser files kisi aur jagah save karta hai, to us folder ka path istemal karein. Compose file Docker ko batati hai ke kaun si services aur images chalani hain. Check theek ho to koi output nahi aata.

Agar release mein file abhi maujood nahi, to [source se image banane ki hidayaat](docs/container-setup.md) dekhein. Release image **x86-64 aur ARM64** dono ke liye hai.

## 3. App start karein

Usi folder mein ye commands chalayein jahan `compose.yaml` hai:

```text
docker compose up -d
docker compose ps -a
```

Docker tayyar app image download karta hai aur Ollama start karta hai. Pehli baar translation model download hone mein kuch minute lag sakte hain. Jab **app** ke saamne **healthy** nazar aaye, to browser mein [http://localhost:8765](http://localhost:8765) kholein. **model-setup** ke saamne **Exited (0)** ka matlab hai ke setup theek se mukammal ho gaya.

## 4. Pehli video dub karein

1. Kisi chhoti English YouTube video ka link paste karein jise download aur dub karne ki aap ko ijazat ho.
2. Ijazat wala checkbox tick karein aur **Start dubbing** par click karein. Pehli dub par transcription aur voice models download hote hain.
3. Dub tayyar ho to use chala kar dekhein. Phir **Download MP4** aur **Download Roman Urdu transcript** dono save karein. Agla job shuru karne ya app band karne se pehle ye files save kar lein.
4. Koi line theek karni ho to **Review and edit one line** kholein, us ka timestamp chunain aur Roman Urdu badlein. Pehle **Preview edited line** aur phir **Apply to video** par click karein. Updated MP4 aur transcript dobara download karein.

## 5. Asal video save karein

Jis video ko download karne ki ijazat ho, us ka link paste karein, checkbox tick karein aur **Download original video** chunain. Preview tayyar ho to **Download original MP4** par click karein. Is mode mein asal audio rehti hai, video 480p tak download hoti hai, aur chaar ghante tak ki videos li ja sakti hain.

## 6. Lambi video ki dubbing chalu karein

Dubbing ki shuruati limit paanch minute hai. Isay barhane ke liye `compose.yaml` ke saath `.env` naam ki file banayein aur is mein ye line likhein:

```dotenv
URDU_DUB_MAX_MINUTES=15
```

**1 se 240** tak koi poora number istemal karein. Windows par check karein ke file ka naam bilkul `.env` ho. Apni maujooda exports save karein, phir `docker compose up -d` dobara chalayein aur browser refresh kar ke limit check karein. Lambi dubbing mein CPU par kaafi waqt lag sakta hai. Job beech mein ruk jaye to dobara submit karne par shuru se chalegi.

## 7. App band karein aur dobara chalayein

Browser tab band karne se containers chalte rehte hain. Files save karne ke baad app band karni ho to PowerShell ya Terminal mein usi folder mein wapas ja kar ye command chalayein:

```text
docker compose stop
```

Agli baar zaroorat ho to pehle Docker Desktop kholein. Phir usi folder mein ja kar ye command chalayein:

```text
docker compose up -d
```

Browser mein dobara [http://localhost:8765](http://localhost:8765) kholein. Docker download kiye hue models sambhal kar rakhta hai. Update ke liye pehle exports save karein. Phir naye release ki `compose.yaml` ko **usi folder** mein purani file ki jagah rakh dein. Pehle `docker compose pull` aur phir `docker compose up -d` chalayein.

## Mazeed rehnumai

| Guide | Is mein aap ko milega |
| --- | --- |
| [Local setup](docs/local-setup.md) | Ubuntu ya WSL mein Python se app chalane ke steps |
| [Build guide](docs/build-guide.md) | Video import se le kar mukammal dub tak code ki rehnumai |
| [Container setup](docs/container-setup.md) | Source se Docker image banane ke steps |
| [Troubleshooting](docs/troubleshooting.md) | Startup, video import, audio aur editor ke masail ka hal |
| [Release notes](docs/release-notes.md) | Tabdeeliyan aur tests ki surat-e-haal |
| [Docker release publish karein](docs/publish-image.md) | Repo maintain karne wale ke liye image banane aur share karne ke steps |

Ye app aik waqt mein aik user ke liye hai. Dub istemal karne se pehle technical alfaaz aur timing check kar lein.
