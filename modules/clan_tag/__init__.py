import random
from events import Event
from players.entity import Player
from players.helpers import index_from_userid
from weapons.manager import weapon_manager
from zr import zr

@Event('player_death')
def player_death(args):
	userid = args.get_int('userid')
	attacker = args.get_int('attacker')
	if attacker > 0:
		play = Player(index_from_userid(attacker))
		if not play.is_bot() and play.clan_tag in zr.clan:
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
			if not play.is_bot() and play.clan_tag in zr.clan:
				chance = 10
				if random.randint(1, 100) <= chance:
					weapon = play.active_weapon
					primary = play.primary
					secondary = play.secondary
					max_clip = weapon_manager[weapon.classname].clip
					if weapon == primary:
						weapon.clip = max_clip
					elif weapon == secondary:
						weapon.clip = max_clip  
