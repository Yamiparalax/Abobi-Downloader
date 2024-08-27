# Abobi Video Downloader

## Description

This Python script uses `yt-dlp` to download videos and audio from sites like TikTok and YouTube. It features a graphical user interface (GUI) built with PyQt5, allowing users to enter URLs, choose between audio or video downloads, and start the download process. The script organizes downloaded files into specific folders based on the type of site.

## Features

- **Video and Audio Download**: Supports downloading both videos and audio from TikTok and YouTube.
- **Automatic Organization**: Downloads are saved in specific folders (`TikTok` or `YouTube`) within the user's video directory.
- **Graphical Interface**: User-friendly interface developed with PyQt5 for easy URL entry and download options.
- **Progress and Logging**: Displays download progress and error messages in the interface.

## Prerequisites

- Python 3.x
- `yt-dlp`
- `PyQt5`

## Installation

1. Clone the repository or download the Python script.
2. Install the required dependencies using pip:

   ```bash
   pip install yt-dlp PyQt5
   ```

3. Ensure the graphical interface file `yt-dlp.ui` is in the same directory as the script or adjust the path in the code.

## Usage

1. Run the Python script:

   ```bash
   python your_script.py
   ```

2. The graphical interface will appear. Enter the URL of the video you want to download in the appropriate field.
3. Choose whether you want to download audio only or video.
4. Click the download button to start the process.
5. Progress and any error messages will be displayed in the text area of the interface.

## Example Code

```python
import sys
import os
import re
import threading
import yt_dlp
from PyQt5 import uic, QtWidgets

def sanitize_filename(url):
    filename = re.sub(r'[\/:*?"<>|]', '-', url)
    return filename + '.mp4'

def download_video(url, audio_only, video_only):
    base_dir = "C:\\Users\\abobi\\Videos"
    if 'tiktok.com' in url:
        save_dir = os.path.join(base_dir, 'Tiktok')
    elif 'youtube.com' in url or 'youtu.be' in url:
        save_dir = os.path.join(base_dir, 'Youtube')
    else:
        ui.textEdit.append(f"Unsupported URL: {url}")
        return

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    filename = sanitize_filename(url)
    filepath = os.path.join(save_dir, filename)

    ydl_opts = {
        'outtmpl': filepath,
        'progress_hooks': [progress_hook],
        'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best' if video_only else 'best'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', []) + [info_dict]
            best_format = max(
                (f for f in formats if f.get('height') is not None and f.get('tbr') is not None),
                key=lambda f: (f.get('height', 0), f.get('tbr', 0)),
                default=None
            )

            if not best_format:
                ui.textEdit.append(f"Error: Could not determine the best format for {url}")
                return

            ydl_opts['format'] = best_format['format_id']
            ydl_opts['outtmpl'] = filepath

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        ui.textEdit.append(f"Download completed for: {url}")
    except Exception as e:
        ui.textEdit.append(f"Error downloading {url}: {e}")

def progress_hook(d):
    if d['status'] == 'finished':
        ui.textEdit.append(f"Finished: {d['filename']}")

def download_button_clicked():
    url = ui.lineEdit.text()
    audio_only = ui.checkBox.isChecked()
    video_only = ui.checkBox_2.isChecked()

    if not url:
        ui.textEdit.append("URL not provided.")
        return

    thread = threading.Thread(target=download_video, args=(url, audio_only, video_only))
    thread.start()

app = QtWidgets.QApplication([])
ui = uic.loadUi("G:\\Meu Drive\\felquinhas.py\\yt-dlp\\yt-dlp.ui")
ui.pushButton.clicked.connect(download_button_clicked)
ui.show()
sys.exit(app.exec_())
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
