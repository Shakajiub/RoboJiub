from random import choice

def question(args):
    """Return with a string answering a yes/no question."""
    viewer = args[1]
    #user_input = args[2]
    response = choice(["Yes", "No", "Yep", "Nope", "Definitely", "No way", "I dunno", "No idea"])
    return "@{0} - {1}.".format(viewer, response)
