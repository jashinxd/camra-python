# -*- coding: utf-8 -*-
import re

def createBadWordsENG():
    bad = ["anal", "anus", "ballsack", "blowjob", "boner",
           "cock", "cunt", "dick", "dildo", "dyke",
           "fag", "fuck", "jizz", "muff", "nigger",
           "nigga", "penis", "piss", "pussy",
           "scrotum", "sex", "shit", "slut",
           "smegma", "spunk", "twat", "vagina",
           "wank", "whore", "erection"]
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

def createBadWordsSPAN():
    bad = ["Asesinato", "asno", "bastardo", "Bollera",
           "Cabron", "Cabrón", "Caca", "Chupada",
           "Chupapollas", "Chupetón", "concha", "Concha de tu madre",
           "Coño", "Coprofagía", "Culo", "Drogas", 
           "Esperma", "Fiesta de salchichas", "Follador", "Follar",
           "Gilipichis", "Gilipollas", "Hacer una paja", "Haciendo el amor",
           "Heroína", "Hija de puta", "Hijaputa", "Hijo de puta",
           "Hijoputa", "Idiota", "Imbécil", "infierno",
           "Jilipollas", "Kapullo", "Lameculos", "Maciza",
           "Macizorra", "maldito", "Mamada", "Marica"]
    return bad

def filterBadSongs(songName):
    badEng = createBadWordsENG()
    badRus = createBadWordsRUS()
    badSpan = createBadWordsSPAN()
    if (len(badEng) == 0) or (len(badRus) == 0):
        return True
    if (songName == None):
        return True
    for word in badEng:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            return True
    for word in badRus:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            return True
    for word in badSpan:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            return True
    return False

def censorFilteredWords(songName):
    badEng = createBadWordsENG()
    badRus = createBadWordsRUS()
    badSpan = createBadWordsSPAN()
    cen = ""
    if (len(badEng) == 0) or (len(badRus) == 0):
        return True
    if (songName == None):
        return True
    for word in badEng:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            for i in list(word):
                cen = cen + "*"
    for word in badRus:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            for i in list(word):
                cen = cen + "*"
    for word in badSpan:
        bad_word = re.compile(re.escape(word), re.IGNORECASE)
        if re.search(bad_word, songName):
            for i in list(word):
                cen = cen + "*"
    if cen is "":
        cen = songName
    return cen






            