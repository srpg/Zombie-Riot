import urllib
from io import BytesIO
from path import Path
from paths import GAME_PATH
from urllib.request import urlopen
from zipfile import ZipFile
from core import echo_console
from commands.server import ServerCommand

Ver = '1.5.2'
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
		echo_console('[Zombie Riot] There is new version available to download!\n[Zombie Riot] Type in console zr_update to download new version')
	else:
		echo_console('[Zombie Riot] There is no new version available!')

def download(timeout=3):
	with urlopen('https://github.com/srpg/Zombie-Riot/archive/main.zip') as response:
		with ZipFile(BytesIO(response.read())) as zipfile:
			for info in zipfile.infolist():
				if info.is_dir():
					continue
				filename = info.filename
				path = GAME_PATH / Path(filename.split('/', 1)[1])
				path.dirname().makedirs_p()
				with open(path, 'wb') as f:
					f.write(zipfile.read(filename))

@ServerCommand('zr_update')
def zr_update(command):
	if version_checker() > Ver:
		download()
		echo_console('[Zombie Riot] Newest version of plugin have downloaded!. Please restart the server for apply changes')
	else:
		echo_console('[Zombie Riot] There is no new version available to download')
