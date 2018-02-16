# -*- coding: utf-8 -*-
import sys

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer

chatbot = None

def question(args):
    """Answer any given question somewhat sensibly."""
    #usage = "@robojiub (question)"
    global chatbot

    queue = args[0]
    viewer = args[1]
    message = args[2]

    del message[0] # "s!question"
    del message[0] # "@robojiub"

    bots = ["streamelements", "nightbot", "pannebot"]
    if viewer in bots:
        return None

    if message[0] == "export":
        if viewer != "shakajiub":
            return None

        if chatbot == None:
            init_bot(True)

        chatbot.trainer.export_for_training('./database_export.yml')
        return "@{0} - Database exported!".format(viewer)

    elif message[0] == "train":
        if viewer != "shakajiub":
            return None

        if "<" not in message or ">" not in message:
            init_bot(False)
            chatbot.set_trainer(ChatterBotCorpusTrainer)
            chatbot.train("training.conversations")
            #chatbot.train("training.emotions")
            chatbot.train("training.greetings")
            chatbot.train("training.jokes")
            chatbot.train("training.robojiub")
            chatbot.train("training.suntzu")
            init_bot(True)
            return "@{0} - Training complete!".format(viewer)

        msg = " ".join(message).split(" < ")[1]
        question = msg.split(" > ")[0]
        answer = msg.split(" > ")[1]

        init_bot(False)
        chatbot.set_trainer(ListTrainer)
        chatbot.train([question, answer])
        init_bot(True)

        return "@{0} - I can now associate \"{1}\" with \"{2}\", thank you. :)".format(viewer, question, answer)

    if chatbot == None:
        init_bot(True)

    print "< " + " ".join(message)

    response = "Sorry, I have not been trained yet..."
    try:
        response = chatbot.get_response(" ".join(message))
    except Exception:
        queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
        queue.put(("question() - Could not get response", 'BG_error'))
        response = "You broke me."

    print "> " + response.text

    return "@{0} - {1}".format(viewer, response.text)

def init_bot(readonly):
    global chatbot
    if chatbot != None:
        del chatbot

    chatbot = ChatBot('RoboJiub', read_only=readonly,
        trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        logic_adapters=[
            "chatterbot.logic.MathematicalEvaluation",
            {
                "import_path": "chatterbot.logic.BestMatch",
                "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
                "response_selection_method": "chatterbot.response_selection.get_random_response"
            }
        ],
        filters=[
            'chatterbot.filters.RepetitiveResponseFilter'
        ],
        database="./database.db"
    )
