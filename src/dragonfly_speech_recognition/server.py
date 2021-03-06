#!/usr/bin/env python

import sys, os
import time
import logging
import pythoncom

# XML RPC SERVER
from threading import Thread
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer as Server

def error(error):
    print "ERROR: %s"%error
    sys.exit()

dragonfly_path = "%s/../../deps/dragonfly"%os.path.dirname(os.path.realpath(__file__))
sys.path.append(dragonfly_path)

try:
    from dragonfly.engines.backend_sapi5.engine import Sapi5InProcEngine
    from dragonfly import (Grammar, CompoundRule, Dictation, Choice)
except:
    error("Failed to import dragonfly, path: %s"%dragonfly_path)

#---------------------------------------------------------------------------

RESULT = None

#---------------------------------------------------------------------------

class GrammarRule(CompoundRule):   
    def _process_recognition(self, node, extras):
        global RESULT
        RESULT = extras

# RPC METHOD
def recognize(spec, choices_values, timeout):

    global RESULT
    RESULT = None

    grammar = Grammar("grammar")

    extras = []
    for name, choices in choices_values.iteritems():
        extras.append(Choice(name, dict((c,c) for c in choices)))

    Rule = type("Rule", (GrammarRule,),{"spec": spec, "extras": extras})
    grammar.add_rule(Rule())
    grammar.load()   

    future = time.time() + timeout
    while time.time() < future:
        if RESULT is not None:
            break

        pythoncom.PumpWaitingMessages()

        time.sleep(.1)

    grammar.unload()

    print "RESULT:", RESULT

    return RESULT

if __name__ == "__main__":
    engine = Sapi5InProcEngine()
    engine.connect()

    server = Server(("localhost", 8000))
    server.register_function(recognize, 'recognize')

    engine.speak('Speak recognition active!')
    print "Speak recognition active! Serving at port 8000"

    server.serve_forever()


