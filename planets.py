from enum import Enum
from json import dump, load
from time import time

from converters import numformat, to_dhm


PTYPE = Enum("PTYPE", ["Desert", "Fire", "Water", "Terran", "Gas", "Ice"])
PTYPE_EMOJI = ["", "🏜️", "🔥", "💧", "🌎", "🪐", "🧊"]

PORDER = [
    (PTYPE.Desert, 1, ""),
    (PTYPE.Fire,   1, ""),
    (PTYPE.Water,  1, ""),
    (PTYPE.Terran, 1, ""),
    (PTYPE.Gas,    2, ""),
    (PTYPE.Terran, 3, ""),
    (PTYPE.Fire,   3, ""),
    (PTYPE.Water,  3, ""),
    (PTYPE.Gas,    4, ""),
    (PTYPE.Desert, 3, ""),
    (PTYPE.Fire,   4, ""),
    (PTYPE.Desert, 4, ""),
    (PTYPE.Water,  4, ""),
    (PTYPE.Terran, 4, ""),
    (PTYPE.Ice,    4, "a"),
    (PTYPE.Ice,    4, "b")
]

PLANET_SHIPMENTS = None
PLAYER_INFO = None

### Planets

def create_player_if_not_exists(caller_id):
    """
    Creates a player if they do not already exist.
    Default values as shown.
    """
    global PLAYER_INFO
    
    _read_player_info()
    if caller_id not in PLAYER_INFO:
        PLAYER_INFO[caller_id] = {
            # [Name, Level, Upgrade Until]
            "planets": [[None, 0, None] for _ in range(len(PORDER))],
            "settings": {
                "ping_when_upgraded": False
            }
        }
        _write_player_info()


async def upgrade_planet(inter, planet_name, duration):
    """
    Sets a player's planet as upgrading.
    Takes duration in seconds.
    """
    global PLAYER_INFO
    
    caller_id = str(inter.author.id)
    create_player_if_not_exists(caller_id)
    
    # Validate planet
    planets = PLAYER_INFO[caller_id]["planets"]
    pnames = list(zip(*planets))[0]
    if planet_name not in pnames:
        await inter.response.send_message(
            "Planet name not found. Make sure the planet is added first."
        )
        return
    
    pnum = pnames.index(planet_name)

    # Validate level
    if planets[pnum][1] >= _max_planet_level(PORDER[pnum][1]):
        await inter.response.send_message(
            "This planet is already at max level!"
        )
        return

    # Validate duration
    if duration <= 0:
        duration = _upgrade_duration(planets[pnum][1])
    
    # Write to file
    old_upgrade_time = planets[pnum][2]
    planets[pnum][2] = int(time()) + duration
    _write_player_info()

    # Respond
    new_dhm = to_dhm(duration)
    _, fut_cc, _, _ = _compute_cap(planets)

    if old_upgrade_time is not None:
        old_dhm = to_dhm(old_upgrade_time - int(time()))
        await inter.response.send_message(
            f"Changed the upgrade timer for Tier "
            f"{PORDER[pnum][1]}{PORDER[pnum][2]} "
            f"{PORDER[pnum][0].name} planet __{planet_name}__ from "
            f"<t:{old_upgrade_time}:F> ({old_dhm}) to "
            f"<t:{planets[pnum][2]}:F> ({new_dhm})."
        )
    else:
        await inter.response.send_message(
            f"Started the upgrade timer for Tier "
            f"{PORDER[pnum][1]}{PORDER[pnum][2]} "
            f"{PORDER[pnum][0].name} planet __{planet_name}__ to finish at "
            f"<t:{planets[pnum][2]}:F> ({new_dhm}).\n"
            f"Upgraded Credit Cap is now {numformat(fut_cc)} CR."
        )


