import random
from players.entity import Player
from weapons.manager import weapon_manager
from zr import zr

def deal_spawn(userid):
	player = Player.from_userid(userid)
	if player.clan_tag in zr.server_clan:
		player.max_health += 25
		player.health = player.max_health
		player.speed += 0.10 # Increases 10% of speed
		base = 1
		player.gravity = base
		player.gravity -= 0.10 # Lowers gravity 10%

def deal_death(attacker):
	if attacker > 0:
		play = Player.from_userid(attacker)
		if not play.is_bot() and play.clan_tag in zr.server_clan:
			if not play.max_health > 145 and not play.health > 145:
				play.max_health += 5:
				play.health += 5
			if not play.speed > 1.5:
				play.speed += 5
				play.speed -= 4.95


def deal_hurt(attacker, userid):
	if attacker > 0:
		victim = Player.from_userid(userid)
		hurter = Player.from_userid(attacker)
		if not victim.team == hurter.team:    
			if hurter.get_active_weapon().classname.replace('weapon_', '', 1) in zr.secondaries() + zr.rifles():
				if not hurter.is_bot() and hurter.clan_tag in zr.server_clan and not hurter.dead:
					if random.randint(1, 100) <= 10:
						weapon = hurter.get_active_weapon()
						weapon.clip = weapon_manager[weapon.classname].clip
