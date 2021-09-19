# Zombie-Riot

This plugin is human vs zombies.

In order to win a day, you need to kill all zombies.

This plugin requires <a href="https://forums.sourcepython.com/">Source.Python</a> to load.

This plugin only supports Counter-Strike-Source(Possible other games, but not csgo)

Load Command: sp plugin load zr

Currently have 11Days as max, but you can easyly add more.

# Example of days adding
1. Go inside of _settings.ini file.
2. Make enter inside of file after [11]
3. Add [12] inside of _settings file
4. After added [12] make press enter
5. After you pressed enter add amount = 150 and press enter again
6. After you pressed enter add health = 600 and press enter again
7. After you pressed enter add Model = 'models/player/zh/zh_corpse002.mdl' and press enter again
8. After you pressed enter add speed = 1.30 and press enter again
9. After you pressed enter add dmg = 2 and press enter again
10. After those change in [Days] value = 12
11. Save _settings.ini file after those changes and reload plugin to apply the changes

# How to add admin
1. Go to addons/source-python/plugins/zr/modules/admin/ and you find inside of the folder _admins.ini file
2. Open the _admins.ini file and add your steamid3.
3. Add the steamid3 like this: [U:1:182650578] and save the file
4. After adding steamid3 and save the file, type market in chat and it will show option admin.

# Bug reports

If you find errors or bugs in plugin or suggestion for it, open in github issue.

Github: https://github.com/srpg/Zombie-Riot/issues

# How to add files to download
1. Go inside of css.text file.
2. Add inside of css.txt file materials/models file path

For example like:
  models/player/zh/zh_zombie003.dx80.vtx
  models/player/zh/zh_zombie003.dx90.vtx
  models/player/zh/zh_zombie003.mdl
  models/player/zh/zh_zombie003.phy
  models/player/zh/zh_zombie003.sw.vtx
  models/player/zh/zh_zombie003.vvd

# How to add boss day
1. Go inside of _settings.ini file
2. Go to [boss] section
3. Modify value to the day you want as boss day
4. Modify zombies value to how many zombies should be

Example:
[boss]
	value = 1 # The day of the boss day
	zombies = 2 # The amount of the zombies
