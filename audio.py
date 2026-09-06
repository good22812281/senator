import customtkinter as ctk
import pygame
import os
from mutagen.mp3 import MP3

pygame.mixer.init()

script_dir = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(script_dir, "music")

all_songs = [f for f in os.listdir(MUSIC_DIR) if f.endswith(".mp3")]
songs = all_songs.copy()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("SenatorAudio")
root.geometry("480x720")
root.resizable(False, False)

search_entry = ctk.CTkEntry(root, placeholder_text="Поиск...", width=440)
search_entry.place(x=10, y=10)

song_list_frame = ctk.CTkScrollableFrame(root, width=440, height=520, fg_color="#1a1a1a")
song_list_frame.place(x=10, y=50)

now_playing_label = ctk.CTkLabel(root, text="Ничего не играет")
now_playing_label.place(x=10, y=580)

progress_bar = ctk.CTkProgressBar(root, width=440)
progress_bar.set(0)
progress_bar.place(x=10, y=605)

paused = False
loop_enabled = False
current_index = None
track_length = 0
start_offset = 0
song_buttons = []

def rebuild_song_list():
    global song_buttons
    for widget in song_list_frame.winfo_children():
        widget.destroy()
    song_buttons = []

    for i, song in enumerate(songs):
        display_text = song
        color = "#1f6aa5" if i == current_index else "transparent"
        b = ctk.CTkButton(
            song_list_frame,
            text=display_text,
            anchor="w",
            fg_color=color,
            hover_color="#2a2a2a",
            command=lambda i=i: play_by_index(i)
        )
        b.pack(fill="x", pady=2, padx=2)
        song_buttons.append(b)

def refresh_highlight():
    for i, b in enumerate(song_buttons):
        if i == current_index:
            name = songs[i]
            b.configure(text=f"▶  {name}", fg_color="#1f6aa5")
        else:
            b.configure(text=songs[i], fg_color="transparent")

def search(event=None):
    global songs
    query = search_entry.get().lower()
    songs = [s for s in all_songs if query in s.lower()]
    rebuild_song_list()
    refresh_highlight()

search_entry.bind("<KeyRelease>", search)

def play_by_index(index):
    global current_index, paused, track_length, start_offset
    if index < 0 or index >= len(songs):
        return
    current_index = index
    song = songs[current_index]
    path = os.path.join(MUSIC_DIR, song)
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(loops=-1 if loop_enabled else 0)
    paused = False
    start_offset = 0
    now_playing_label.configure(text=song)
    track_length = MP3(path).info.length
    refresh_highlight()

def play():
    if current_index is not None:
        play_by_index(current_index)
    elif songs:
        play_by_index(0)

def next_song():
    if current_index is None:
        return
    play_by_index((current_index + 1) % len(songs))

def prev_song():
    if current_index is None:
        return
    play_by_index((current_index - 1) % len(songs))

def toggle_loop():
    global loop_enabled
    loop_enabled = not loop_enabled
    loop_btn.configure(text="loop: on" if loop_enabled else "loop: off")

def toggle_pause():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
        pause_btn.configure(text="pause")
    else:
        pygame.mixer.music.pause()
        paused = True
        pause_btn.configure(text="resume")

def set_volume(value):
    pygame.mixer.music.set_volume(value)

def seek(event):
    global start_offset
    if current_index is None or track_length == 0:
        return
    click_x = event.x
    bar_width = progress_bar.winfo_width()
    percent = click_x / bar_width
    percent = max(0, min(percent, 1))
    new_pos = percent * track_length

    song = songs[current_index]
    path = os.path.join(MUSIC_DIR, song)
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(loops=-1 if loop_enabled else 0, start=new_pos)
    start_offset = new_pos

def update_progress():
    if current_index is not None and track_length > 0 and not paused:
        if not loop_enabled and not pygame.mixer.music.get_busy():
            next_song()
            root.after(500, update_progress)
            return
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms >= 0:
            current_seconds = (start_offset + (pos_ms / 1000)) % track_length
            progress_bar.set(min(current_seconds / track_length, 1))
    root.after(500, update_progress)

rebuild_song_list()
update_progress()

progress_bar.bind("<Button-1>", seek)

btn = ctk.CTkButton(root, text="▶", command=play, width=80)
btn.place(x=10, y=645)

prev_btn = ctk.CTkButton(root, text="⏮", command=prev_song, width=80)
prev_btn.place(x=100, y=645)

next_btn = ctk.CTkButton(root, text="⏭", command=next_song, width=80)
next_btn.place(x=190, y=645)

pause_btn = ctk.CTkButton(root, text="⏹", command=toggle_pause, width=80)
pause_btn.place(x=280, y=645)

loop_btn = ctk.CTkButton(root, text="loop: off", command=toggle_loop, width=80)
loop_btn.place(x=370, y=645)

volume_slider = ctk.CTkSlider(root, from_=0, to=1, command=set_volume, width=430)
volume_slider.set(1)
volume_slider.place(x=15, y=690)

root.mainloop()