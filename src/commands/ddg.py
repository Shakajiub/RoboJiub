import json

from urllib2 import urlopen, URLError

def ddg(args):
    """Get the abstract text from DuckDuckGo api for given query."""
    usage = "s!ddg (query)"

    if len(args[2]) < 2:
        return usage

    queue = args[0]
    viewer = args[1]
    message = args[2]

    del message[0]
    query = "+".join(message)
    result = "@{0} - Sorry, I could not find anything with that query.".format(viewer)

    try:
        response = urlopen('https://api.duckduckgo.com/?q={0}&format=json'.format(query))
        parsed_json = json.loads(response.read())

        source = " Source: ???"
        abstract = parsed_json['Abstract']

        if len(parsed_json['AbstractURL']) > 0:
            source = " Source: " + parsed_json['AbstractURL']

        if len(abstract) > 0:
            if (len(abstract) > (420 - len(source))):
                result = abstract[:(420 - len(source))] + " (...)" + source
            else: result = abstract + source

    except KeyError:
        queue.put(("ddg() - Error parsing DDG json!", 'BG_error'))
    except URLError:
        queue.put(("ddg() - Could not get query from DDG!", 'BG_error'))

    return result
