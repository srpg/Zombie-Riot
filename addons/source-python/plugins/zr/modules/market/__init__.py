from players.entity import Player
from players.helpers import index_from_userid, userid_from_index
from menus import PagedMenu, PagedOption, Text
from menus import SimpleMenu, SimpleOption
from filters.weapons import WeaponClassIter
from weapons.manager import weapon_manager
from zr import zr
from zr.modules import message
from messages import SayText2

def weapons_menu(userid):
	menu = SimpleMenu()
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('Weapon Market'))
	menu.append(Text('-'* 25))
	menu.append(SimpleOption(1, 'Rebuy Bullets', 'rebuy'))
	menu.append(SimpleOption(2, 'Rebuy', 'weapon_rebuy'))
	menu.append(SimpleOption(3, 'Secondarys', 'secondary'))
	menu.append(SimpleOption(4, 'Primarys', 'primary'))
	menu.append(SimpleOption(5, 'Grenades', 'grenade'))
	if zr.isAlive(userid):
		menu.append(SimpleOption(6, 'Activate automatic rebuy', 'rebuy_activate'))
	menu.append(Text('-'* 25))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = main_menu_callback
	menu.send(index_from_userid(userid))

def secondary_weapons_menu(userid):
	menu = PagedMenu(title='Secondary Weapons\n')
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	player = Player.from_userid(userid)
	for weapon in WeaponClassIter(is_filters='pistol'):
		menu.append(PagedOption('%s: %s$' % (weapon.basename.title(), weapon.cost), weapon, player.cash >= weapon.cost and zr.isAlive(userid), player.cash >= weapon.cost and zr.isAlive(userid)))
	menu.select_callback = secondary_menu_callback
	menu.send(index_from_userid(userid))

def primary_weapons_menu(userid):
	menu = PagedMenu(title='Primary Weapons\n')
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	player = Player.from_userid(userid)
	for weapon in WeaponClassIter(is_filters='primary'):
		menu.append(PagedOption('%s: %s$' % (weapon.basename.title(), weapon.cost), weapon, player.cash >= weapon.cost and zr.isAlive(userid), player.cash >= weapon.cost and zr.isAlive(userid)))
	menu.select_callback = primary_menu_callback
	menu.send(index_from_userid(userid))

def grenades_menu(userid):
	menu = PagedMenu(title='Grenades\n')
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	player = Player.from_userid(userid)
	for weapon in WeaponClassIter(is_filters='grenade'):
		menu.append(PagedOption('%s: %s$' % (weapon.basename.title(), weapon.cost), weapon, player.cash >= weapon.cost and zr.isAlive(userid), player.cash >= weapon.cost and zr.isAlive(userid)))
	menu.select_callback = grenade_menu_callback
	menu.send(index_from_userid(userid))

