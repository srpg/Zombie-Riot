from urllib.request import urlopen
from core import echo_console

Ver = '1.0.3'

new_version = ('http://cssbestrpg.online/version.txt')

def version_checker(timeout=3):
    with urlopen(new_version, timeout=timeout) as url:
        return url.read().decode('utf-8')

def check_version():
	if version_checker() > Ver:
		echo_console('[Zombie Riot] There is %s version available to download!' % (version_checker()))
		echo_console('[Zombie Riot] You can download new version from: https://github.com/srpg/Zombie-Riot')
		echo_console('[Zombie Riot] You are currently running %s version' % (Ver))
	else:
		echo_console('[Zombie Riot] There is no new version available!')