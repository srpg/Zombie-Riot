import random
from events import Event
from players.entity import Player
from players.helpers import index_from_userid
from weapons.manager import weapon_manager
from zr import zr

@Event('player_spawn')
def player_spawn(args):
	userid = args.get_int('userid')
	player = Player(index_from_userid(userid))
	if player.clan_tag in zr.server_clan:
		player.max_health += 25
		player.health = player.max_health
		player.speed += 0.10 # Increases 10% of speed
		base = 1
		player.gravity = base
		player.gravity -= 0.10 # Lowers gravity 10%

@Event('player_death')
def player_death(args):
	userid = args.get_int('userid')
	attacker = args.get_int('attacker')
	if attacker > 0:
		play = Player(index_from_userid(attacker))
		if not play.is_bot() and play.clan_tag in zr.server_clan:
			if not play.max_health > 145:
				play.max_health += 5
			if not play.health > 145:
				play.health += 5
			if not play.speed > 1.5:
				play.speed += 5
				play.speed -= 4.95


@Event('player_hurt')
def player_hurt(args):
	userid = args.get_int('userid')
	attacker = args.get_int('attacker')
	if attacker > 0:
		if not Player(index_from_userid(userid)).team == Player(index_from_userid(attacker)).team:    
			play = Player(index_from_userid(attacker))
			if play.get_active_weapon() in zr.secondaries() + zr.rifles():
				if not play.is_bot() and play.clan_tag in zr.server_clan:
					chance = 10
					if random.randint(1, 100) <= chance:
						weapon = play.get_active_weapon()
						weapon.clip = weapon_manager[weapon.classname].clip
