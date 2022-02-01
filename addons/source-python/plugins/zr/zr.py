import os, path, random
from engines.server import engine_server
from core import GAME_NAME, echo_console
from entities.entity import Entity
from events import Event
from events.hooks import PreEvent, EventAction
from players.helpers import index_from_userid, userid_from_index, userid_from_inthandle
from players.entity import Player
from filters.players import PlayerIter
from filters.entities import EntityIter
from engines.precache import Model
from engines.server import queue_command_string
from listeners.tick import Delay
from commands.say import SayCommand
from commands.server import ServerCommand
from configobj import ConfigObj
from filters.weapons import WeaponClassIter, WeaponIter
from weapons.manager import weapon_manager
from messages import TextMsg, HintText, SayText2
from stringtables.downloads import Downloadables
from colors import Color, GREEN, LIGHT_GREEN, RED
from menus import Text, SimpleMenu, PagedMenu, SimpleOption
from entities.hooks import EntityPreHook, EntityCondition
from entities.helpers import index_from_pointer
from entities import TakeDamageInfo
from memory import make_object
from listeners import OnLevelShutdown
from zr.modules import admin
from zr.modules import market 
from zr.modules import potion
from zr.modules import clan_tag
from zr.modules import version
from zr.modules import message

__FILEPATH__    = path.Path(__file__).dirname()
_CONFIG = ConfigObj(__FILEPATH__ + '/_settings.ini')
download = os.path.join(__FILEPATH__ + '/css.txt')
_loaded = 0
weapons = [weapon.basename for weapon in WeaponClassIter(not_filters='knife')]

_cankill = True
_show_hudhint = True

#=====================
# Config
#=====================
server_name = 0 # Enable change server name to Zombie Riot Day [1/11]
fire = 1 # 1 = Enable fire hegrenades to burn zombies, 0 = Disabled
info_panel = 1 # 1 = Enable show left side of screen info of zombie, 0 = Disabled
auto_updater = 1 # 1 = Enable automatic updating when server start and new version available
freeze_time = 10 # How many seconds zombies are frozen
beacon_value = 4 # How much less zombies have remaining to beacon
#===================
# Def/Global functions
#===================
red         = RED
green       = GREEN
light_green = LIGHT_GREEN

server_clan = ['[Best RPG]'] # Change here to activate clan tag

clan = '%s' % ('[Best RPG]').replace("'", "").replace("'", "")# This is used menu to display which clan tag have using

class ZombiePlayer(Player):
	caching = True # Uses caching

	def __init__(self, index):
		super().__init__(index)
		self.infinity_bullets 	    = False
		self.joined_team 		    = False
		self.welcome_message 		= False
		self.weapon_rifle 		    = False
		self.weapon_secondary 		= False
		self.player_target          = False
		self.is_beaconned           = False
		self.is_autobuy             = False

def strip_weapons(userid):
	player = Player.from_userid(userid)
	if player.primary:
		player.primary.remove()
	if player.secondary:
		player.secondary.remove()

def secondaries():
	if GAME_NAME == 'cstrike':
		return ['usp','glock','deagle','p228','elite','fiveseven']
	else:
		print(f'[Zombie Riot] does not have defined weapons for {GAME_NAME}')

def rifles():
	if GAME_NAME == 'cstrike':
		return ['m4a1','ak47','awp','scout','sg552','galil','famas','aug','ump45','mp5navy','m3','xm1014','tmp','mac10','p90','g3sg1','sg550','m249']
	else:
		print(f'[Zombie Riot] does not have defined weapons for {GAME_NAME}')

def alive():
	return len(PlayerIter(['ct', 'alive']))

def all_zombies():
	return len(PlayerIter(['t', 'all']))

def alive_zombies():
	return len(PlayerIter(['t', 'alive']))
    
def real_count():
	return alive() # Apperently this code counts basic amount of ct's

def bomb_target(enable):
	for i in EntityIter.iterator():
		if i.classname.startswith('func_bomb'):
			i.call_input(['Disable', 'Enable'][int(bool(enable))])
            
def hostage_rescue(enable):
	for i in EntityIter.iterator():
		if i.classname.startswith('func_hostage'):
			i.call_input(['Disable', 'Enable'][int(bool(enable))])

def hudhint(userid, text):
	HintText(message=text).send(index_from_userid(userid))

def getUseridList():
	for i in PlayerIter.iterator():
		yield i.userid
	
def centertell(userid, text):
	TextMsg(message=text, destination=4).send(index_from_userid(userid))

