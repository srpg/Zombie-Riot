from urllib.request import urlopen

Ver = '1.0.1'

new_version = ('http://cssbestrpg.online/version.txt')

def version_checker(timeout=3):
    with urlopen(new_version, timeout=timeout) as url:
        return url.read().decode('utf-8')