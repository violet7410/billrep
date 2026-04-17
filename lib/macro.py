#!/bin/env python

import uuid

def macroLink(text, url):
    return "<a href='%s'>%s</a>" % (url, text)

def macroExpand(label, text) :
    uniqId = uuid.uuid4()
    return "<a class='expandText1' onclick='ToggleExpandText(this, \"%s\")'>+ %s</a><br/><div id='%s' class='collapseText'>%s</div>" % (uniqId, label, uniqId, text)

def macroClipboard(label, text) :
    uniqId = uuid.uuid4()
    return "<button onclick='CopyToClipboard(this, \"%s\")'>%s</button><div id='%s' class='collapseText'>%s</div>" % (uniqId, label, uniqId, text)


def processMacro(params):
    macroText = ''
    macroName = params.pop(0)

    if macroName.lower() == 'link' :
        if len(params) != 2 : raise(Exception('Macro \'%s\' required 2 parameters but got %s' % (macroName, len(params))))
        macroText = macroLink(text=params[0], url=params[1])
    elif macroName.lower() == 'expand' :
        if len(params) != 2 : raise(Exception('Macro \'%s\' required 2 parameters but got %s' % (macroName, len(params))))
        macroText = macroExpand(label=params[0], text=params[1])
    elif macroName.lower() == 'clipboard' :
        if len(params) != 2 : raise(Exception('Macro \'%s\' required 2 parameters but got %s' % (macroName, len(params))))
        macroText = macroClipboard(label=params[0], text=params[1])
    else :
        raise(Exception('Unknown macro \'%s\'' % (macroName)))
    
    return macroText


