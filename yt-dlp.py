import yt_dlp
import os


def download_video(url, output_path='C:/Users/abobi/Videos/Youtube'):
    # Ensure the output path exists
    os.makedirs(output_path, exist_ok=True)

    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestvideo[height<=1080][fps<=60]+bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',  # Ensure that the output is in MP4 format
        'noplaylist': True,  # Download only the video, not playlists
        'progress_hooks': [progress_hook]  # Optional: Add a progress hook
    }

    # Download the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} at {d['_speed_str']}")


if __name__ == "__main__":
    # Replace 'your_video_url' with the URL of the video you want to download
    video_url = 'https://youtu.be/RG4qhWr1tA4?si=32m20nxDuUhQ9DSi'
    download_video(video_url)
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import threading
from queue import Queue
from yt_dlp import YoutubeDL

# Função para baixar vídeo com as opções de qualidade
def download_video(url, output_folder, max_resolution='2K'):
    ydl_opts = {
        'format': f'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Worker para rodar os downloads em uma thread separada
class DownloadWorker(QtCore.QThread):
    update_progress = QtCore.pyqtSignal(str)
    
    def __init__(self, url, output_folder, platform, max_resolution):
        super().__init__()
        self.url = url
        self.output_folder = output_folder
        self.platform = platform
        self.max_resolution = max_resolution
    
    def run(self):
        try:
            download_video(self.url, self.output_folder, self.max_resolution)
            self.update_progress.emit(f"Download completed: {self.url}")
        except Exception as e:
            self.update_progress.emit(f"Error downloading {self.url}: {str(e)}")

# Classe da Interface Gráfica
class Ui_MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.queue = Queue()
        self.downloading = False

    def setupUi(self):
        self.setWindowTitle("YouTube & TikTok Downloader")
        self.setGeometry(100, 100, 600, 400)
        
        self.label = QtWidgets.QLabel("Enter URL:", self)
        self.label.setGeometry(20, 20, 100, 30)
        
        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.setGeometry(100, 20, 400, 30)
        
        self.download_button = QtWidgets.QPushButton("Add to Queue", self)
        self.download_button.setGeometry(100, 60, 150, 30)
        self.download_button.clicked.connect(self.add_to_queue)
        
        self.textEdit_log = QtWidgets.QTextEdit(self)
        self.textEdit_log.setGeometry(20, 100, 560, 250)
        
        self.show()

    def log_message(self, message):
        self.textEdit_log.append(message)
        self.textEdit_log.verticalScrollBar().setValue(self.textEdit_log.verticalScrollBar().maximum())

    def add_to_queue(self):
        url = self.url_input.text().strip()
        if not url:
            self.show_error("Please enter a valid URL.")
            return
        
        platform = self.detect_platform(url)
        if platform == "YouTube":
            output_folder = "YouTube"
        elif platform == "TikTok":
            output_folder = "TikTok"
        else:
            self.show_error("Unsupported platform.")
            return
        
        os.makedirs(output_folder, exist_ok=True)
        
        self.queue.put((url, output_folder, platform))
        self.log_message(f"Added to queue: {url}")
        if not self.downloading:
            self.start_download()

    def start_download(self):
        if not self.queue.empty():
            self.downloading = True
            url, output_folder, platform = self.queue.get()
            worker = DownloadWorker(url, output_folder, platform, '2K')
            worker.update_progress.connect(self.log_message)
            worker.finished.connect(self.start_download)
            worker.start()
        else:
            self.downloading = False

    def detect_platform(self, url):
        if "youtube.com" in url or "youtu.be" in url:
            return "YouTube"
        elif "tiktok.com" in url:
            return "TikTok"
        return None

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

# Inicializa o aplicativo
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = Ui_MainWindow()
    sys.exit(app.exec_())
