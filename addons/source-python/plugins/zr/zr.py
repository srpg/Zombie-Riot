 # Imports
import os, path, random
# Core
from core import GAME_NAME, echo_console
# Entity
from entities.entity import Entity
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
# Say/Server Commands
from commands.say import SayFilter
from commands.server import ServerCommand
# Config
from configobj import ConfigObj
# Weapon
from filters.weapons import WeaponClassIter, WeaponIter
# Messages
from messages import TextMsg, HintText
# Download
from stringtables.downloads import Downloadables
# Color
from colors import Color
from colors import GREEN, LIGHT_GREEN, RED
# Menus
from menus import Text, SimpleMenu, PagedMenu, SimpleOption
# Listeners
from listeners import OnLevelShutdown
# Own Modules
from zr.modules import admin
from zr.modules import market 
from zr.modules import potion
from zr.modules import clan_tag
from zr.modules import version
from zr.modules import message

__FILEPATH__    = path.Path(__file__).dirname()
_CONFIG = ConfigObj(__FILEPATH__ + '/_settings.ini')
download = os.path.join(__FILEPATH__ + '/css.txt')

weapons = [weapon.basename for weapon in WeaponClassIter(not_filters='knife')]

#=====================
# Config
#=====================
server_name = 0 # Enable change server name to Zombie Riot Day [1/11]
fire = 1 # 1 = Enable fire hegrenades to burn zombies, 0 = Disabled
info_panel = 1 # 1 = Enable show left side of screen info of zombie, 0 = Disabled

#===================
# Def/Global functions
#===================
red         = RED
green       = GREEN
light_green = LIGHT_GREEN

clan = '%s' % ('[Best RPG]').replace("'", "").replace("'", "")# Change inside of ('You clan_tag') to enable your clan tag features, currently it enable features to [Best RPG] clan_tag

class ZombiePlayer(Player):
	caching = True # Uses caching

	def __init__(self, index):
		super().__init__(index)
		self.consecutive_bullets 	= False
		self.joined_team 		= False
		self.welcome_message 		= False

def alive():
	return len(PlayerIter(['ct', 'alive']))

def alive_zombies():
	return len(PlayerIter(['t', 'alive']))
    
def real_count():
	return alive() # Apperently this code counts basic amount of ct's

def hudhint(userid, text):
	HintText(message=text).send(index_from_userid(userid))

def remove_idle_weapons():
	for w in WeaponIter.iterator():
		if w.get_property_int('m_hOwnerEntity') in [-1, 0]:
			w.call_input('Kill')

def getUseridList():
	for i in PlayerIter.iterator():
		yield i.userid
	
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

@ServerCommand('zombie_version')
def zombie_version(command):
	version.check_version()

def load():
	global _loaded
	global _infity
	global _value
	global _humans
	global _health
	if GAME_NAME == 'cstrike':
		_loaded = 1
		if  _loaded > 0:
			_value = 0
			_humans = 0
			_health = 100
			_infity = False
			global _day
			_day = 1
			echo_console('***********************************************************')
			version.check_version()
			echo_console('[Zombie Riot] Initializing Settings')
			queue_command_string('bot_quota 20')
			queue_command_string('bot_join_after_player 0')
			queue_command_string('bot_join_team t')
			queue_command_string('mp_limitteams 0')
			queue_command_string('mp_autoteambalance 0')
			queue_command_string('bot_chatter off')
			queue_command_string('mp_humanteam ct')
			queue_command_string('sv_hudhint_sound 0')
			set_download()
			echo_console('[Zombie Riot] Clan Tag: %s' % (clan))
			init_loop()
			echo_console('[Zombie Riot] Author: F1N/srpg')
			echo_console('[Zombie Riot] Version: Beta')
			echo_console('[Zombie Riot] Loaded Completely')
			queue_command_string('mp_restartgame 1')
			echo_console('***********************************************************')
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

@OnLevelShutdown
def shutdown():
	global _loaded
	global _day
	if _loaded > 0:
		_day = 1
    

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
		name = player.name
		if player.team == 3:
			zr_player = ZombiePlayer.from_userid(args['userid'])
			if not zr_player.welcome_message:
				message.welcome.send(player.index, name=name, ver=version.Ver, red=red,green=green,light_green=light_green) # Welcome message
				zr_player.welcome_message = True
			global _humans
			_humans += 1
			message.Game.send(player.index,green=green,light_green=light_green)
			message.Market.send(player.index,green=green,light_green=light_green)

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
		if server_name:
			queue_command_string('hostname "Zombie Riot Day: [%s/%s]"' % (_day, max_day()))
		_humans = real_count()
		echo_console('***********************************************************')
		echo_console('[Zombie Riot] Round Start')
		echo_console('[Zombie Riot] Current Day: %s/%s' % (_day, max_day()))
		echo_console('[Zombie Riot] Current Zombies: %s' % (_value))
		if _day > 0:
			echo_console('[Zombie Riot] Current Zombies Health: %s' % (_health))
		echo_console('[Zombie Riot] Current Humans: %s' % (_humans))
		echo_console('***********************************************************')

@Event('player_activate')
def player_activate(args):
	global _loaded
	if _loaded > 0:
		player = ZombiePlayer.from_userid(args['userid'])
		player.joined_team = False
		player.welcome_message = False

