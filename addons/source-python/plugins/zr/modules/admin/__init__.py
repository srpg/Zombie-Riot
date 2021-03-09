from players.entity import Player
from players.helpers import index_from_userid, userid_from_index
from engines.server import queue_command_string
from menus import SimpleMenu, Text, SimpleOption
from menus import PagedMenu, PagedOption
from messages import SayText2
from zr import zr
from zr.modules import version

admins = ['[U:1:182650578]']

def get_steamid(userid):
	pEnt	= Player(index_from_userid(userid))
	steamid	= pEnt.steamid

	if steamid == 'BOT':
		steamid = 'BOT_%s' % pEnt.name

	return steamid


def is_admin(userid):
	if get_steamid(userid) in admins:
		return True
	return False
    
def adminmenu(userid):
	menu = SimpleMenu()
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('Admin Menu\nSection: Main'))
	menu.append(Text(' '))
	menu.append(SimpleOption(1, 'Days',	'day'))
	menu.append(Text(' '))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = admin_menu_callback
	menu.send(index_from_userid(userid))

def day_menu(userid):
	menu = PagedMenu(title='Admin Menu\nSection: Days\n')
	if zr.is_queued(menu, index_from_userid(userid)):
		return
	for i in [1, 2, 3, 4, 5, 10]:
		menu.append(PagedOption('%s' % (i), (i)))
	menu.select_callback = days_menu_callback
	menu.send(index_from_userid(userid))

def days_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		zr._day = choice
		SayText2('\x04[Zombie Riot] » You have changed day to %s!' % (choice)).send(index_from_userid(userid))

def admin_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if choice == 'update':
			update_menu(userid)
		elif choice == 'day':
			day_menu(userid)