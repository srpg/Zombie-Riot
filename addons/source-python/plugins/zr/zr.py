 # Imports
import os, path, random
# Core
from core import GAME_NAME, echo_console
# Events
from events import Event
from events.hooks import PreEvent, EventAction
# Player class / userid / Player Iter
from players.helpers import index_from_userid, userid_from_index
from players.entity import Player
from filters.players import PlayerIter
# Engine
from engines.precache import Model
from engines.server import queue_command_string
# Delay
from listeners.tick import Delay
# Say Commands
from commands.say import SayFilter
# Config
from configobj import ConfigObj
# Weapon
from filters.weapons import WeaponClassIter, WeaponIter
from weapons.manager import weapon_manager
# Messages
from messages import TextMsg, HudMsg, SayText2
# Download
from stringtables.downloads import Downloadables
# Color
from colors import Color
# Menus
from menus import Text, SimpleMenu, PagedMenu, SimpleOption
# Own Modules
from zr.modules import market 
from zr.modules import potion
from zr.modules import clan_tag

__FILEPATH__    = path.Path(__file__).dirname()
_CONFIG = ConfigObj(__FILEPATH__ + '/_settings.ini')
download = os.path.join(__FILEPATH__ + '/css.txt')

weapons = [weapon.basename for weapon in WeaponClassIter(not_filters='knife')]


#===================
# Def/Global functions
#===================
clan = ['Test']

def alive():
	return len(PlayerIter(['ct', 'alive']))

def real_count():
	return alive() # Apperently this code counts basic amount of ct's

def remove_idle_weapons():
	for w in WeaponIter.iterator():
		if w.get_property_int('m_hOwnerEntity') in [-1, 0]:
			w.call_input('Kill')

def getUseridList():
	for i in PlayerIter.iterator():
		yield i.userid

_HUDMSG_COLOR = Color(255, 255, 255)
_HUDMSG_X = 0.02
_HUDMSG_Y = 0.3
_HUDMSG_EFFECT = 0
_HUDMSG_FADEOUT = 0
_HUDMSG_HOLDTIME = 2
_HUDMSG_FXTIME = 0
_HUDMSG_CHANNEL = 3
	
def hudmessage(userid, text):
	HudMsg(text, color1=_HUDMSG_COLOR, x=_HUDMSG_X, y=_HUDMSG_Y,
		effect=_HUDMSG_EFFECT,
		fade_out=_HUDMSG_FADEOUT,
		hold_time=_HUDMSG_HOLDTIME,
		fx_time=_HUDMSG_FXTIME,
		channel=_HUDMSG_CHANNEL
	).send(index_from_userid(userid))

def centertell(userid, text):
	TextMsg(message=text, destination=4).send(index_from_userid(userid))

@PreEvent('server_cvar', 'player_team', 'player_disconnect', 'player_connect_client')
def pre_events(game_event):
	global _loaded
	if _loaded > 0:
		return EventAction.STOP_BROADCAST

@SayFilter
def sayfilter(command, index, teamonly):
	global _loaded
	if _loaded > 0:
		userid = None
		if index:
			userid = userid_from_index(index)
			if userid and command:
				text = command[0].replace('!', '', 1).replace('/', '', 1).lower()
				args = command.arg_string
				if text == 'market':
					main_menu(userid)
					return False

def load():
	global _loaded
	global _value
	global _humans
	global _health
	if GAME_NAME == 'cstrike':
		_loaded = 1
		if  _loaded > 0:
			_value = 0
			_humans = 0
			_health = 100
			global _day
			_day = 1
			echo_console('***********************************************************')
			echo_console('[Zombie Riot] Initializing Settings')
			queue_command_string('bot_quota 20')
			queue_command_string('bot_join_after_player 0')
			queue_command_string('bot_join_team t')
			queue_command_string('mp_limitteams 0')
			queue_command_string('mp_autoteambalance 0')
			queue_command_string('bot_chatter off')
			queue_command_string('mp_humanteam ct')
			set_download()
			echo_console('[Zombie Riot] Clan Tag: %s' % (clan))
			init_loop()
			echo_console('[Zombie Riot] Author: F1N/srpg')
			echo_console('[Zombie Riot] Version: Beta')
			echo_console('[Zombie Riot] Loaded Completely')
			queue_command_string('mp_restartgame 1')
			echo_console('***********************************************************')
		else:
			echo_console('[Zombie Riot] The plugin is not loaded!')
	else:
		raise NotImplementedError('[Zombie Riot] This plugin only supports Counter-Strike-Source!') 

