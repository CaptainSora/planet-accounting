from json import load
from math import ceil


ART_DROPS = None
RESEARCH = None

def load_info():
    global ART_DROPS, RESEARCH
    if ART_DROPS is None:
        with open("art_drops.json") as f:
            ART_DROPS = load(f)
    if RESEARCH is None:
        with open("research_info.json") as f:
            RESEARCH = load(f)


async def artifact_count(
    inter, art_level, trade, mining, weapons, shields, support
):
    load_info()

    def parse(arg):
        return [int(num) if num.isdecimal() else -1 for num in arg.split()]
    
    bps = [
        parse(trade), parse(mining),
        parse(weapons), parse(shields),
        parse(support)
    ]

    given = [len(cat) for cat in bps]
    order = ["Trade", "Mining", "Weapons", "Shields", "Support"]
    expected = [len(RESEARCH[t]) for t in order]

    msg = ""
    for i in range(len(order)):
        if given[i] != expected[i]:
            msg += (
                f'Expected {expected[i]} {order[i]} modules, '
                f'recieved {given[i]}.\n'
            )
    if msg:
        await inter.response.send_message(msg.strip())
        return
    
    # List of bps remaining, sorted by level and type
    blues = [[] for _ in range(11)]
    orbs = [[] for _ in range(11)]
    tets = [[] for _ in range(11)]

    def count_missing(art_type, bp_counts, art_color):
        for i in range(len(RESEARCH[art_type])):
            name, level, req = RESEARCH[art_type][i]
            if bp_counts[i] > -1:
                art_color[level - 1].append([max(0, req - bp_counts[i]), name])
    
    count_missing("Trade", bps[0], blues)
    count_missing("Mining", bps[1], blues)
    count_missing("Weapons", bps[2], orbs)
    count_missing("Shields", bps[3], orbs)
    count_missing("Support", bps[4], tets)

    # color = [blues, blues, orbs, orbs, tets]
    # for i in range(len(order)):
    #     for j in range(len(RESEARCH[order[i]])):
    #         _, level, req = RESEARCH[order[i]][j]
    #         if bps[i][j] > -1:
    #             color[i][level - 1].append(max(0, req - bps[i][j]))
    
    def compute_arts(art_color_str, art_color, emoji):
        msg = ""
        for level in range(len(art_color)):
            if not art_color[level]:
                continue
            msg += f"\nr{level+1}: "
            if level + 1 > art_level:
                msg += ":warning: Will not recieve BPs for this level!"
                continue
            try:
                avg_drop = sum(ART_DROPS[art_color_str][art_level - 1][level])
                avg_drop *= 0.6  # Average plus 20% bonus
                min_drop = ART_DROPS[art_color_str][art_level - 1][level][0]
                min_drop *= 1.2  # 20% bonus
            except IndexError:
                print(f"IndexError on r{level} {art_color_str}")
            else:
                amts, names = list(zip(*art_color[level]))
                msg += str(int(sum(
                    [ceil(j / avg_drop) for j in amts]
                )))
                msg += f" ({', '.join(names)})"
            
        if not msg:
            msg += " Complete!\n"
        
        return f"\n{emoji} {art_color_str}:" + msg + "\n"
        
    emojis = (
        inter.client.get_emoji(1014264731487440916),
        inter.client.get_emoji(1014264732867366942),
        inter.client.get_emoji(1014264730350792714)
    )

    await inter.response.send_message(
        f"Level {art_level} arts:" +
        compute_arts("Blues", blues, emojis[0]) +
        compute_arts("Orbs", orbs, emojis[1]) +
        compute_arts("Tets", tets, emojis[2])
    )

    # art_color_str = ("Blues", "Orbs", "Tets")
    # art_colors = (blues, orbs, tets)

    # for emoji, cstr, color in zip(emojis, art_color_str, art_colors):
    #     compute_arts(cstr, color)
    #     msg += f"\n{emoji} {cstr}:"
    #     if sum(color) > 0:
    #         msg += "\n"
    #         for i in range(len(color)):
    #             if color[i] > 0:
    #                 msg += f"r{i+1}: {color[i]}\n"
    #     else:
    #         msg += " Complete!\n"
    #     if cstr in warn:
    #         msg += ":warning: Warning: still missing higher level BPs!\n"

    # msg += ":blue7: Blues:"
    # if sum(blues) > 0:
    #     msg += "\n"
    #     for i in range(len(blues)):
    #         msg += f"r{i+1}: {blues[i]}\n"
    # else:
    #     msg += " Complete!\n"
    # if "Blues" in warn:
    #     msg += ":warning: Warning: still missing higher level BPs!\n"
    
    # msg += "\n:orb7: Orbs:"
    # if sum(orbs) > 0:
    #     msg += "\n"
    #     for i in range(len(orbs)):
    #         msg += f"r{i+1}: {orbs[i]}\n"
    # else:
    #     msg += " Complete!\n"
    # if "Orbs" in warn:
    #     msg += ":warning: Warning: still missing higher level BPs!\n"

    # msg += "\n:tet7: Tets:"
    # if sum(tets) > 0:
    #     msg += "\n"
    #     for i in range(len(tets)):
    #         msg += f"r{i+1}: {tets[i]}\n"
    # else:
    #     msg += " Complete!\n"
    # if "Tets" in warn:
    #     msg += ":warning: Warning: still missing higher level BPs!\n"
    
    # await inter.response.send_message(msg.strip())
