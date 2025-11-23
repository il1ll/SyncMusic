# SyncMusic
A command‑line music player that downloads songs, fetches synchronized LRC lyrics, processes timing for every word and character, and displays them dynamically during playback.

## ✨ Features
- Automatic YouTube audio download (MP3)
- Fetches synchronized LRC lyrics from multiple sources
- Accurate timing processing for lines, words, and characters
- Real‑time lyric highlighting during playback
- Automatic caching for downloaded audio & lyrics

---

## 📦 Requirements
Install the needed Python libraries:
```bash
pip install yt-dlp
pip install pydub
pip install syncedlyrics
```

### 🔧 FFmpeg is required for audio processing
#### Linux
```bash
sudo apt install ffmpeg
```

#### Windows
Download FFmpeg from the official website:
https://ffmpeg.org/download.html

Then add it to your system PATH.

---

## 📥 Installation
Clone the repository:
```bash
git clone https://github.com/il1ll/SyncMusic.git
```

Enter the directory:
```bash
cd SyncMusic
```

Run the script:
```bash
python main.py
```

---

## 🎵 How It Works
Once the script starts:
1. Enter the song name.
2. The tool will automatically:
   - Create a folder for the song
   - Download the MP3 from YouTube
   - Fetch synchronized LRC lyrics
   - Process the lyrics into JSON with timing
   - Start audio playback with real‑time lyric display

If cached files exist, the tool loads them instantly without downloading again.

---

## 🗂 File Structure
```
song_cache/
  ├── main.py
  └── song_name/
      ├── song.mp3
      ├── song.lrc
      └── song.json   (processed lyric timing)
```

---

## 🤝 Contributing
Feel free to contribute, improve features, or report issues.

---

## © Ownership & Credits
This project is fully owned by [**coder.gg**](https://il1ll.github.io/).

### 📬 Contact & Socials
- **Discord:** [@coder.gg](https://discord.com/users/1099039269391171765)
- **Telegram:** [@codergg](https://t.me/codergg)
- **TikTok:** [@coder.gg](https://tiktok.com/@coder.gg)
