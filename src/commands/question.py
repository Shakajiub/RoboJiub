from random import choice

def question(args):
    """Answer a yes/no question."""
    #usage = "@robojiub (yes/no question)"

    # TODO - More advanced conversations, in the style of 'CleverBot'

    viewer = args[1]
    response = choice(["Yes", "No", "Yep", "Nope", "Definitely", "No way", "No idea"])

    return "@{0} - {1}.".format(viewer, response)