@EntityPreHook(EntityCondition.is_player, 'buy_internal')
def pre_buy(args):
	try:
		player = ZombiePlayer(index_from_pointer(args[0]))
		weapon = args[1]
		if not player.is_bot():
			if GAME_NAME == 'cstrike':
				if weapon in secondaries():
					player.weapon_secondary = weapon
				elif weapon in rifles():
					player.weapon_rifle = weapon
			else:
				print(f'[Zombie Riot] This plugin does not have weapons data for {GAME_NAME}')
		else:
			return False
	except KeyError:
		return

@EntityPreHook(EntityCondition.is_human_player, 'on_take_damage')
@EntityPreHook(EntityCondition.is_bot_player, 'on_take_damage')
def pre_on_take_damage(args):
	global _day
	if not _day == get_boss(_day):
		info = make_object(TakeDamageInfo, args[1])
		index = index_from_pointer(args[0])
		if info.attacker == info.inflictor:
			if info.type & 2:
				_damage = info.damage
				userid = userid_from_index(index)
				attacker = userid_from_inthandle(info.attacker)
				hurter = Player.from_userid(attacker)
				if hurter.is_bot():
					_damage += (_damage / 100.0) * zombies_dmg(_day)
				info.damage = _damage

@PreEvent('server_cvar', 'player_team', 'player_disconnect', 'player_connect_client')
def pre_events(game_event):
	global _loaded
	if _loaded > 0:
		return EventAction.STOP_BROADCAST

@SayCommand('market')
def market_command(command, index, teamonly):
	global _loaded
	if _loaded > 0:
		userid = userid_from_index(index)
		main_menu(userid)
	return False

@ServerCommand('zombie_version') # Move this to version module?
def zombie_version(command):
	version.check_version()

def load():
	global _loaded
	global _value
	global _humans
	global _health
	if not GAME_NAME == 'csgo':
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
			queue_command_string('bot_quota_mode off')
			queue_command_string('mp_limitteams 0')
			queue_command_string('mp_autoteambalance 0')
			queue_command_string('bot_chatter off')
			queue_command_string('mp_humanteam ct')
			queue_command_string('sv_hudhint_sound 0')
			queue_command_string('mp_timelimit 300')
			set_download()
			echo_console(f'[Zombie Riot] Clan Tag: {clan}')
			init_loop()
			echo_console('[Zombie Riot] Author: F1N/srpg')
			echo_console(f'[Zombie Riot] Version: {version.Ver}')
			echo_console('[Zombie Riot] Loading Finished')
			queue_command_string('mp_restartgame 1')
			bomb_target(False)
			hostage_rescue(False)
			echo_console('***********************************************************')
	else:
		raise NotImplementedError(f'[Zombie Riot] This plugin doesn\'t support {GAME_NAME}!') 

def unload():
	global _loaded
	global _value
	stop_loop()
	_loaded = 0
	_value = 0
	admin.can_beacon = False
	bomb_target(True)
	hostage_rescue(True)
	for player in PlayerIter('bot'):
		player.unrestrict_weapons(*weapons)
                
def isAlive(userid):
	return not Player(index_from_userid(userid)).dead

def max_day():
	return int(_CONFIG['Days']['value'])

def get_days(value):
	val = '%s' % (value)
	return int(_CONFIG[val]['amount'])

def get_health(value):
	val = '%s' % (value)
	return int(_CONFIG[val]['health'])
    
def get_model(value):
	val = '%s' % (value)
	return _CONFIG[val]['Model']
 
def get_speed(value):
	val = '%s' % (value)
	return float(_CONFIG[val]['speed'])

def get_day_name(value):
	val = '%s' % (value)
	return _CONFIG[val]['name']

def get_boss(value):
	val = '%s' % (value)
	return int(_CONFIG['boss']['value'])

def boss_zombies(value):
	val = '%s' % (value)
	return int(_CONFIG['boss']['zombies'])

def zombies_dmg(value):
	val = '%s' % (value)
	return float(_CONFIG[val]['dmg'])

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
		player = ZombiePlayer(index_from_userid(userid))
		if player.team == 2: # Is a terrorist team
			strip_weapons(userid)
			player.restrict_weapons(*weapons)
			if not int(_day) > max_day():
				value = _day
				_health = get_health(value)
				_model = get_model(value)
				_speed = get_speed(value)
				player.health = _health
				player.set_model(Model(_model))
				player.speed = _speed
		player.noblock = True
		player.cash = 12000
		name = player.name
		if player.team == 3 and not player.is_bot():
			clan_tag.deal_spawn(userid)
			if player.is_autobuy: # Is automatic rebuy activated
				if not player.primary: # Player doesn't have rifle
					market.rebuy(userid)
			if not player.welcome_message:
				message.welcome.send(player.index, name=name, ver=version.Ver, red=red,green=green,light_green=light_green) # Welcome message
				player.welcome_message = True
			global _humans
			_humans += 1
			message.Game.send(player.index,green=green,light_green=light_green)
			message.Market.send(player.index,green=green,light_green=light_green)

