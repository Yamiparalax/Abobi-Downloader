import sys
import os
import re
import threading
import yt_dlp
from PyQt5 import uic, QtWidgets
from queue import Queue

# Função para substituir caracteres inválidos no nome do arquivo
def sanitize_filename(url):
    # Remove a parte da URL após o vídeo ID e substitui caracteres inválidos
    filename = re.sub(r'[\/:*?"<>|]', '-', url)
    # Adiciona a extensão .mp4
    return filename + '.mp4'

# Função para baixar vídeos usando yt-dlp
def download_video(url, audio_only, video_only, total_videos, index):
    base_dir = "C:\\Users\\abobi\\Videos"

    if 'tiktok.com' in url:
        save_dir = os.path.join(base_dir, 'Tiktok')
    elif 'youtube.com' in url or 'youtu.be' in url:
        save_dir = os.path.join(base_dir, 'Youtube')
    else:
        ui.textEdit.append(f"URL não suportada: {url}")
        return

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Nome do arquivo baseado na URL
    filename = sanitize_filename(url)
    filepath = os.path.join(save_dir, filename)

    ydl_opts = {
        'outtmpl': filepath,
        'progress_hooks': [progress_hook],
        'format': 'bestaudio' if audio_only else 'bestvideo+bestaudio/best' if video_only else 'best',
        'verbose': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        ui.textEdit.append(f"Downloaded {index} of {total_videos}: {url}")
    except Exception as e:
        ui.textEdit.append(f"Erro ao baixar {url}: {e}")

# Função de callback para mostrar progresso
def progress_hook(d):
    if d['status'] == 'finished':
        ui.textEdit.append(f"Concluído: {d['filename']}")

# Função para lidar com a fila de downloads
def download_queue_worker():
    while not download_queue.empty():
        url, audio_only, video_only = download_queue.get()
        try:
            # Extrair informações sobre a playlist ou vídeo único
            with yt_dlp.YoutubeDL() as ydl:
                info_dict = ydl.extract_info(url, download=False)
                if 'entries' in info_dict:  # É uma playlist
                    total_videos = len(info_dict['entries'])
                    for index, entry in enumerate(info_dict['entries'], start=1):
                        video_url = entry.get('webpage_url', None)
                        if video_url:
                            download_video(video_url, audio_only, video_only, total_videos, index)
                else:  # É um vídeo único
                    download_video(url, audio_only, video_only, 1, 1)

            ui.textEdit.append("All downloads complete.")
        finally:
            download_queue.task_done()

# Função para lidar com o botão de download
def download_button_clicked():
    url = ui.lineEdit.text()
    audio_only = ui.checkBox.isChecked()
    video_only = ui.checkBox_2.isChecked()

    if not url:
        ui.textEdit.append("URL não fornecida.")
        return

    # Adiciona a URL à fila de downloads
    download_queue.put((url, audio_only, video_only))

    # Inicia uma thread para processar a fila de downloads
    if not download_thread.is_alive():
        download_thread.start()

# Carregar a interface
app = QtWidgets.QApplication([])
ui = uic.loadUi("G:\\Meu Drive\\felquinhas.py\\Abobi-Downloader\\yt-dlp.ui")

# Conectar o botão de download à função
ui.pushButton.clicked.connect(download_button_clicked)

# Criar uma fila para os downloads
download_queue = Queue()

# Criar uma thread para processar a fila de downloads
download_thread = threading.Thread(target=download_queue_worker, daemon=True)

# Mostrar a interface
ui.show()
sys.exit(app.exec_())
