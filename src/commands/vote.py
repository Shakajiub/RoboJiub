
def vote(args):
    return "TODO - This command."

# A mod could start the vote with something like:
# "s!vote option1 option2 option_with_more_words 120"

# If the last parameter is an integer, use it for the duration (in seconds) (default could be a minute)
# RoboJiub will then announce that a vote has been started with given options, something like this:

# "A vote has started! Type '1' for {option1}, '2'
# for {option2} or '3' for {option_with_more_words}.
# Vote closes in 120 seconds!"

# Chat will then look like this for a while:
# user: 2
# user: 3
# user: 1
# user: 4 Kappa
# user: 1

# Repeating the message every 30 seconds or so would probably be good.
# When the timer ends, RoboJiub should announce the votes each choice received:

# "The vote has ended! Winner: {option2} (x votes)!
# {option1} got (y) votes and {option_with_more_words}
# got (z) votes."

# "s!vote close" could be useful to end the vote prematurely.

# This command is not currently possible with the way the bot is set up to parse chat messages,
# so some kind of hook would need to be setup to redirect every message here for parsing during
# the vote. This would make every other command unusable during the vote, which would actually
# be very much desired. A hook like this would be very useful for future commands.
