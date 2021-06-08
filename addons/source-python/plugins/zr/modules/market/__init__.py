from players.entity import Player
from players.helpers import index_from_userid, userid_from_index
from menus import PagedMenu, PagedOption, Text
from menus import SimpleMenu, SimpleOption
from filters.weapons import WeaponClassIter
from weapons.manager import weapon_manager
from zr import zr
from zr.modules import message

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
				weapon = player.get_active_weapon()
				if player.cash >= 1000 and not weapon.classname.replace('weapon_', '', 1) in ['knife', 'hegrenade', 'flashbang', 'smokegrenade']:
					player.cash -= 1000
					weapon.clip = weapon_manager[weapon.classname].clip
					weapon.ammo = weapon_manager[weapon.classname].maxammo
					message.Rebuy.send(_index, weapon=weapon.classname.replace('weapon_', '', 1), cost=1000, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					message.Money.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
			else:
				message.Alive.send(_index, type="rebuy bullets", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == 'secondary':
			secondary_weapons_menu(userid)
		elif choice == 'primary':
			primary_weapons_menu(userid)
		elif choice == 'weapon_rebuy':
			if zr.isAlive(userid):
				rebuy(userid)
			else:    
				message.Alive.send(_index, type="rebuy weapons", red=zr.red,green=zr.green,light_green=zr.light_green)
                
def rebuy(userid):
	if zr.isAlive(userid):
		player = Player.from_userid(userid)
		zr_player = zr.ZombiePlayer.from_userid(userid)
		if zr_player.weapon_secondary:
			if player.cash >= weapon_manager[zr_player.weapon_secondary].cost:
				if player.secondary:
					player.secondary.remove()
				player.give_named_item('weapon_%s' % zr_player.weapon_secondary)
				player.cash -= weapon_manager[zr_player.weapon_secondary].cost
				message.Weapon.send(_index, weapon=zr_player.weapon_secondary, cost=weapon_manager[zr_player.weapon_secondary].cost, red=zr.red,green=zr.green,light_green=zr.light_green)
			else:
				message.Money.send(player.index, red=zr.red,green=zr.green,light_green=zr.light_green)
		if zr_player.weapon_rifle:
			if player.cash >= weapon_manager[zr_player.weapon_rifle].cost:
				if player.primary:
					player.primary.remove()
				player.give_named_item('weapon_%s' % zr_player.weapon_rifle)
				player.cash -= weapon_manager[zr_player.weapon_rifle].cost
				message.Weapon.send(_index, weapon=zr_player.weapon_rifle, cost=weapon_manager[zr_player.weapon_rifle].cost, red=zr.red,green=zr.green,light_green=zr.light_green)
			else:
				message.Money.send(player.index, red=zr.red,green=zr.green,light_green=zr.light_green)
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
				player.give_named_item('%s' % (choice.name))
				message.Weapon.send(_index, weapon=choice.basename.upper(), cost=choice.cost, red=zr.red,green=zr.green,light_green=zr.light_green)
				zr_player = zr.ZombiePlayer.from_userid(userid)
				zr_player.weapon_secondary = choice.basename.upper()
				weapons_menu(userid)
			else:
				message.Money.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
		else:
			message.Alive.send(_index, type=choice.basename.upper(), green=zr.green,light_green=zr.light_green)
            
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
				player.give_named_item('%s' % (choice.name))
				message.Weapon.send(_index, weapon=choice.basename.upper(), cost=choice.cost, red=zr.red,green=zr.green,light_green=zr.light_green)
				zr_player = zr.ZombiePlayer.from_userid(userid)
				zr_player.weapon_rifle = choice.basename.upper()
				weapons_menu(userid)
			else:
				message.Money.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
		else:
			message.Alive.send(_index, type=choice.basename.upper(), green=zr.green,light_green=zr.light_green)