@Event('round_start')
def round_start(args):
	global _show_hudhint
	global _cankill
	_show_hudhint = True
	_cankill = True
	global _loaded
	if _loaded > 0:
		queue_command_string('mp_roundtime 9')
		global _day
		global _humans
		_health = get_health(_day)
		global _value
		if get_boss(_day) == int(_day):
			_value = boss_zombies(_day)
		else:
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
		for player in PlayerIter('all'):
			player.client_command('r_screenoverlay 0')
			ZombiePlayer.from_userid(player.userid).player_target = False
		boss_day = get_boss(_day)
		if boss_day == int(_day):
			queue_command_string(f'bot_quota {boss_zombies(_day)}')
		else:
			queue_command_string('bot_quota 20')

@Event('round_end')
def round_end(args):
	global _show_hudhint
	global _cankill
	_show_hudhint = False
	_cankill = False

@Event('round_freeze_end')
def round_freeze_end(args):
	for player in PlayerIter('bot'):
		player.set_stuck(True)
		player.set_godmode(True)
		player.delay(freeze_time, un_freeze, (player.userid,))

def un_freeze(userid):
	player = Player.from_userid(userid)
	player.set_stuck(False)
	player.set_godmode(False)

@Event('player_team')
def player_team(args):
	global _loaded
	if _loaded > 0:
		global _humans
		userid = args.get_int('userid')
		if _humans > 0 and not isAlive(userid):
			if args.get_int('team') == 3: # Is ct
				player = ZombiePlayer.from_userid(userid)
				if not player.joined_team:
					player.delay(0.1, timer, (userid, 10, 1))
					player.joined_team = True
				else:
					player.delay(0.1, timer, (userid, 30, 1))

@Event('player_disconnect')
def player_disconnect(args):
	try: # This code reduces errors when server get restarted/closed
		userid = args.get_int('userid')
		if Player(index_from_userid(userid)).team == 3 and isAlive(userid):
			global _loaded
			if _loaded > 0:
				global _humans
				_humans -= 1
	except:
		pass

@Event('player_death')
def player_death(args):
	global _loaded
	if _loaded > 0:
		global _humans
		global _value
		global _day
		global _cankill
		userid = args.get_int('userid')
		attacker = args.get_int('attacker')
		victim = ZombiePlayer.from_userid(userid)
		if attacker > 0:
			clan_tag.deal_death(attacker)
			killer = ZombiePlayer.from_userid(attacker)
			if victim.userid == killer.player_target:
				killer.player_target = False
		if victim.team == 2:
			victim.is_beaconned = False
			_value -= 1
			if not _value == alive_zombies(): # Works better than if _value > 19
				Delay(0, check_value) # Call checker to ensure not getting invalid respawns
				if _humans > 0 and _cankill:
					victim.delay(0.1, respawn, (userid,))
			if _value < beacon_value:
				for player in PlayerIter(['bot', 'alive']):
					admin.beacon(player.userid)
			if _value == 0:
				Delay(0.1, won)
				for player in PlayerIter('human'):
					player.client_command('r_screenoverlay overlays/zr/humans_win.vmt')
		elif victim.team == 3: 
			_humans -= 1
			if _humans > 0:
				victim.delay(0.1, timer, (userid, 30, 1))
			if _humans == 0:
				for player in PlayerIter('human'):
					player.client_command('r_screenoverlay overlays/zr/zombies_win.vmt')

def won():
	global _day
	global _value
	if _value < 1: # Checks zombie have less than 1
		if _day == max_day():
			Delay(0.1, winner)
		_day += 1
            
def winner():
	global _day
	message.Won.send(red=red,green=green,light_green=light_green)
	mapDir = os.listdir("%s/maps" % GAME_NAME)
	next_map = random.choice(mapDir).replace('.bsp', '', 1).replace('.nav', '', 1)
	if not engine_server.is_map_valid(next_map):
		Delay(0.1, new_try)
	else:
		SayText2(f'{green}[Zombie Riot] » {light_green} Map will be changed to {green}{next_map}').send()
		Delay(11, change_map, (next_map,))
		Delay(10, tell, (1,))
		Delay(9, tell, (2,))
		Delay(8, tell, (3,))
		Delay(1, tell, (10,))
	_day = 1

