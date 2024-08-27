import sys
import os
import re
import threading
import yt_dlp
from PyQt5 import uic, QtWidgets

# Função para substituir caracteres inválidos no nome do arquivo
def sanitize_filename(url):
    # Remove a parte da URL após o vídeo ID e substitui caracteres inválidos
    filename = re.sub(r'[\/:*?"<>|]', '-', url)
    # Adiciona a extensão .mp4
    return filename + '.mp4'

# Função para baixar vídeos usando yt-dlp
def download_video(url, audio_only, video_only):
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
        'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best' if video_only else 'best'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)  # Extraí informações sem baixar
            formats = info_dict.get('formats', []) + [info_dict]  # Adiciona informações de formatos

            if not formats:
                ui.textEdit.append(f"Erro: Nenhum formato disponível para {url}")
                return

            # Escolha do melhor formato baseado em resolução e qualidade, com proteção contra NoneType
            best_format = max(
                (f for f in formats if f.get('height') is not None and f.get('tbr') is not None),
                key=lambda f: (f.get('height', 0), f.get('tbr', 0)),
                default=None
            )

            if not best_format:
                ui.textEdit.append(f"Erro: Não foi possível determinar o melhor formato para {url}")
                return

            # Configura o formato e nome do arquivo final
            ydl_opts['format'] = best_format['format_id']
            ydl_opts['outtmpl'] = filepath

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        ui.textEdit.append(f"Download concluído para: {url}")
    except Exception as e:
        ui.textEdit.append(f"Erro ao baixar {url}: {e}")

# Função de callback para mostrar progresso
def progress_hook(d):
    if d['status'] == 'finished':
        ui.textEdit.append(f"Concluído: {d['filename']}")

# Função para lidar com o botão de download
def download_button_clicked():
    url = ui.lineEdit.text()
    audio_only = ui.checkBox.isChecked()
    video_only = ui.checkBox_2.isChecked()

    if not url:
        ui.textEdit.append("URL não fornecida.")
        return

    # Rodar o download em uma thread para não travar a interface
    thread = threading.Thread(target=download_video, args=(url, audio_only, video_only))
    thread.start()

# Carregar a interface
app = QtWidgets.QApplication([])
ui = uic.loadUi("G:\\Meu Drive\\felquinhas.py\\yt-dlp\\yt-dlp.ui")

# Conectar o botão de download à função
ui.pushButton.clicked.connect(download_button_clicked)

# Mostrar a interface
ui.show()
sys.exit(app.exec_())
