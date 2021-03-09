from io import BytesIO
from path import Path
from paths import GAME_PATH
from urllib.request import urlopen
from zipfile import ZipFile
from core import echo_console
from commands.server import ServerCommand

Ver = '1.0.6'
new_version = ('http://cssbestrpg.online/version.txt')
UPDATE_PATH = GAME_PATH

def version_checker(timeout=3):
	with urlopen(new_version, timeout=timeout) as url:
		return url.read().decode('utf-8')

def check_version():
	if version_checker() > Ver:
		echo_console('[Zombie Riot] There is new version available to download!')
		echo_console('[Zombie Riot] Type in console zombie_download to download new version')
	else:
		echo_console('[Zombie Riot] There is no new version available!')

def download(timeout=3):
	with urlopen('https://github.com/srpg/Zombie-Riot/archive/main.zip') as response:
		with ZipFile(BytesIO(response.read())) as zipfile:
			for info in zipfile.infolist():
				filename = info.filename
				path = GAME_PATH / filename.split('/', 1)[1]
				if info.is_dir():
					path.makedirs_p()
				else:
					with open(path, 'wb') as f:
						f.write(zipfile.read(filename))

@ServerCommand('zombie_download')
def zombie_downloadd(command):
	if version_checker() > Ver:
		download()
		echo_console('[Zombie Riot] You have downloaded newest version of the plugin. Restart a server to apply changes')
	else:
		echo_console('[Zombie Riot] There is no new version available to download')
