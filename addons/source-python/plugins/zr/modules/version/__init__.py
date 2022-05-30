import urllib
from io import BytesIO
from path import Path
from paths import GAME_PATH
from urllib.request import urlopen
from zipfile import ZipFile
from core import echo_console
from commands.server import ServerCommand
from engines.server import queue_command_string
from zr import zr

Ver = '2.1.2'
UPDATE_PATH = GAME_PATH

def check_version():
	print('[Zombie Riot]: You have to check at github new version, no longer have automatic detect')

def download(timeout=3):
	print('[Zombie Riot] Started downloading the files. Progress 20%')
	with urlopen('https://github.com/srpg/Zombie-Riot/archive/main.zip') as response:
		print('[Zombie Riot] Downloaded the files. Progress 40%')
		extract(response)

def extract(response):
	print('[Zombie Riot] Started extracting the files. Progress 60%')
	with ZipFile(BytesIO(response.read())) as zipfile:
		for info in zipfile.infolist():
			if info.is_dir():
				continue
			filename = info.filename
			path = GAME_PATH / Path(filename.split('/', 1)[1])
			path.dirname().makedirs_p()
			with open(path, 'wb') as f:
				f.write(zipfile.read(filename))
		print('[Zombie Riot] Extracted the files. Progress 80%')
		apply() 
        
def apply():
	print('[Zombie Riot] Auto update finished. Progress 100%')
	if zr.auto_updater:
		queue_command_string('sp plugin reload zr')
	else:
		print('[Zombie Riot] In order to apply the changes please restart the server or reload plugin')

@ServerCommand('zr_update')
def zr_update(command):
	download()
