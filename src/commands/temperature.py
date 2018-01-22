def temperature(args):
    """Convert given temperature from one scale to another."""
    usage = "usage: s!(celsius/fahrenheit/kelvin) (temperature) (C/F/K)"

    if len(args[2]) != 4:
        return usage

    viewer = args[1]
    message = args[2]

    if message[2][0] == '-':
        if not message[2][1:].isdigit():
            return "@{0} - Invalid amount. 1".format(viewer)
    elif not message[2].isdigit():
        return "@{0} - Invalid amount. 2".format(viewer)

    scale_to = message[1]
    scale_from = message[3]

    if scale_to[0] == scale_from:
        return "@{0} - That's a bit silly.".format(viewer)

    temp_to = 0
    temp_from = int(message[2])

    if scale_from == 'c':
        temp_to = ((temp_from * 9) / 5) + 32 if scale_to[0] == 'f' else temp_from + 273.15
    elif scale_from == 'f':
        temp_to = ((temp_from - 32) * 5) / 9 if scale_to[0] == 'c' else (temp_from + 459.67) * 5 / 9
    elif scale_from == 'k':
        temp_to = temp_from - 273.15 if scale_to[0] == 'c' else (temp_from * 9 / 5) - 459.67

    return "{0}{1} is about {2}{3}".format(temp_from, scale_from.upper(), temp_to, scale_to[0].upper())
