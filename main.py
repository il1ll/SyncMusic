import os
import re
import time
import json
import signal
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from syncedlyrics import search as search_lyrics
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from pydub.playback import play

CACHE_DIR = Path("song_cache")
CACHE_DIR.mkdir(exist_ok=True)

stop_playback = False

def signal_handler(sig, frame):
    global stop_playback
    print("\n\033[31m[STOP] Playback stopped by user\033[0m")
    stop_playback = True
    sys.exit(0)

def clean_exit():
    print("\n\033[32m[SUCCESS] Playback Finished\033[0m")
    sys.exit(0)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored():
    green = "\033[32m"
    purple = "\033[35m"
    reset = "\033[0m"
    
    clear()
    
    print(f"{green}Music and Lyrics Player - Discord: coder.gg{reset}")
    
    ascii_art = """
 -========== ≫ ──── ≪•◦ ❈ ◦•≫ ──── ≪==========-
 │                                            │
 │  ██████╗ ██████╗ ██████╗ ███████╗██████╗   │
 │ ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗  │
 │ ██║     ██║   ██║██║  ██║█████╗  ██████╔╝  │
 │ ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗  │
 │ ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║  │
 │  ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝  │
 │                                            │
 │                                            │
 ╰─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━─╯
    """
    
    print(f"{purple}{ascii_art}{reset}")

