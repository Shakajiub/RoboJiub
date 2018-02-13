# -*- coding: utf-8 -*-
import sys

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer

#from src.currency.currency import get_mods

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

        if "q" not in message or "a" not in message:
            return "@{0} - Invalid training input.".format(viewer)

        msg = " ".join(message).split(" q ")[1]
        question = msg.split(" a ")[0]
        answer = msg.split(" a ")[1]

        init_bot(False)
        chatbot.set_trainer(ListTrainer)

        chatbot.train([
            question,
            answer
        ])
        init_bot(True)
        chatbot.set_trainer(ChatterBotCorpusTrainer)

#        chatbot.train("training.robojiub")
#        chatbot.train("training.humor")
#        chatbot.train("chatterbot.corpus.english.ai")
#        chatbot.train("chatterbot.corpus.english.computers")
#        chatbot.train("chatterbot.corpus.english.conversations")
#        chatbot.train("chatterbot.corpus.english.emotion")
#        chatbot.train("chatterbot.corpus.english.greetings")

        return "@{0} - I can now associate \"{1}\" with \"{2}\", thank you. :)".format(viewer, question, answer)

    if chatbot == None:
        init_bot(True)

    response = "Sorry, I have not been trained yet..."
    try:
        response = chatbot.get_response(" ".join(message).capitalize(), 42)
    except Exception:
        queue.put(("{0}".format(sys.exc_info()[0]), 'BG_error'))
        queue.put(("question() - Could not get response", 'BG_error'))
        response = "You broke me."

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
