from enum import Enum


PTYPE = Enum("PType", ["desert", "fire", "water", "terran", "gas", "ice"])
PTYPE_EMOJI = ["", "🏜️", "🔥", "💧", "🪨", "🪐", "🧊"]

PORDER = [
    (PTYPE.desert, 1, ""),
    (PTYPE.fire, 1, ""),
    (PTYPE.water, 1, ""),
    (PTYPE.terran, 1, ""),
    (PTYPE.gas, 2, ""),
    (PTYPE.terran, 3, ""),
    (PTYPE.fire, 3, ""),
    (PTYPE.water, 3, ""),
    (PTYPE.gas, 4, ""),
    (PTYPE.desert, 3, ""),
    (PTYPE.fire, 4, ""),
    (PTYPE.desert, 4, ""),
    (PTYPE.water, 4, ""),
    (PTYPE.terran, 4, ""),
    (PTYPE.ice, 4, "a"),
    (PTYPE.ice, 4, "b")
]


def upgrade_cost(cur_lv: int):
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


def upgrade_duration(cur_lv: int):
    """
    Returns the number of minutes for a planet upgrade given its current level.
    """
    if cur_lv < 3:
        return 0
    elif cur_lv < 13:
        return [1, 2, 5, 20, 60, 4*60, 8*60, 16*60, 24*60, 36*60][cur_lv - 3]
    else:
        return min(12*60 * (cur_lv - 8), 14*24*60)


def credit_storage(cur_lv: int):
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


def hydro_storage(cur_lv: int):
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

