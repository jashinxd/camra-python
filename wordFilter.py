# -*- coding: utf-8 -*-
import re

def createBadWordsENG():
    bad = ["anal", "anus", "ballsack", "blowjob", "boner",
           "cock", "cunt", "dick", "dildo", "dyke",
           "fag", "fuck", "jizz", "muff", "nigger",
           "nigga", "penis", "piss", "pussy",
           "scrotum", "sex", "shit", "slut",
           "smegma", "spunk", "twat", "vagina",
           "wank", "whore"]
    return bad

def createBadWordsRUS():
    bad = ["выёбываться", "гандон", "говно", "говнюк",
           "голый", "дать пизды", "дерьмо", 
           "дрочить", "другой дразнится", "ёбарь",
           "ебать-копать", "ебло", "ебнуть",
           "ёб твою мать", "жопа", "жополиз", 
           "играть на кожаной флейте", "измудохать",
           "каждый дрочит как он хочет", "какая разница",
           "как два пальца обоссать", "курите мою трубку",
           "лысого в кулаке гонять", "малофя", "манда"]
    return bad

def filterBadSongs(songName):
    badEng = createBadWordsENG()
    badRus = createBadWordsRUS()
    if (len(badEng) == 0) or (len(badRus) == 0):
        return False
    if (songName == None):
        return False
    for word in badEng:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            return False
        else:
            return True 
    for word in badRus:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            return False
        else:
            return True 
    return False

def censorFilteredWords(songName):
    badEng = createBadWordsENG()
    badRus = createBadWordsRUS()
    cen = ""
    if (len(badEng) == 0) or (len(badRus) == 0):
        return False
    if (songName == None):
        return False
    for word in badEng:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            for i in list(word):
                cen = cen.join("*")
    for word in badRus:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            for i in list(word):
                cen = cen.join("*")
    return cen






            