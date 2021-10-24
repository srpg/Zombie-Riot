from events import Event
from players.entity import Player
from players.helpers import index_from_userid, userid_from_index
from menus import SimpleMenu, SimpleOption, Text
from weapons.manager import weapon_manager
from zr.modules import message
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
	menu.append(SimpleOption(7, 'Full Bullets[14000$]', 'full_bullets', player.cash >= 14000 and zr.isAlive(userid), player.cash >= 14000 and zr.isAlive(userid)))
	menu.append(SimpleOption(8, 'Infinity Bullets[16000$]', 'infi_bullets', player.cash >= 16000 and zr.isAlive(userid), player.cash >= 16000 and zr.isAlive(userid)))
	menu.append(SimpleOption(9, 'Respawn[6000$]', 'respawn', player.cash >= 6000 and not zr.isAlive(userid) and zr._humans > 0, player.cash >= 6000 and not zr.isAlive(userid) and zr._humans > 0))
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
				if player.cash >= 12000:
					player.health += player.max_health
					player.cash -= 12000
					message.Potion.send(_index, type="full health", cost=12000, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					pass # Todo add a message when don't have enough cash
			else:
				message.Alive.send(_index, type="health potion", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == 'half_health':
			if zr.isAlive(userid):
				if player.cash >= 6000:
					bonus = int(player.max_health / 2)
					player.health += bonus
					player.cash -= 6000
					message.Potion.send(_index, type="half health", cost=6000, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					pass # Todo add a message when don't have enough cash
			else:
				message.Alive.send(_index, type="health potion", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == '25_health':
			if zr.isAlive(userid):
				if player.cash >= 3000:
					bonus = int(player.max_health / 4)
					player.health += bonus
					player.cash -= 3000
					message.Potion.send(_index, type="25% health", cost=3000, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					pass # Todo add a message when don't have enough cash
			else:
				message.Alive.send(_index, type="health potion", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == 'full_bullets':
			if zr.isAlive(userid):
				if player.cash >= 14000:
					if player.get_active_weapon().classname.replace('weapon_', '', 1) in zr.secondaries() + zr.rifles():
						player.cash -= 14000
						weapon = player.get_active_weapon()
						weapon.clip = weapon_manager[weapon.classname].clip
						weapon.ammo = weapon_manager[weapon.classname].maxammo
						message.Potion.send(_index, type="full bullets", red=zr.red,cost=14000, green=zr.green,light_green=zr.light_green)
					else:
						message.Invalid.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					pass # Todo add a message when don't have enough cash
			else:
				message.Alive.send(_index, type="fullbullets", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == '25_speed':
			if zr.isAlive(userid):
				if player.cash >= 3000:
					bonus = player.speed / 4
					player.speed += bonus
					player.cash -= 3000
					message.Potion.send(_index, type="25% speed", cost=3000, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					pass # Todo add a message when don't have enough cash
			else:
				message.Alive.send(_index, type="speed potion", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == 'half_speed':
			if zr.isAlive(userid):
				if player.cash >= 6000:
					bonus = player.speed / 2
					player.speed += bonus
					player.cash -= 6000
					message.Potion.send(_index, type="half speed", cost=6000, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					pass # Todo add a message when don't have enough cash
			else:
				message.Alive.send(_index, type="speed potion", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == 'full_speed':
			if zr.isAlive(userid):
				if player.cash >= 12000:
					player.speed += player.speed
					player.cash -= 12000
					message.Potion.send(_index, type="full speed", cost=12000, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					pass # Todo add a message when don't have enough cash
			else:
				message.Alive.send(_index, type="speed potion", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == 'infi_bullets':
			if zr.isAlive(userid):
				if player.cash >= 16000:
					if player.get_active_weapon().classname.replace('weapon_', '', 1) in zr.secondaries() + zr.rifles():
						player.get_active_weapon().clip = weapon_manager[player.get_active_weapon().classname].clip
						player.cash -= 16000
						user = zr.ZombiePlayer.from_userid(userid)
						user.infinity_bullets = True
						message.Potion.send(_index, type="infinity bullets", cost=16000, red=zr.red,green=zr.green,light_green=zr.light_green)
					else:
						message.Invalid.send(_index, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					pass # Todo add a message when don't have enough cash
			else:
				message.Alive.send(_index, type="infinity bullets potion", red=zr.red,green=zr.green,light_green=zr.light_green)
		elif choice == 'respawn':
			if not zr.isAlive(userid) and zr._humans > 0:
				if player.cash >= 6000:
					player.delay(0.1, zr.respawn, (userid,))
					player.cash -= 6000
					message.Potion.send(_index, type="respawn", cost=6000, red=zr.red,green=zr.green,light_green=zr.light_green)
				else:
					pass # Todo add a message when don't have enough cash
			else:
				message.Dead.send(_index, green=zr.green,light_green=zr.light_green)

@Event('round_end')
def round_end(args):
	for i in zr.getUseridList():
		user = zr.ZombiePlayer.from_userid(i)
		user.infinity_bullets = False

@Event('round_start')
def round_start(args):
	for i in zr.getUseridList():
		user = zr.ZombiePlayer.from_userid(i)
		user.infinity_bullets = False

@Event('player_death')
def player_death(args):
	victim = zr.ZombiePlayer.from_userid(args['userid'])
	victim.infinity_bullets = False

@Event('weapon_fire')
def weapon_fire(args):
	userid = args.get_int('userid')
	user = zr.ZombiePlayer.from_userid(userid)
	if user.infinity_bullets:
		player = Player(index_from_userid(userid))
		weapon = player.get_active_weapon()
		if player.get_active_weapon().classname.replace('weapon_', '', 1) in zr.secondaries() + zr.rifles():
			weapon.clip += 1