@Event('player_team')
def player_team(args):
	global _loaded
	if _loaded > 0:
		global _humans
		userid = args.get_int('userid')
		if _humans > 0:
			if not isAlive(userid):
				if args.get_int('team') == 3: # Is ct
					player = ZombiePlayer.from_userid(userid)
					if not player.joined_team:
						Player(index_from_userid(userid)).delay(0.1, timer, (userid, 10, 1))
						player.joined_team = True
					else:
						Player(index_from_userid(userid)).delay(0.1, timer, (userid, 30, 1))

@Event('player_disconnect')
def player_disconnect(args):
	userid = args.get_int('userid')
	if Player(index_from_userid(userid)).team == 3 and isAlive(userid):
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
		victim = Player.from_userid(userid)
		killer = Player.from_userid(attacker)# Use instead args['attacker']?
		if attacker > 0:
			if victim.is_bot():
				if userid == attacker: # Did zombie kill himself, Should fix fire kills not removing values
					_value -= 1
					if not _value == alive_zombies():
						Delay(0.1, respawn, (userid,)) # Respawn suicided bot due to fire
			if not victim.is_bot():
				if userid == attacker: # Did player suicide
					_humans -= 1
					if _humans > 0:
						victim.delay(0.1, timer, (userid, 30, 1))
			if not victim.team == killer.team:
				if victim.team == 3: 
					_humans -= 1
					if _humans > 0:
						victim.delay(0.1, timer, (userid, 30, 1))
				if _humans > 0:
					Delay(0.1, won)
					if victim.team == 2:
						_value -= 1
						if not _value == alive_zombies(): # Works better than if _value > 19
							Delay(0.1, respawn, (userid,))
				if _value == 0: 
					for player in PlayerIter('all'):
						player.client_command('r_screenoverlay overlays/zr/humans_win.vmt')
						player.delay(3, cancel_overplay, (player.index,))
				if _humans == 0:
					for player in PlayerIter('all'):
						player.client_command('r_screenoverlay overlays/zr/zombies_win.vmt')
						player.delay(3, cancel_overplay, (player.index,))

def cancel_overplay(index):
	player = Player(index)
	player.client_command('r_screenoverlay 0')

@Event('weapon_fire_on_empty')
def weapon_fire_on_empty(args):
	global _loaded
	if _loaded > 0:
		userid = args.get_int('userid')
		player = Player.from_userid(userid)
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
	message.Won.send(red=red,green=green,light_green=light_green)
	message.New.send(red=red,green=green,light_green=light_green)
	_day = 1

def burn(userid, duration):
	try:
		Entity(index_from_userid(userid)).call_input('IgniteLifetime', float(duration))
	except ValueError:
		pass

def respawn(userid):
	player = Player.from_userid(userid)
	player.spawn(True)

def timer(userid, duration, count):
	global _humans
	if _humans > 0:
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
	for i in getUseridList():
		if info_panel:
			hudhint(i, build_hudmessage(i))

def build_hudmessage(userid):
	global _value
	global _day
	_health = get_health(_day)
	__msg__ = 'Day: %s/%s' % (_day, max_day())
	__msg__ += '\nZombies: %s' % (_value)
	__msg__ += '\nZombies Health: %s' % (_health)
	__msg__ += '\nHumans: %s' % (_humans)
	return __msg__

@Event('player_hurt')
def player_hurt(args):
	global _loaded
	if _loaded > 0:
		if args.get_string('weapon') == 'hegrenade' and fire:
			userid = args.get_int('userid')
			attacker = args.get_int('attacker')
			victim = Player.from_userid(userid)
			killer = Player.from_userid(attacker)
			if attacker > 0:
				if not victim.team == killer.team:
					burn(userid, 10)   

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
		elif choice == 'admin_menu':
			admin.adminmenu(userid)

def info_menu_callback(_menu, _index, _option):
	choice = _option.value
	if choice:
		userid = userid_from_index(_index)
		if choice == 'Back':
			main_menu(userid)
		elif choice == 'menu':
			potions_info_menu(userid)
		elif choice == 'return':
			info_menu(userid)
            
def potions_info_menu(userid):
	menu = SimpleMenu()
	if is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('About Potions'))
	menu.append(Text('-' * 30))
	menu.append(Text('- Health potions is based of your total health.'))
	menu.append(Text('- Speed potions is based of your current speed.'))
	menu.append(Text('- The purchased potions only last to:'))
	menu.append(Text('- Death or new round start'))
	menu.append(Text('-' * 30))
	menu.append(SimpleOption(8, 'Back', 'return'))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = info_menu_callback
	menu.send(index_from_userid(userid))
    
def info_menu(userid):
	menu = SimpleMenu()
	if is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('Info Menu'))
	menu.append(Text('-' * 30))
	menu.append(Text(' '))
	menu.append(SimpleOption(1, 'Potions', 'menu'))
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
	menu.append(Text('- 10% full clip restore chance when hurt'))
	menu.append(Text('- Requires: %s clan_tag' % (clan)))
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
	if admin.get_admin(userid):
		menu.append(SimpleOption(4, 'Admin', 'admin_menu'))
	menu.append(Text('-' * 30))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = main_menu_callback
	menu.send(index_from_userid(userid))