def main_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		player = zr.ZombiePlayer(index_from_userid(userid))
		if choice == 'rebuy':
			if zr.isAlive(userid):
				weapon = player.get_active_weapon()
				if weapon.classname.replace('weapon_', '', 1) in zr.secondaries() + zr.rifles() and not weapon.clip == weapon_manager[weapon.classname].clip:
					if player.cash >= 1000:
						player.cash -= 1000
						weapon.clip = weapon_manager[weapon.classname].clip
						weapon.ammo = weapon_manager[weapon.classname].maxammo
						message.Rebuy.send(_index, weapon=weapon.classname.replace('weapon_', '', 1), cost=1000, red=zr.red,green=zr.green,light_green=zr.light_green)
					else:
						message.Money.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					weapon = weapon.classname.replace('weapon_', '', 1).title()
					SayText2(f'{zr.green}[Zombie Riot] » {zr.light_green}Your {zr.green}{weapon} {zr.light_green}have {zr.green}full clip').send(player.index)
			else:
				message.Alive.send(_index, type="rebuy bullets", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == 'secondary':
			secondary_weapons_menu(userid)
		elif choice == 'grenade':
			grenades_menu(userid)
		elif choice == 'primary':
			primary_weapons_menu(userid)
		elif choice == 'weapon_rebuy':
			if zr.isAlive(userid):
				rebuy(userid)
			else:    
				message.Alive.send(_index, type="rebuy weapons", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == 'rebuy_activate':
			if not player.is_autobuy:
				player.is_autobuy = True
				SayText2(f'{zr.green}[Zombie Riot] » {zr.light_green}You have activated automatic {zr.green}rebuy').send(player.index)
			else:
				player.is_autobuy = False
				SayText2(f'{zr.green}[Zombie Riot] » {zr.light_green}You have disabled automatic {zr.green}rebuy').send(player.index)

def rebuy(userid):
	player = Player.from_userid(userid)
	zr_player = zr.ZombiePlayer.from_userid(userid)
	if zr.isAlive(userid):
		if zr_player.weapon_secondary:
			if player.cash >= weapon_manager[zr_player.weapon_secondary].cost:
				if player.secondary:
					player.secondary.remove()
				player.give_named_item(f'weapon_{zr_player.weapon_secondary}')
				player.cash -= weapon_manager[zr_player.weapon_secondary].cost
				message.Weapon.send(player.index, weapon=zr_player.weapon_secondary, cost=weapon_manager[zr_player.weapon_secondary].cost, red=zr.red,green=zr.green,light_green=zr.light_green)
			else:
				message.Money.send(player.index, red=zr.red,green=zr.green,light_green=zr.light_green)
		if zr_player.weapon_rifle:
			if player.cash >= weapon_manager[zr_player.weapon_rifle].cost:
				if player.primary:
					player.primary.remove()
				player.give_named_item(f'weapon_{zr_player.weapon_rifle}')
				player.cash -= weapon_manager[zr_player.weapon_rifle].cost
				message.Weapon.send(player.index, weapon=zr_player.weapon_rifle, cost=weapon_manager[zr_player.weapon_rifle].cost, red=zr.red,green=zr.green,light_green=zr.light_green)
			else:
				message.Money.send(player.index, red=zr.red,green=zr.green,light_green=zr.light_green)
		else:
			print("Weapon wasn't found")
	else:    
		message.Alive.send(player.index, type="rebuy weapons", red=zr.red,green=zr.green,light_green=zr.light_green)

def secondary_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if zr.isAlive(userid):
			player = Player(index_from_userid(userid))
			if player.cash >= choice.cost:
				player.cash -= choice.cost
				secondary = player.secondary
				if secondary:
					secondary.remove()
				player.give_named_item(f'{choice.name}')
				message.Weapon.send(_index, weapon=choice.basename.upper(), cost=choice.cost, red=zr.red,green=zr.green,light_green=zr.light_green)
				zr_player = zr.ZombiePlayer.from_userid(userid)
				zr_player.weapon_secondary = choice.basename
				weapons_menu(userid)
			else:
				message.Money.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
		else:
			message.Alive.send(_index, type=choice.basename.title(), green=zr.green,light_green=zr.light_green)

def grenade_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if zr.isAlive(userid):
			player = Player(index_from_userid(userid))
			check_grenades(userid, choice)

def check_grenades(userid, choice):
	player = Player.from_userid(userid)
	_index = player.index
	if choice.basename == 'hegrenade':
		if not player.get_property_int('localdata.m_iAmmo.011'):
			if player.cash >= choice.cost:
				player.cash -= choice.cost
				player.give_named_item(f'{choice.name}')
				message.Weapon.send(player.index, weapon=choice.basename.title(), cost=choice.cost, red=zr.red,green=zr.green,light_green=zr.light_green)
				weapons_menu(userid)
			else:
				message.Money.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
		else:
			SayText2(f'{zr.green}[Zombie Riot] » {zr.light_green}You cannot buy {zr.green}hegrenade {zr.light_green}you already have {zr.green}hegrenade!').send(player.index)
	if choice.basename == 'smokegrenade':
		if not player.get_property_int('localdata.m_iAmmo.013'):
			if player.cash >= choice.cost:
				player.cash -= choice.cost
				player.give_named_item(f'{choice.name}')
				message.Weapon.send(player.index, weapon=choice.basename.title(), cost=choice.cost, red=zr.red,green=zr.green,light_green=zr.light_green)
				weapons_menu(userid)
			else:
				message.Money.send(player.index, red=zr.red,green=zr.green,light_green=zr.light_green)
		else:
			SayText2(f'{zr.green}[Zombie Riot] » {zr.light_green}You cannot buy {zr.green}smokegrenade {zr.light_green}you already have {zr.green}smokegrenade!').send(player.index)
	if choice.basename == 'flashbang':
		if not player.get_property_int('localdata.m_iAmmo.012'):
			if player.cash >= choice.cost:
				player.cash -= choice.cost
				player.give_named_item(f'{choice.name}')
				message.Weapon.send(_index, weapon=choice.basename.title(), cost=choice.cost, red=zr.red,green=zr.green,light_green=zr.light_green)
				weapons_menu(userid)
			else:
				message.Money.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
		else:
			SayText2(f'{zr.green}[Zombie Riot] » {zr.light_green}You cannot buy {zr.green}flashbang {zr.light_green}you already have {zr.green}flashbang!').send(player.index)

def primary_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if zr.isAlive(userid):
			player = Player(index_from_userid(userid))
			if player.cash >= choice.cost:
				player.cash -= choice.cost
				primary = player.primary
				if primary:
					primary.remove()
				player.give_named_item(f'{choice.name}')
				message.Weapon.send(_index, weapon=choice.basename.title(), cost=choice.cost, red=zr.red,green=zr.green,light_green=zr.light_green)
				zr_player = zr.ZombiePlayer.from_userid(userid)
				zr_player.weapon_rifle = choice.basename
				weapons_menu(userid)
			else:
				message.Money.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
		else:
			message.Alive.send(_index, type=choice.basename.title(), green=zr.green,light_green=zr.light_green)