def clean_filename(song_name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", song_name).strip()

def create_song_folder(song_name: str) -> Path:
    safe_name = clean_filename(song_name)
    song_folder = CACHE_DIR / safe_name
    song_folder.mkdir(exist_ok=True)
    return song_folder

def download_song(query: str, output_path: Path) -> Optional[Path]:
    print(f"\033[36m[INFO] Downloading song for query: '{query}'\033[0m")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': str(output_path.with_suffix('')),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(query, download=True)
            actual_path = output_path.with_suffix('.mp3')
            if actual_path.exists():
                print(f"\033[32m[SUCCESS] Download successful: {actual_path}\033[0m")
                return actual_path
            else:
                downloaded_files = list(output_path.parent.glob(f"{output_path.stem}*.mp3"))
                if downloaded_files:
                    downloaded_files[0].rename(actual_path)
                    print(f"\033[32m[SUCCESS] Download successful and renamed: {actual_path}\033[0m")
                    return actual_path
                
            print("\033[31m[ERROR] Could not find the downloaded MP3 file\033[0m")
            return None
    except Exception as e:
        print(f"\033[31m[ERROR] An error occurred during download: {e}\033[0m")
        return None

def fetch_and_save_lrc_lyrics(query: str, lrc_path: Path) -> Optional[str]:
    print(f"\033[36m[INFO] Fetching synchronized lyrics for: '{query}'\033[0m")
    
    lrc_text = search_lyrics(query)
    if not lrc_text:
        print("\033[31m[ERROR] Could not find synchronized lyrics (LRC format)\033[0m")
        return None

    with open(lrc_path, 'w', encoding='utf-8') as f:
        f.write(lrc_text)
    
    print(f"\033[32m[SUCCESS] LRC lyrics saved to: {lrc_path}\033[0m")
    return lrc_text

def process_lyrics_for_playback(lrc_text: str, mp3_path: Path) -> Optional[List[Dict[str, Any]]]:
    lrc_lines = []
    for line in lrc_text.split('\n'):
        match = re.match(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)', line.strip())
        if match:
            minutes, seconds, milliseconds, text = match.groups()
            time_ms = (int(minutes) * 60 + int(seconds)) * 1000 + int(milliseconds.ljust(3, '0')[:3])
            lrc_lines.append({'time_ms': time_ms, 'text': text.strip()})

    if not lrc_lines:
        print("\033[31m[ERROR] Parsed LRC is empty\033[0m")
        return None

    try:
        audio = AudioSegment.from_mp3(mp3_path)
        duration_ms = len(audio)
    except Exception as e:
        print(f"\033[33m[WARNING] Error reading audio duration: {e}\033[0m")
        duration_ms = lrc_lines[-1]['time_ms'] + 5000

    timed_lyrics = []
    for i, line_data in enumerate(lrc_lines):
        start_time = line_data['time_ms']
        text = line_data['text']
        
        if i + 1 < len(lrc_lines):
            end_time = lrc_lines[i+1]['time_ms']
        else:
            end_time = duration_ms
        
        line_duration = end_time - start_time
        
        words = text.split()
        if not words:
            continue

        total_chars = len(text)
        time_per_char = line_duration / total_chars if total_chars > 0 else 0
        
        current_word_start_time = start_time
        word_data = []
        
        for word in words:
            word_len = len(word)
            word_duration = word_len * time_per_char
            word_end_time = current_word_start_time + word_duration
            
            char_data = []
            char_time_per_char = word_duration / word_len if word_len > 0 else 0
            current_char_start_time = current_word_start_time
            
            for char in word:
                char_duration = char_time_per_char
                char_end_time = current_char_start_time + char_duration
                
                char_data.append({
                    'char': char,
                    'start_ms': int(current_char_start_time),
                    'end_ms': int(char_end_time)
                })
                current_char_start_time = char_end_time
            
            word_data.append({
                'word': word,
                'start_ms': int(current_word_start_time),
                'end_ms': int(word_end_time),
                'chars': char_data
            })
            
            current_word_start_time = word_end_time + time_per_char

        timed_lyrics.append({
            'line_text': text,
            'start_ms': start_time,
            'end_ms': end_time,
            'words': word_data
        })

    return timed_lyrics

def load_processed_lyrics(path: Path) -> Optional[List[Dict[str, Any]]]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def play_and_display_lyrics(mp3_path: Path, timed_lyrics: List[Dict[str, Any]]):
    global stop_playback
    stop_playback = False
    
    print("\n\033[36m[INFO] Starting Playback... (Press Ctrl+C to stop)\033[0m")
    
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        audio_duration = len(audio)
    except Exception as e:
        print(f"\033[31m[ERROR] Error loading audio file: {e}\033[0m")
        return

    import threading
    
    def play_audio():
        try:
            play(audio)
        except:
            pass
    
    playback_thread = threading.Thread(target=play_audio)
    playback_thread.daemon = True
    playback_thread.start()
    
    start_time = time.time()
    current_line_index = 0
    
    try:
        while playback_thread.is_alive() and not stop_playback:
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            if elapsed_ms >= audio_duration:
                break
            
            if current_line_index < len(timed_lyrics):
                current_line = timed_lyrics[current_line_index]
                
                if elapsed_ms >= current_line['start_ms']:
                    line_text = current_line['line_text']
                    highlighted_line = ""
                    
                    for word_data in current_line['words']:
                        word = word_data['word']
                        word_start = word_data['start_ms']
                        word_end = word_data['end_ms']
                        
                        if elapsed_ms < word_start:
                            highlighted_line += word + " "
                        elif elapsed_ms >= word_end:
                            highlighted_line += f"\033[32m{word}\033[0m "
                        else:
                            highlighted_word = ""
                            for char_data in word_data['chars']:
                                char = char_data['char']
                                char_start = char_data['start_ms']
                                char_end = char_data['end_ms']
                                
                                if elapsed_ms < char_start:
                                    highlighted_word += char
                                elif elapsed_ms >= char_end:
                                    highlighted_word += f"\033[34m{char}\033[0m"
                                else:
                                    highlighted_word += f"\033[31m{char}\033[0m"
                                    
                            highlighted_line += highlighted_word + " "
                    
                    print(f"\r{highlighted_line.strip()}", end="", flush=True)
                    
                    if elapsed_ms >= current_line['end_ms']:
                        print(f"\r\033[32m{line_text}\033[0m\n", flush=True)
                        current_line_index += 1
                
            time.sleep(0.05)
        
        if not stop_playback:
            clean_exit()
            
    except KeyboardInterrupt:
        stop_playback = True
        print("\n\033[31m[STOP] Playback Stopped\033[0m")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print_colored()
    input("\033[36mPress Enter to continue...\033[0m")
    print_colored()
    
    song_name = input("\033[33mEnter the name of the song to play: \033[0m")
    if not song_name:
        print("\033[31mNo song name provided. Exiting.\033[0m")
        return

    song_folder = create_song_folder(song_name)
    mp3_path = song_folder / f"{clean_filename(song_name)}.mp3"
    lrc_path = song_folder / f"{clean_filename(song_name)}.lrc"
    json_path = song_folder / f"{clean_filename(song_name)}.json"

    timed_lyrics = load_processed_lyrics(json_path)
    
    if mp3_path.exists() and lrc_path.exists() and timed_lyrics:
        print(f"\033[32mFound cached song and synchronized lyrics for '{song_name}'\033[0m")
    else:
        print(f"\033[36mCached files not found or incomplete. Starting download process...\033[0m")
        
        if not mp3_path.exists():
            downloaded_path = download_song(song_name, mp3_path)
            if not downloaded_path:
                print("\033[31mFailed to download song. Cannot proceed.\033[0m")
                return
            mp3_path = downloaded_path
        
        if not lrc_path.exists():
            lrc_text = fetch_and_save_lrc_lyrics(song_name, lrc_path)
            if not lrc_text:
                print("\033[31mFailed to fetch LRC lyrics. Cannot proceed.\033[0m")
                return
        
        if not timed_lyrics:
            with open(lrc_path, 'r', encoding='utf-8') as f:
                lrc_text = f.read()
            timed_lyrics = process_lyrics_for_playback(lrc_text, mp3_path)
            if timed_lyrics:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(timed_lyrics, f, ensure_ascii=False, indent=4)
            else:
                print("\033[31mFailed to process lyrics for playback. Cannot proceed.\033[0m")
                return

    play_and_display_lyrics(mp3_path, timed_lyrics)

if __name__ == "__main__":
    CACHE_DIR.mkdir(exist_ok=True)
    main()
