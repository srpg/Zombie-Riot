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

Ver = '2.0.7'
new_version = ('https://cssbestrpg.online/version.txt')
UPDATE_PATH = GAME_PATH

is_online = True

def version_checker(timeout=3):
	global is_online
	try:
		with urlopen(new_version, timeout=timeout) as url:
			is_online = True
			return url.read().decode('utf-8')
	except urllib.error.URLError:
		print('[Zombie Riot] Automatic version checker is offline!. You have to check yourself new version at github!')
		is_online = False
		return '%s' % (Ver)

def check_version():
	global is_online
	if version_checker() > Ver:
		if zr.auto_updater:
			print('[Zombie Riot] Started updating plugin automatically!')
			queue_command_string('zr_update')
		else:
			echo_console('[Zombie Riot] There is new version available to download!\n[Zombie Riot] Type in console zr_update to download new version')
	else:
		if is_online == True:
			echo_console('[Zombie Riot] There is no new version available!')
		else:
			print('[Zombie Riot] Version checking is not available!')

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
	if version_checker() > Ver:
		download()
	else:
		echo_console('[Zombie Riot] There is no new version available to download')
