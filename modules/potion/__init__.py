from players.entity import Player
from players.helpers import index_from_userid, userid_from_index
from menus import SimpleMenu, SimpleOption, Text
from messages import SayText2
from weapons.manager import weapon_manager
from zr import zr

def potion_market_menu(userid):
	menu = SimpleMenu()
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	player = Player(index_from_userid(userid))
	menu.append(Text('Market\nSection: Potions'))
	menu.append(Text('-' * 30))
	menu.append(SimpleOption(1, 'Full Health[12000$]', 'full_health', player.cash >= 12000 and zr.isAlive(userid), player.cash >= 12000 and zr.isAlive(userid)))
	menu.append(SimpleOption(2, 'Half Health[6000$]', 'half_health', player.cash >= 6000 and zr.isAlive(userid), player.cash >= 6000 and zr.isAlive(userid)))
	menu.append(SimpleOption(3, '25% Of Health[3000$]', '25_health', player.cash >= 3000 and zr.isAlive(userid), player.cash >= 3000 and zr.isAlive(userid)))
	menu.append(SimpleOption(4, 'Full Speed[12000$]', 'full_speed', player.cash >= 12000 and zr.isAlive(userid), player.cash >= 12000 and zr.isAlive(userid)))
	menu.append(SimpleOption(5, 'Half Speed[6000$]', 'half_speed', player.cash >= 6000 and zr.isAlive(userid), player.cash >= 6000 and zr.isAlive(userid)))
	menu.append(SimpleOption(6, '25% Of Speed[3000$]', '25_speed', player.cash >= 3000 and zr.isAlive(userid), player.cash >= 3000 and zr.isAlive(userid)))
	menu.append(SimpleOption(7, 'Full Bullets[16000$]', 'full_bullets', player.cash >= 16000 and zr.isAlive(userid), player.cash >= 16000 and zr.isAlive(userid)))
	menu.append(Text('-' * 30))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = potion_menu_callback
	menu.send(index_from_userid(userid))

def potion_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		player = Player(index_from_userid(userid))
		if choice == 'full_health':
			if zr.isAlive(userid):
				player.health += player.max_health
				player.cash -= 12000
				SayText2('\x04[Zombie Riot] » You have bought full health with 12000$').send(_index)
			else:
				SayText2('\x04[Zombie Riot] » You need to be alive for buy health potion').send(_index)
		elif choice == 'half_health':
			if zr.isAlive(userid):
				bonus = int(player.max_health / 2)
				player.health += bonus
				player.cash -= 6000
				SayText2('\x04[Zombie Riot] » You have bought half health with 6000$').send(_index)
			else:
				SayText2('\x04[Zombie Riot] » You need to be alive for buy health potion').send(_index)
		elif choice == '25_health':
			if zr.isAlive(userid):
				bonus = int(player.max_health / 4)
				player.health += bonus
				player.cash -= 3000
				SayText2('\x04[Zombie Riot] » You have bought 25% health with 3000$').send(_index)
			else:
				SayText2('\x04[Zombie Riot] » You need to be alive for buy health potion').send(_index)
		elif choice == 'full_bullets':
			if zr.isAlive(userid):
				player.cash -= 16000
				weapon = player.active_weapon
				primary = player.primary
				secondary = player.secondary
				max_clip = weapon_manager[weapon.classname].clip
				max_ammo = weapon_manager[weapon.classname].maxammo
				if weapon == primary:
					weapon.clip = max_clip
					weapon.ammo = max_ammo
				elif weapon == secondary:
					weapon.clip = max_clip
					weapon.ammo = max_ammo
				SayText2('\x04[Zombie Riot] » You have bought full bullets with 16000$').send(_index)
			else:
				SayText2('\x04[Zombie Riot] » You need to be alive for buy full bullets').send(_index)
		elif choice == '25_speed':
			if zr.isAlive(userid):
				bonus = player.speed / 4
				player.speed += bonus
				player.cash -= 3000
				SayText2('\x04[Zombie Riot] » You have bought 25% speed with 3000$').send(_index)
			else:
				SayText2('\x04[Zombie Riot] » You need to be alive for buy speed potion').send(_index)
		elif choice == 'half_speed':
			if zr.isAlive(userid):
				bonus = player.speed / 2
				player.speed += bonus
				player.cash -= 6000
				SayText2('\x04[Zombie Riot] » You have bought half speed with 6000$').send(_index)
			else:
				SayText2('\x04[Zombie Riot] » You need to be alive for buy speed potion').send(_index)
		elif choice == 'full_speed':
			if zr.isAlive(userid):
				player.speed += player.speed
				player.cash -= 12000
				SayText2('\x04[Zombie Riot] » You have bought full speed with 12000$').send(_index)
			else:
				SayText2('\x04[Zombie Riot] » You need to be alive for buy speed potion').send(_index)