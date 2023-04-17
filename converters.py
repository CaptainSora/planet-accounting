def duration(inter, argument):
    """
    Takes in a string of of the form "xdyhzm" where:
    - x, y, z are integers
    - d is a string representing days
    - h is a string representing hours
    - m is a string representing minutes
    - d, h, m can be followed by any whitespace and be of any capitalization

    Returns the duration in seconds.
    """
    if not isinstance(argument, str):
        return 0
    # Valid strings
    daystr = ["d", "day", "days"]
    hourstr = ["h", "hr", "hrs", "hour", "hours"]
    minstr = ["m", "min", "mins", "minute", "minutes"]
    valid = [daystr, hourstr, minstr]

    # Clean input
    timestr = "".join(argument.lower().split())
    duration = [0, 0, 0]  # D H M

    # Search
    for i in range(len(valid)):
        for vstr in valid[i][::-1]:
            if timestr.find(vstr) > 0:
                d, timestr = timestr.split(vstr, 1)
                duration[i] = d
                break
    
    # Validate
    try:
        d, h, m = [int(d) for d in duration]
    except:
        return 0
    else:
        return 60 * (60 * ((24 * d) + h) + m)


def to_dhm(seconds, ignore_min=False):
    """
    Returns a duration in seconds into a xd yh zm string.
    Truncates any sub-minute precision.
    """
    d, s = divmod(seconds, 24 * 60 * 60)
    h, s = divmod(s, 60 * 60)
    m, s = divmod(s, 60)
    outstr = []
    if d > 0:
        outstr.append(f"{d}d")
    if d + h > 0:
        outstr.append(f"{h}h")
    if not ignore_min or not outstr:
        outstr.append(f"{m}m")

    return " ".join(outstr)


def numformat(num):
    """
    Formats a positive integer keeping 3 sig figs, and using k/m notation.
    """
    num = round(num, -1 * (len(str(num)) - 3))
    if len(str(num)) < 4:
        return str(num)
    elif len(str(num)) < 7:
        return f"{num/1000:.3g}k"
    elif len(str(num)) < 10:
        return f"{num/1000000:.3g}m"
    else:
        return f"{num // 1000000:,}m"