def unload():
	global _loaded
	stop_loop()
	_loaded = 0
	echo_console('***********************************************************')
	echo_console('[Zombie Riot] Unloaded Completely')
	if _loaded == 0:
		msg = 'Not Loaded'
	else: 
		msg = 'Loaded'
	echo_console('[Zombie Riot] Plugin is %s' % (msg))
	echo_console('***********************************************************')

def isAlive(userid):
	return not Player(index_from_userid(userid)).get_property_bool('pl.deadflag')

def max_day():
	return int(_CONFIG['Days']['value'])

def get_days(value):
	val = '%s' % (value)
	return  int(_CONFIG[val]['amount'])

def get_health(value):
	val = '%s' % (value)
	return  int(_CONFIG[val]['health'])
    
def get_model(value):
	val = '%s' % (value)
	return  _CONFIG[val]['Model']
    
def set_download():
	echo_console('[Zombie Riot] Setting downloads!')
	dl = Downloadables()
	with open(download) as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			dl.add(line)

@Event('player_spawn')
def player_spawn(args):
	global _loaded
	if _loaded > 0:
		global _health
		global _day
		userid = args.get_int('userid')
		player = Player(index_from_userid(userid))
		if player.team == 2: # Is a terrorist team
			player.restrict_weapons(*weapons)
			value = _day
			_health = get_health(value)
			_model = get_model(value)
			player.health = _health
			player.set_model(Model(_model))
			remove_idle_weapons()
		player.noblock = True
		player.cash = 12000
		if player.team == 3:
			global _humans
			_humans += 1
			SayText2('\x04[Zombie Riot] » The game is human vs zombies, to order win a day you have to kill all zombies.').send(player.index)
			SayText2('\x04[Zombie Riot] » Type market to open main menu').send(player.index)
		if player.clan_tag in clan:
			player.max_health += 25
			player.health = player.max_health
			player.speed += 0.10 # Increases 10% of speed
			base = 1
			player.gravity = base
			player.gravity -= 0.10 # Lowers gravity 10%

@Event('round_start')
def round_start(args):
	global _loaded
	if _loaded > 0:
		queue_command_string('mp_roundtime 9')
		queue_command_string('bot_knives_only 1')
		global _day
		global _value
		global _humans
		_health = get_health(_day)
		_value = get_days(_day)
		queue_command_string('hostname "Zombie Riot Day: [%s/%s]"' % (_day, max_day()))
		_humans = real_count()
		echo_console('***********************************************************')
		echo_console('[Zombie Riot] Current Day: %s/%s' % (_day, max_day()))
		echo_console('[Zombie Riot] Current Zombies: %s' % (_value))
		if _day > 0:
			echo_console('[Zombie Riot] Current Zombies Health: %s' % (_health))
		echo_console('[Zombie Riot] Current Humans: %s' % (_humans))
		echo_console('***********************************************************')
    
@Event('player_team')
def player_team(args):
	global _loaded
	if _loaded > 0:
		global _humans
		userid = args.get_int('userid')
		if _humans > 0:
			if not isAlive(userid):
				if args.get_int('team') == 3: # Is ct
					Player(index_from_userid(userid)).delay(0.1, timer, (userid, 10, 1))

@Event('player_disconnect')
def player_disconnect(args):
	userid = args.get_int('userid')
	if Player(index_from_userid(userid)).team == 3:
		global _loaded
		if _loaded > 0:
			global _humans
			_humans -= 1

@Event('player_death')
def player_death(args):
	global _loaded
	if _loaded > 0:
		global _humans
		global _value
		global _day
		userid = args.get_int('userid')
		attacker = args.get_int('attacker')
		if attacker > 0:
			if not Player(index_from_userid(userid)).team == Player(index_from_userid(attacker)):
				player = Player(index_from_userid(userid))
				if player.is_bot():
					_value -= 1
				if player.team == 3: 
					_humans -= 1
					if _humans > 0:
						Player(index_from_userid(userid)).delay(0.1, timer, (userid, 30, 1))
				if _humans > 0:
					Delay(0.1, won)
					if player.team == 2 and _value > 19:
						Delay(0.1, respawn, (userid,))


@Event('weapon_fire_on_empty')
def weapon_fire_on_empty(args):
	global _loaded
	if _loaded > 0:
		userid = args.get_int('userid')
		player = Player(index_from_userid(userid))
		if player.primary:
			player.primary.remove()
		elif player.secondary:
			player.secondary.remove()