async def shift_upgrade_times(inter, duration):
    """
    Shifts all of a player's planet upgrade times by a fixed duration.
    Used to compensate for TM usage.
    """
    global PLAYER_INFO
    
    caller_id = str(inter.author.id)
    create_player_if_not_exists(caller_id)

    # Validate duration
    if duration <= 0:
        await inter.response.send_message(
            "Need to shift by a non-zero duration."
        )
        return

    # Shift
    changed = False
    for i in range(len(PORDER)):
        if PLAYER_INFO[caller_id]["planets"][i][2] is not None:
            PLAYER_INFO[caller_id]["planets"][i][2] -= duration
            changed = True
    
    if changed:
        _write_player_info()
        dhm = to_dhm(duration)
        await inter.response.send_message(
            f"Shifted all upgrade timers ahead by {dhm}."
        )
    else:
        await inter.response.send_message(
            "No upgrade timers to shift."
        )


async def add_planet(inter, planet_name, level, ptype, tier, disc):
    """
    Adds a planet to a player's info, creating the player if needed.
    Renames/replaces the level of a planet if it already exists.
    """
    global PLAYER_INFO
    
    caller_id = str(inter.author.id)
    create_player_if_not_exists(caller_id)

    # Validate Tier 4 Ice
    if PTYPE(ptype) == PTYPE.Ice and tier == 4:
        if disc == "":
            await inter.response.send_message(
                "Must specify a discriminator a/b for Tier 4 Ice planets."
            )
            return
    else:
        # Clear discriminator
        disc = ""
    
    # Validate remaining
    planet = (PTYPE(ptype), tier, disc)
    if planet not in PORDER:
        await inter.response.send_message(
            "Invalid planet type/tier."
        )
        return
    
    # Write to file
    pnum = PORDER.index(planet)
    old_planet = PLAYER_INFO[caller_id]["planets"][pnum]
    PLAYER_INFO[caller_id]["planets"][pnum] = [planet_name, level, None]
    _write_player_info()

    # Respond
    if old_planet[0] is None:
        await inter.response.send_message(
            f"Added Tier {tier}{disc} {PTYPE(ptype).name} planet "
            f"__{planet_name}__ at level {level}."
        )
    else:
        await inter.response.send_message(
            f"Replaced Tier {tier}{disc} {PTYPE(ptype).name} planet "
            f"__{old_planet[0]}__ at level {old_planet[1]} with "
            f"__{planet_name}__ at level {level}."
        )


async def list_planets(inter):
    """
    Lists all planets, levels, and upgrade status.
    """
    caller_id = str(inter.author.id)
    create_player_if_not_exists(caller_id)

    p = PLAYER_INFO[caller_id]["planets"]

    output = []
    for i in range(len(PORDER)):
        # Conditional markers
        upgr_emoji, max_emoji = "", ""
        if p[i][2] is not None:
            upgr_emoji = f"🛠️ ({to_dhm(p[i][2] - int(time()))})"
        if p[i][1] == _max_planet_level(PORDER[i][1]):
            max_emoji = "✨"
        # Create string
        outstr = "".join([
            PTYPE_EMOJI[PORDER[i][0].value], str(PORDER[i][1]), PORDER[i][2],
            " - __", str(p[i][0]), "__ (Level ",
            str(p[i][1]), "/", str(_max_planet_level(PORDER[i][1])), ") ",
            upgr_emoji,
            max_emoji
        ])
        # print(outstr)
        output.append(outstr)
    
    # await inter.response.send_message("bing")
    await inter.response.send_message("\n".join(output))