def new_try():
	mapDir = os.listdir("%s/maps" % GAME_NAME)
	next_map = random.choice(mapDir).replace('.bsp', '', 1).replace('.nav', '', 1)
	if engine_server.is_map_valid(next_map):
		SayText2(f'{green}[Zombie Riot] » {light_green} Map will be changed to {green}{next_map}').send()
		Delay(11, change_map, (next_map,))
		Delay(10, tell, (1,)) # Move to hudhint?
		Delay(9, tell, (2,))
		Delay(8, tell, (3,))
		Delay(1, tell, (10,))
	else:
		Delay(1, new_try)

def check_value():
	global _cankill
	global _value
	calculated = _value - 1 # Calculate from normal amount of zombies and reduce by one
	if calculated < all_zombies():
		_cankill = False

def change_map(next_map):
	queue_command_string(f'changelevel {next_map}')

def tell(msg):
	SayText2(f'{green}[Zombie Riot] » {light_green} {msg} seconds to {green}map change!').send()

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
			player = Player.from_userid(userid)
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
	global _day
	global _show_hudhint
	for player in PlayerIter('human'):
		if info_panel:
			if _show_hudhint and player.team > 1:
				if not _day > max_day():
					hudhint(player.userid, build_hudmessage(player.userid))

def build_hudmessage(userid):
	global _value
	global _day 
	player = ZombiePlayer.from_userid(userid)
	__msg__ = f'Day {_day}/{max_day()} - {get_day_name(_day)}'
	__msg__ += f'\nZombies Left: {_value}'
	__msg__ += f'\nHumans Left: {_humans}'
	__msg__ += f'\nZombies Damage: {zombies_dmg(_day)} x'
	__msg__ += f'\nZombies Speed: {get_speed(_day)} x'
	if not player.player_target == False:
		try:
			target = Player.from_userid(player.player_target)
			if not target.dead and target.health > 0:
				__msg__ += f'\n{target.name} | {target.health}'
			else:
				player.player_target = False
		except:
			player.player_target = False

	return __msg__

@Event('player_hurt')
def player_hurt(args):
	global _loaded
	if _loaded > 0:
		if args.get_int('attacker') > 0:
			userid = args.get_int('userid')
			victim = Player.from_userid(args['userid'])
			killer = ZombiePlayer.from_userid(args['attacker'])
			if not victim.team == killer.team:
				if args.get_string('weapon') == 'hegrenade' and fire:
					burn(userid, 10)
				if not killer.is_bot():
					killer.player_target = userid
					clan_tag.deal_hurt(args.get_int('attacker'), userid)
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
		elif choice == 'return':
			info_menu(userid)

def info_menu(userid):
	menu = SimpleMenu()
	if is_queued(menu, index_from_userid(userid)):
		return
	menu.append(Text('-> 1) About Zombie Riot'))
	menu.append(Text('-' * 30))
	menu.append(Text('- Is developed by F1N/srpg'))
	menu.append(Text('- Have unique support clan tag'))
	menu.append(Text('- Have automatic rebuy for weapons'))
	menu.append(Text('- Have Potions'))
	menu.append(Text('- Current Version: %s' % version.Ver))
	menu.append(Text(' '))
	menu.append(Text('->2) About Clan Tag:'))
	menu.append(Text('- Increases your health/speed (Spawn)'))
	menu.append(Text('- Increases your health/speed (Kill)'))
	menu.append(Text('- Lowers your gravity'))
	menu.append(Text('- 10% chance for full clip'))
	menu.append(Text('- Requires: %s Clan Tag' % (clan)))
	menu.append(Text(' '))
	menu.append(Text('->3) About Potions:'))
	menu.append(Text('- Can buy with the game cash'))
	menu.append(Text('- Effect last to:'))
	menu.append(Text('- Next Round & Your Death'))
	menu.append(Text('- Speed & Health is based of:'))
	menu.append(Text('- Your current speed/health'))
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
		menu.append(SimpleOption(4, 'Admin', 'admin_menu')) # Move this option in admin module?
	menu.append(Text('-' * 30))
	menu.append(SimpleOption(0, 'Close', None))
	menu.select_callback = main_menu_callback
	menu.send(index_from_userid(userid))
