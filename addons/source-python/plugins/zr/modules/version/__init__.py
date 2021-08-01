import urllib
from io import BytesIO
from path import Path
from paths import GAME_PATH
from urllib.request import urlopen
from zipfile import ZipFile
from core import echo_console
from commands.server import ServerCommand
from engines.server import queue_command_string

Ver = '1.5.5'
new_version = ('https://cssbestrpg.online/version.txt')
UPDATE_PATH = GAME_PATH

def version_checker(timeout=3):
	try:
		with urlopen(new_version, timeout=timeout) as url:
			return url.read().decode('utf-8')
	except urllib.error.URLError:
		print('[Zombie Riot] Version checker website is down, you have to check yourself a version at github!')
		return '%s' % (Ver)
        
def check_version():
	if version_checker() > Ver:
		if zr.auto_updater:
			print('[Zombie Riot] Started updating plugin automatically!')
			queue_command_string('zr_update')
		else:
			echo_console('[Zombie Riot] There is new version available to download!\n[Zombie Riot] Type in console zr_update to download new version')
	else:
		echo_console('[Zombie Riot] There is no new version available!')

def download(timeout=3):
	print('[Zombie Riot] Updating progress: 33%')
	print('[Zombie Riot] Started downloading the files!')
	with urlopen('https://github.com/srpg/Zombie-Riot/archive/main.zip') as response:
		print('[Zombie Riot] Updating progress: 66%')
		print('[Zombie Riot] Downloaded the files!')
		with ZipFile(BytesIO(response.read())) as zipfile:
			for info in zipfile.infolist():
				if info.is_dir():
					continue
				filename = info.filename
				path = GAME_PATH / Path(filename.split('/', 1)[1])
				path.dirname().makedirs_p()
				with open(path, 'wb') as f:
					f.write(zipfile.read(filename))
		print('[Zombie Riot] Updating progress: Finished')
		print('[Zombie Riot] Extracted the files!')

@ServerCommand('zr_update')
def zr_update(command):
	if version_checker() > Ver:
		download()
		if zr.auto_updater:
			queue_command_string('sp plugin reload zr')
			print('[Zombie Riot] New version have installed and applyed the changes!')
		else:
			echo_console('[Zombie Riot] Newest version of plugin have downloaded!. Please restart the server for apply changes')
	else:
		echo_console('[Zombie Riot] There is no new version available to download')
