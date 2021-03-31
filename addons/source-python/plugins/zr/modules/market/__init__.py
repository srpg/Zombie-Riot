from players.entity import Player
from players.helpers import index_from_userid, userid_from_index
from menus import PagedMenu, PagedOption, Text
from menus import SimpleMenu, SimpleOption
from filters.weapons import WeaponClassIter
from weapons.manager import weapon_manager
from messages import SayText2
from zr import zr
from zr.modules import message

def weapons_menu(userid):
	menu = SimpleMenu()
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('Weapon Market'))
	menu.append(Text('-'* 25))
	menu.append(SimpleOption(1, 'Rebuy', 'rebuy'))
	menu.append(SimpleOption(2, 'Secondarys', 'secondary'))
	menu.append(SimpleOption(3, 'Primarys', 'primary'))
	menu.append(Text('-'* 25))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = main_menu_callback
	menu.send(index_from_userid(userid))

def secondary_weapons_menu(userid):
	menu = PagedMenu(title='Secondary Weapons\n')
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	for weapon in WeaponClassIter(is_filters='pistol'):
		menu.append(PagedOption('%s: %s$' % (weapon.basename.upper(), weapon.cost), weapon, Player(index_from_userid(userid)).cash >= weapon.cost and zr.isAlive(userid), Player(index_from_userid(userid)).cash >= weapon.cost and zr.isAlive(userid)))
	menu.select_callback = secondary_menu_callback
	menu.send(index_from_userid(userid))

def primary_weapons_menu(userid):
	menu = PagedMenu(title='Primary Weapons\n')
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	for weapon in WeaponClassIter(is_filters='primary'):
		menu.append(PagedOption('%s: %s$' % (weapon.basename.upper(), weapon.cost), weapon, Player(index_from_userid(userid)).cash >= weapon.cost and zr.isAlive(userid), Player(index_from_userid(userid)).cash >= weapon.cost and zr.isAlive(userid)))
	menu.select_callback = primary_menu_callback
	menu.send(index_from_userid(userid))
  
def main_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		player = Player(index_from_userid(userid))
		if choice == 'rebuy':
			if zr.isAlive(userid):
				weapon = player.active_weapon
				player.cash -= 1000
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
				SayText2('\x04[Zombie Riot] » You have rebuy weapons bullets back with %s$' % (1000)).send(_index)
			else:
				SayText2('\x04[Zombie Riot] » You need to be alive for weapons bullets rebuy').send(_index)
		elif choice == 'secondary':
			secondary_weapons_menu(userid)
		elif choice == 'primary':
			primary_weapons_menu(userid)
            
def secondary_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if zr.isAlive(userid):
			player = Player(index_from_userid(userid))
			player.cash -= choice.cost
			secondary = player.secondary
			if secondary:
				secondary.remove()
			player.give_named_item('%s' % (choice.name))
			SayText2('\x04[Zombie Riot] » You have bought %s with %s$' % (choice.basename.upper(), choice.cost)).send(_index)
		else:
			SayText2('\x04[Zombie Riot] » You need to be alive for buy weapon').send(_index)
            
def primary_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if zr.isAlive(userid):
			player = Player(index_from_userid(userid))
			player.cash -= choice.cost
			primary = player.primary
			if primary:
				primary.remove()
			player.give_named_item('%s' % (choice.name))
			Weapon.send(_index, name='%s', cost='%s' % (choice.basename.upper(), choice.cost)).#SayText2('\x04[Zombie Riot] » You have bought %s with %s$' % (choice.basename.upper(), choice.cost)).send(_index)
		else:
			SayText2('\x04[Zombie Riot] » You need to be alive for buy weapon').send(_index)