async def upgrade_details(inter, raw=False):
    """
    Lists upgrading planets and details.
    Suggests next planet upgrade.
    """
    caller_id = str(inter.author.id)
    create_player_if_not_exists(caller_id)

    planets = PLAYER_INFO[caller_id]["planets"]

    # Counters and output
    output = []
    next_upgr = []

    # Check all planets
    for i in range(len(PORDER)):
        ptype, ptier, disc = PORDER[i]
        pname, level, upgr_until = planets[i]
        cc = _credit_storage(level)
        hc = _hydro_storage(level)

        if upgr_until is not None:
            dhm = to_dhm(upgr_until - int(time()))
            output.append((
                f"{PTYPE_EMOJI[ptype.value]}{ptier}{disc} __{pname}__ "
                f"({level} -> {level + 1}):\n"
                f"- <t:{upgr_until}:f> ({dhm})",
                upgr_until - int(time())
            ))
        else:
            if level < _max_planet_level(ptier):
                cost = _upgrade_cost(level)
                cr_incr = (
                    _shipment_value(ptype, ptier, level + 1) - 
                    _shipment_value(ptype, ptier, level)
                )
                cc_incr = _credit_storage(level + 1) - cc
                next_upgr.append([
                    ptype.name, str(ptier) + disc, pname, level, cost,
                    cr_incr/cost, cc_incr/cost
                ])
    
    # Select next planet to upgrade
    unmaxed = bool(next_upgr)
    if unmaxed:
        next_upgr = sorted(
            next_upgr,
            key=lambda t: (t[6], t[5]), reverse=True
        )[0]
        next_upgr = "\nSuggested Upgrade:\n" + " ".join([
            "Tier", next_upgr[1], next_upgr[0] + ":", next_upgr[2],
            "(Level", str(next_upgr[3]), "->", str(next_upgr[3] + 1) + ")",
            f"- {numformat(next_upgr[4])} CR", "/",
            to_dhm(_upgrade_duration(next_upgr[3]), ignore_min=True)
        ])
    
    # Clean upgrades
    upgrading = bool(output)
    if output:
        output.sort(key=lambda t: t[1])
        output = "\n\n" + "\n\n".join(list(zip(*output))[0]) + "\n\n"
    else:
        output = ""

    # Compute caps
    cur_cc, fut_cc, cur_hc, fut_hc = _compute_cap(planets)
    
    upgraded_cap = (
        f"Upgraded Credit Cap: {numformat(fut_cc)} CR\n"
        f"Upgraded Hydro Cap: {numformat(fut_hc)} H\n"
    ) if upgrading else ""

    # Respond
    await inter.response.send_message(
        f"Current Credit Cap: {numformat(cur_cc)} CR\n"
        f"Current Hydro Cap: {numformat(cur_hc)} H"
        f"{output}"
        f"{upgraded_cap}"
        f"{next_upgr}"
    )


### Settings

async def change_bool_settings(inter, setting, flag):
    """
    Changes player boolean settings.
    """
    global PLAYER_INFO

    caller_id = str(inter.author.id)
    create_player_if_not_exists(caller_id)

    PLAYER_INFO[caller_id]["settings"][setting] = flag
    _write_player_info()

    await inter.response.send_message(
        f"Set {setting.replace('_', ' ').title()} to {flag}."
    )


async def view_settings(inter):
    """
    Lists all player settings.
    """
    global PLAYER_INFO
    
    caller_id = str(inter.author.id)
    create_player_if_not_exists(caller_id)

    output = []
    
    for k, v in PLAYER_INFO[caller_id]["settings"].items():
        output.append(f"{k.replace('_', ' ').title()}: {v}")
    
    await inter.response.send_message("\n".join(output))


### Checks

async def check_planet_upgrade_status(channel):
    global PLAYER_INFO

    _read_player_info()
    cur_time = int(time())
    changed = False

    for pid in PLAYER_INFO:
        for i in range(len(PORDER)):
            planet = PLAYER_INFO[pid]["planets"][i]
            if planet[2] is not None and planet[2] <= cur_time:
                # Edit
                PLAYER_INFO[pid]["planets"][i] = \
                    [planet[0], planet[1] + 1, None]
                changed = True
                # Notify
                if PLAYER_INFO[pid]["settings"]["ping_when_upgraded"]:
                    cur_cc, _, _, _ = _compute_cap(PLAYER_INFO[pid]["planets"])
                    await channel.send(
                        f"<@{pid}> {planet[0]} completed upgrade to level "
                        f"{planet[1] + 1}.\n"
                        f"Current Credit Cap is now {numformat(cur_cc)} CR."
                    )
    
    if changed:
        _write_player_info()


### Private planet helper functions

def _read_player_info():
    global PLAYER_INFO
    if PLAYER_INFO is None:
        with open("player_info.json") as f:
            PLAYER_INFO = load(f)


def _write_player_info():
    global PLAYER_INFO
    if PLAYER_INFO is not None:
        with open("player_info.json", "w") as f:
            dump(PLAYER_INFO, f)