def won():
	global _day
	global _value
	if _value == 0:
		_day += 1
		if _day > max_day():
			Delay(1, winner)
            
def winner():
	global _day
	SayText2('\x04[Zombie Riot] » Congralations the humans has won the game!').send()
	SayText2('\x04[Zombie Riot] » For winning the game, the game is starting over!').send()
	_day = 1
    
def respawn(userid):
	player = Player(index_from_userid(userid))
	player.spawn(True)

def timer(userid, duration, count):
	if not isAlive(userid):
		player = Player(index_from_userid(userid))
		if player.team == 3:
			centertell(userid, 'You will respawn in %s Seconds' % (duration - (count)))
			count += 1
			if count == duration:
				player.delay(0.1, respawn, (userid,))
			else:
				player.delay(1, timer, (userid, duration, count))

def init_loop():
	global hint
	hint = Delay(1.0, info)

def stop_loop():
	global hint
	hint.cancel()
    
def info():
	init_loop()
	temp_menu = PagedMenu()
	temp_menu = SimpleMenu()
	for i in getUseridList():
		if not is_queued(temp_menu, index_from_userid(i)):
			hudmessage(i, build_hudmessage(i))

def build_hudmessage(userid):
	global _value
	global _day
	_health = get_health(_day)
	__msg__ = 'Zombie Riot'
	__msg__ += '\n\n'
	__msg__ += 'Day: %s/%s' % (_day, max_day())
	__msg__ += '\nZombies: %s' % (_value)
	__msg__ += '\nZombies Health: %s' % (_health)
	__msg__ += '\nHumans: %s' % (_humans)
	player = Player(index_from_userid(userid))
	if player.clan_tag in clan and isAlive(userid):
		__msg__ += '\n\n'
		__msg__ += 'Health: %s/%s' % (player.health, player.max_health)
		speed = '%s%s' % (int(player.speed / 1.0 * 100.0), '%')
		__msg__ += '\nSpeed: %s' % (speed)
		__msg__ += '\nGravity: %s%s' % (int(player.gravity / 1.0 * 100.0), '%')
	return __msg__

@Event('player_hurt')
def player_hurt(args):
	global _loaded
	if _loaded > 0:
		if args.get_string('weapon') == 'hegrenade':
			userid = args.get_int('userid')
			attacker = args.get_int('attacker')
			if attacker > 0:
				if not Player(index_from_userid(userid)).team == Player(index_from_userid(attacker)).team:
					Player(index_from_userid(userid)).ignite(10.0)    
                  

#==================================
# Menu Call Backs
#==================================
def is_queued(_menu, _index):
	q = _menu._get_queue_holder()
	for i in q:
		if i == _index:
			for x in q[i]:
				return True
	return False


def main_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if choice == 'weapon':
			market.weapons_menu(userid)
		elif choice == 'potion':
			potion.potion_market_menu(userid)
		elif choice == 'info':
			info_menu(userid)

def info_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if choice == 'Back':
			main_menu(userid)

def info_menu(userid):
	menu = SimpleMenu()
	if is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('About Potions'))
	menu.append(Text('-' * 30))
	menu.append(Text('- Health potions is based of your total health.'))
	menu.append(Text('- The purchased potions only last to:'))
	menu.append(Text('- Death or new round start'))
	menu.append(Text(' '))
	menu.append(Text('About Zombie Riot:'))
	menu.append(Text('- Made by F1N/srpg'))
	menu.append(Text('- Is still in developing'))
	menu.append(Text('- Has unigue support for clan tag'))
	menu.append(Text(' '))
	menu.append(Text('About Clan Tag:'))
	menu.append(Text('- Increases your spawn health/speed'))
	menu.append(Text('- Lowers your gravity'))
	menu.append(Text('- Increases Health/Speed per kill'))
	menu.append(Text('- Increases Max health/speed limit'))
	menu.append(Text('- 10% full clip restore chance whenn hurt'))
	menu.append(Text('-' * 30))
	menu.append(SimpleOption(8, 'Back', 'Back'))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = info_menu_callback
	menu.send(index_from_userid(userid))
    
def main_menu(userid):
	menu = SimpleMenu()
	if is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('Market\nSection: Main'))
	menu.append(Text('-' * 30))
	menu.append(SimpleOption(1, 'Weapons', 'weapon'))
	menu.append(SimpleOption(2, 'Potions', 'potion'))
	menu.append(SimpleOption(3, 'Info', 'info'))
	menu.append(Text('-' * 30))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = main_menu_callback
	menu.send(index_from_userid(userid))