from random import choice

def question(args):
    """Answer a yes/no question."""
    #usage = "@robojiub (yes/no question)"

    bots = ["StreamElements", "Nightbot"]
    viewer = args[1]

    if viewer in bots:
        return False

    response = choice(["Yes", "No", "Yep", "Nope", "Definitely", "No way", "No idea"])
    return "@{0} - {1}.".format(viewer, response)
