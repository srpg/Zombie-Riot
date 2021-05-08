import path
from configobj import ConfigObj
from players.entity import Player
from engines.server import engine_server
from mathlib import Vector
from effects import TempEntity
from players.helpers import index_from_userid, userid_from_index
from engines.server import queue_command_string
from menus import SimpleMenu, Text, SimpleOption
from menus import PagedMenu, PagedOption
from messages import SayText2
from zr import zr

__FILEPATH__	= path.Path(__file__).dirname()
admins = ConfigObj(__FILEPATH__ + '/_admins.ini')

def get_admin(userid):
	player = Player(index_from_userid(userid))
	return player.steamid.lstrip('[').rstrip(']') in admins
 
def adminmenu(userid):
	menu = SimpleMenu()
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('Admin Menu\nSection: Main'))
	menu.append(Text(' '))
	menu.append(SimpleOption(1, 'Zombies',	'Zombie'))
	menu.append(SimpleOption(2, 'Add Days',	'day'))
	menu.append(SimpleOption(3, 'Remove Days', 'day_remove'))
	menu.append(Text(' '))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = admin_menu_callback
	menu.send(index_from_userid(userid))

def day_menu(userid, type):
	menu = PagedMenu(title='Admin Menu\nSection: %s Days\n' % (type))
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	for i in [1, 2, 3, 4, 5, 10]:
		menu.append(PagedOption('%s' % (i), (i)))
	if type == 'add':
		menu.select_callback = days_menu_callback
	elif type == 'remove':
		menu.select_callback = remove_days_menu_callback
	menu.send(index_from_userid(userid))

def zomnbies_menu(userid):
	menu = SimpleMenu()
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('Admin Menu\nSection: Zombies'))
	menu.append(Text(' '))
	menu.append(SimpleOption(1, 'Beacon', 'beacon'))
	menu.append(Text(' '))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = admin_menu_callback
	menu.send(index_from_userid(userid))

def zombies_players_menu(userid):
	menu = PagedMenu(title='Admin Menu\nSection: Beacon\n')
	if zr.is_queued(menu, index_from_userid(userid)):
		return	
	for i in zr.getUseridList():
		if zr.isAlive(i):
			menu.append(PagedOption('%s' % (Player(index_from_userid(i)).name), (i)))
	menu.select_callback = zombie_menu_callback
	menu.send(index_from_userid(userid))
    
def days_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if not zr._day >= zr.max_day():
			zr._day += choice
			SayText2('\x04[Zombie Riot] » You have changed day to %s!' % (choice)).send(index_from_userid(userid))

def remove_days_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if not zr._day <= 1:
			zr._day -= choice
			SayText2('\x04[Zombie Riot] » You have removed %s days!' % (choice)).send(index_from_userid(userid))

def admin_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if choice == 'Zombie':
			zomnbies_menu(userid)
		elif choice == 'day':
			day_menu(userid, 'add')
		elif choice == 'day_remove':
			day_menu(userid, 'remove')
		elif choice == 'beacon':
			zombies_players_menu(userid)

def zombie_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		player = Player(index_from_userid(userid))
		player.delay(1, beacon, (choice,))

def beacon(userid):
	if zr.isAlive(userid):
		player = Player(index_from_userid(userid))
		player.delay(1, beacon, (userid,))
		player.emit_sound(sample='buttons/blip1.wav',volume=1.0,attenuation=0.5)
		if player.team == 2:
			r = 235
			b = 0
		else:
			r = 0
			b = 102
		beamRing(userid, 1, 350, 0, 1, 3, 3, r, 0, b, 255, 'sprites/laserbeam.vmt')
		beamRing(userid, 1, 350, 0, 1, 3, 3, 255, 255, 255, 255, 'sprites/laserbeam.vmt')

def beamRing(userid, startRadius, endRadius, zplus, lifeTime, width, amplitude, r, g, b, a=255, vmt='sprites/laserbeam.vmt'):
	x,y,z				= getPlayerLocation(userid)
	modelIndex			= engine_server.precache_model(vmt)
	tempEnt				= TempEntity('BeamRingPoint')

	tempEnt.red			= r
	tempEnt.green		= g
	tempEnt.blue		= b
	tempEnt.alpha		= a

	tempEnt.center		= Vector(x, y, z + zplus)
	tempEnt.start_radius	= startRadius
	tempEnt.end_radius	= endRadius

	tempEnt.life_time	= lifeTime
	tempEnt.start_width	= width
	tempEnt.end_width	= width
	tempEnt.amplitude	= amplitude

	tempEnt.halo_index	= modelIndex
	tempEnt.model_index	= modelIndex

	tempEnt.create()

def getPlayerLocation(userid):
	x,y,z = Player(index_from_userid(userid)).get_key_value_string('origin').split(' ')
	return (float(x), float(y), float(z))