def _upgrade_cost(cur_lv: int):
    """
    Returns the cost to upgrade a planet given its current level.
    """
    if cur_lv < 0:
        return 0
    elif cur_lv < 8:
        return [0, 50, 200, 400, 800, 2000, 4000, 8000][cur_lv]
    elif cur_lv < 13:
        return 10000 * (cur_lv - 7)
    elif cur_lv < 19:
        return 25000 * (cur_lv - 10)
    elif cur_lv < 25:
        return [250, 300, 400, 500, 600, 800][cur_lv - 19] * 1000
    elif cur_lv < 33:
        return 250000 * (cur_lv - 21)
    elif cur_lv < 50:
        return 500000 * (cur_lv - 27)
    else:
        return 0


def _upgrade_duration(cur_lv: int):
    """
    Returns the number of seconds for a planet upgrade given its current level.
    """
    if cur_lv < 0:
        return 0
    elif cur_lv < 13:
        return [
            0, 3, 30, 60, 120, 300, 1200, 3600, 4*3600, 8*3600, 16*3600,
            24*3600, 36*3600
        ][cur_lv]
    else:
        return min(12*3600 * (cur_lv - 8), 14*24*3600)


def _credit_storage(cur_lv: int):
    """
    Returns the current credit storage for a planet given its level.
    """
    if cur_lv < 0:
        return 0
    elif cur_lv < 18:
        return [
            0, 1000, 1400, 1800, 3000, 4000, 5000, 6000, 7500, 10000, 13000,
            16000, 20000, 24000, 28000, 35000, 45000, 65000
        ][cur_lv]
    else:
        return min(40000 * (cur_lv - 16) + 10000, 1370000)


def _hydro_storage(cur_lv: int):
    """
    Returns the current hydro storage for a planet given its level.
    Note that fire planets do not increase hydro storage.
    """
    if cur_lv < 0:
        return 0
    elif cur_lv < 20:
        return [
            0, 200, 260, 340, 450, 570, 750, 960, 1250, 1600, 2100, 2750, 3600,
            5000, 7000, 9000, 11000, 13000, 15000, 17000
        ][cur_lv]
    else:
        return min(1000 * (cur_lv - 1), 49000)


def _shipment_value(ptype: PTYPE, ptier: int, cur_lv: int):
    """
    Returns the hourly shipment value for the planet.
    """
    global PLANET_SHIPMENTS

    if ptier < 1 or ptier > 4:
        print("Invalid tier.")
        return 0
    
    if PLANET_SHIPMENTS is None:
        with open("planet_shipments.json") as f:
            PLANET_SHIPMENTS = load(f)
    
    try:
        return PLANET_SHIPMENTS[ptype.name][ptier - 1][cur_lv - 1]
    except IndexError as e:
        print(e)
        print(
            f"Failed to get shipments of {ptype.name} Tier {ptier} "
            f"Level {cur_lv}."
        )
    except Exception as e:
        print(e)
    
    return 0


def _max_planet_level(ptier: int):
    """
    Returns the maximum level of a planet given its tier.
    """
    if ptier < 1 or ptier > 4:
        print("Invalid tier.")
        return 0
    return [0, 15, 20, 35, 50][ptier]


def _compute_cap(planets: list):
    """
    Returns the current and upgraded credit and hydro cap.
    """
    # Counters
    cur_cc, fut_cc = 0, 0
    cur_hc, fut_hc = 0, 0

    # Check all planets
    for i in range(len(PORDER)):
        ptype, ptier, disc = PORDER[i]
        pname, level, upgr_until = planets[i]
        cc = _credit_storage(level)
        hc = _hydro_storage(level) if ptype != PTYPE.Fire else 0

        cur_cc += cc
        cur_hc += hc

        if upgr_until is not None:
            fut_cc += _credit_storage(level + 1)
            fut_hc += _hydro_storage(level + 1) if ptype != PTYPE.Fire else 0
        else:
            fut_cc += cc
            fut_hc += hc
    
    return cur_cc, fut_cc, cur_hc, fut_hc
