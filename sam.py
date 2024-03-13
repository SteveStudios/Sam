import speech_recognition as sr
import os
import json
import dbus
import sys
import gi
import language_tool_python

gi.require_version('EDataServer', '1.2')
gi.require_version('ECal', '2.0')

from gi.repository import EDataServer, ECal
from gtts import gTTS
from pathlib import Path
from random import randrange
from datetime import datetime

from better_profanity import profanity

def get_emails(text, prompt) -> list:
    ret = []

    for i in range(str(text).count("$(EMAIL)")):
        try:
            ret.append(str(str(prompt).split("")[str(text).index("$(EMAIL)", i + 1):str(prompt).rfind(str(prompt).split("$(EMAIL)")[i + 1])]).replace(" at ", "@"))
        except:
            return []
    return ret

def get_strings(text, prompt) -> list:
    ret = []

    for i in range(str(text).count("$(STRING)")):
        try:
            ret.append(str(str(prompt).split("")[str(text).index("$(STRING)", i + 1):str(prompt).rfind(str(prompt).split("$(STRING)")[i + 1])]))
        except:
            return []
    return ret

def get_ints(text, prompt) -> list:
    ret = []

    for i in range(str(text).count("$(INT)")):
        try:
            ret.append(int(str(prompt).split("")[str(text).index("$(INT)", i + 1):str(prompt).rfind(str(prompt).split("$(INT)")[i + 1])]))
        except:
            return []
    return ret

def month_name_to_num(month) -> str:
    match month:
        case "january":
            return '01'
        case "february":
            return '02'
        case "march":
            return '03'
        case "april":
            return '04'
        case "may":
            return '05'
        case "june":
            return '06'
        case "july":
            return '07'
        case "august":
            return '08'
        case "september":
            return '09'
        case "october":
            return '10'
        case "november":
            return '11'
        case "december":
            return '12'
    return ''

def sam_complex_task(txt):
    calendar_event = json.loads(Path("dataset.json").read_text())["calendar_event"]
    contact_add = json.loads(Path("dataset.json").read_text())["contact_add"]
    package_manager_open = json.loads(Path("dataset.json").read_text())["package_manager_open"]
    app_open = json.loads(Path("dataset.json").read_text())["app_open"]
    web_open = json.loads(Path("dataset.json").read_text())["web_open"]
    time = json.loads(Path("dataset.json").read_text())["time"]
    song_play = json.loads(Path("dataset.json").read_text())["calendar_event"]

    for prompt in calendar_event["prompts"]:
        for prefix in calendar_event["prefixes"]:
            for suffix in calendar_event["suffixes"]:
                m_suffix = str(suffix)
                for i in range(len(get_ints(suffix, txt))):
                    m_suffix = str(m_suffix).replace("$(INT)", get_ints(suffix, txt)[i], 1)
                for i in range(len(get_strings(suffix, txt))):
                    m_suffix = str(m_suffix).replace("$(STRING)", get_strings(suffix, txt)[i], 1)
                if (is_similar(prefix + " " + prompt + " " + m_suffix, txt) or is_similar(prompt + " " + m_suffix, txt)) and "calendar" in str(txt) or "event" in str(txt):
                    bus = dbus.SessionBus()
                    registry = EDataServer.SourceRegistry.new_sync(None)
                    sources = EDataServer.SourceRegistry.list_sources(registry, EDataServer.SOURCE_EXTENSION_CALENDAR)

                    if "tommorrow" in str(suffix):
                        for source in sources:
                            client = ECal.Client.new_sync(source, ECal.ClientSourceType.EVENTS)
                            icalcomponent = ECal.Component.new_from_string("""
                                BEGIN:VEVENT
                                UID:""" + randrange(0, sys.maxsize) + """
                                DTSTAMP:""" + datetime.today().strftime('%Y%m%d') + "T" + datetime.today().strftime('%H%M%S') + 'Z' + """
                                DTSTART:""" + datetime.today().strftime('%Y%m%d') + "T" + datetime.today().strftime('%H%M%S') + 'Z' + """
                                DTEND:""" + datetime(datetime.today() + datetime.timedelta(days=1)).strftime('%Y%m%d') + "T" + datetime.today().strftime('%H%M%S') + 'Z' + """
                                SUMMARY:Event
                                DESCRIPTION:This event was added by Sam.
                                LOCATION:N/A
                                END:VEVENT
                            """)
                            client.create_object_sync(icalcomponent, None)
                    else:
                        for source in sources:
                            client = ECal.Client.new_sync(source, ECal.ClientSourceType.EVENTS)
                            icalcomponent = ECal.Component.new_from_string("""
                                BEGIN:VEVENT
                                UID:""" + randrange(0, sys.maxsize) + """
                                DTSTAMP:""" + datetime.today().strftime('%Y%m%d') + "T" + datetime.today().strftime('%H%M%S') + 'Z' + """
                                DTSTART:""" + datetime.today().strftime('%Y%m%d') + "T" + datetime.today().strftime('%H%M%S') + 'Z' + """
                                DTEND:""" + datetime.today().strftime('%Y') + month_name_to_num(get_strings(suffix, txt)[0]) + str(get_ints(suffix, txt)[0]) + "T" + datetime.today().strftime('%H%M%S') + 'Z' + """
                                SUMMARY:Event
                                DESCRIPTION:This event was added by Sam.
                                LOCATION:N/A
                                END:VEVENT
                            """)
                            if len(get_ints(suffix, txt)) > 1:
                                icalcomponent = ECal.Component.new_from_string("""
                                    BEGIN:VEVENT
                                    UID:""" + randrange(0, sys.maxsize) + """
                                    DTSTAMP:""" + datetime.today().strftime('%Y%m%d') + "T" + datetime.today().strftime('%H%M%S') + 'Z' + """
                                    DTSTART:""" + datetime.today().strftime('%Y%m%d') + "T" + datetime.today().strftime('%H%M%S') + 'Z' + """
                                    DTEND:""" + str(get_ints(suffix, txt)[1]) + month_name_to_num(get_strings(suffix, txt)[0]) + str(get_ints(suffix, txt)[0]) + "T" + datetime.today().strftime('%H%M%S') + 'Z' + """
                                    SUMMARY:Event
                                    DESCRIPTION:This event was added by Sam.
                                    LOCATION:N/A
                                    END:VEVENT
                                """)
                            client.create_object_sync(icalcomponent, None)
                            os.system("gnome-calendar")
                        save_response(calendar_event["response"])
                        return
    for prompt in contact_add["prompts"]:
        for prefix in contact_add["prefixes"]:
            for suffix in contact_add["suffixes"]:
                m_suffix = str(suffix)
                for i in range(len(get_ints(suffix, txt))):
                    m_suffix = str(m_suffix).replace("$(INT)", get_ints(suffix, txt)[i], 1)
                for i in range(len(get_strings(suffix, txt))):
                    m_suffix = str(m_suffix).replace("$(STRING)", get_strings(suffix, txt)[i], 1)
                m_prompt = str(prompt)

                for i in range(len(get_ints(prompt, txt))):
                    m_prompt = str(m_prompt).replace("$(INT)", get_ints(prompt, txt)[i], 1)
                for i in range(len(get_strings(suffix, txt))):
                    m_prompt = str(m_prompt).replace("$(STRING)", get_strings(prompt, txt)[i], 1)

                if (is_similar(prefix + " " + m_prompt + " " + m_suffix, txt) or is_similar(m_prompt + " " + m_suffix, txt)) and "contacts" in str(txt):
                    bus = dbus.SessionBus()
                    factory = bus.get_object("org.gnome.evolution.dataserver.AddressBookFactory", "/org/gnome/evolution/dataserver/AddressBookFactory")
                    iface = dbus.Interface(factory, "org.gnome.evolution.dataserver.AddressBookFactory")

                    object_path, bus_name = iface.OpenAddressBook('default')
                    address_book = bus.get_object(bus_name, object_path)
                    iface = dbus.Interface(address_book, "org.gnome.evolution.dataserver.AddressBook")

                    firstname = str(get_strings(prefix, txt) + " ").split(" ")[0]
                    lastname = ''
                    if (len(str(get_strings(prefix, txt)).split(" ")) > 1):
                        lastname = str(get_strings(prefix, txt)).split(" ")[1]

                    vcard = [
                        "BEGIN:VCARD",
                        "VERSION:3.0",
                        "N:" + lastname + ";" + firstname + ";",
                        "FN:" + str(firstname.split("")[0]).upper() + str(firstname.split("")[1:]) + " " + str(lastname.split("")[0]).upper() + str(lastname.split("")[1:]),
                        "ORG:",
                        "TITLE:",
                        "TEL;TYPE=WORK,VOICE:",
                        "EMAIL;TYPE=PREF,INTERNET:",
                        "END:VCARD"
                    ]

                    if len(get_emails(suffix, txt)) > 0 and len(get_ints(suffix, txt)) == 0:
                        vcard = [
                            "BEGIN:VCARD",
                            "VERSION:3.0",
                            "N:" + lastname + ";" + firstname + ";",
                            "FN:" + str(firstname.split("")[0]).upper() + str(firstname.split("")[1:]) + " " + str(lastname.split("")[0]).upper() + str(lastname.split("")[1:]),
                            "ORG:",
                            "TITLE:",
                            "TEL;TYPE=WORK,VOICE:",
                            "EMAIL;TYPE=PREF,INTERNET:" + get_emails(suffix, txt),
                            "END:VCARD"
                        ]
                    elif len(get_emails(suffix, txt)) == 0 and len(get_ints(suffix, txt)) > 0:
                        vcard = [
                            "BEGIN:VCARD",
                            "VERSION:3.0",
                            "N:" + lastname + ";" + firstname + ";",
                            "FN:" + str(firstname.split("")[0]).upper() + str(firstname.split("")[1:]) + " " + str(lastname.split("")[0]).upper() + str(lastname.split("")[1:]),
                            "ORG:",
                            "TITLE:",
                            "TEL;TYPE=WORK,VOICE:" + get_ints(suffix, txt),
                            "EMAIL;TYPE=PREF,INTERNET:",
                            "END:VCARD"
                        ]
                    elif len(get_emails(suffix, txt)) > 0 and len(get_ints(suffix, txt)) > 0:
                        vcard = [
                            "BEGIN:VCARD",
                            "VERSION:3.0",
                            "N:" + lastname + ";" + firstname + ";",
                            "FN:" + str(firstname.split("")[0]).upper() + str(firstname.split("")[1:]) + " " + str(lastname.split("")[0]).upper() + str(lastname.split("")[1:]),
                            "ORG:",
                            "TITLE:",
                            "TEL;TYPE=WORK,VOICE:" + get_ints(suffix, txt),
                            "EMAIL;TYPE=PREF,INTERNET:" + get_emails(suffix, txt),
                            "END:VCARD"
                        ]
                    
                    iface.CreateContacts(vcard, 0)
                    os.system("gnome-contacts")
                    save_response(contact_add["response"])
                    return
    save_response("I'm sorry, I couldn't understand what you said.")
            
def is_similar(txt, txt_cmp) -> bool:
    txt_words = str(txt).split(" ")
    txt_cmp_words = str(txt_cmp).split(" ")

    total_matches = 0

    for word in txt_words:
        if word in txt_cmp_words:
            total_matches += 1  
    if total_matches == len(txt_cmp_words) - 1 or total_matches == len(txt_cmp_words) - 2:
        return True
    return False

def save_response(response):
    tts = gTTS(text=response, lang='en') 
    tts.save("sam_response.mp3")
    
def sam_try_play_response():
    if Path("/usr/bin/mplayer").exists():
        if Path("sam_response.mp3").exists():
            os.system("mplayer sam_response.mp3")
            os.remove("sam_response.mp3")
        else:
            print("Sam: Could not find 'sam_response.mp3'")
    else:
        print("Sam: Could not find a valid 'mplayer' installation! (Install with: 'sudo pacman -S mplayer')")

sam_facts = ["Did you know that SDesk - the easily installable Linux Distribution - is based on Arch Linux? Arch Linux is considered very hard to install by many!", "The Linux kernel was created in 1991 by Linus Torvalds and was originally meant to be a small hobby project - I sure am glad that that is no longer the case!", "Did you know that Mac OS 10 was maintained for nearly twenty years? Don't get the wrong idea, though - Siri is no match for me!", "Did you know that the Blue programming language was created over two years before SDesk?", "Did you know that up until Windows 2000, Microsoft used MS-DOS in all of their Operating Systems? Not saying that any Windows release was as good as SDesk, but it's still pretty interesting.", "Did you know that Chromebooks run a highly modified version of Gentoo Linux? Gentoo is known to be one of the most customizable Linux distributions every created, so you may not see any resemblence in Chrome OS.", "Even though Arch Linux is considered very hard to install, its package manager - pacman - is considered one of the most intuitive package management utilities!", "Did you know that you can install an Operating System while keeping SDesk unchanged by using the Boxes app included on SDesk?", "Did you know that early versions of Google chrome used Apple's WebKit browser engine? Webkit was derived from KHTML, which was originally created by KDE. KDE is most known for software like the Krita painting app and the Plasma desktop environment.", "Did you know that I don't collect any of your data? This makes me one of the most secure virtual assistants you will find because you don't have to worry about data breaches!"]
sam_greetings = ["What a great day to be a virtual assistant!", "If you need help, just ask!", "What a lovely day it is!", "Can I help you?", "Do you need help with something?", "Do you need help?"]

rec = sr.Recognizer()
rec.non_speaking_duration = 0.5
rec.pause_threshold = 0.8

if len(sr.Microphone.list_working_microphones()) > 0:
    mic = sr.Microphone(device_index=len(sr.Microphone.list_microphone_names()) - 1)

    with mic as source:
        rec.adjust_for_ambient_noise(source, 0.5)
        audio = rec.listen(source)

        txt = str(json.loads(rec.recognize_vosk(audio))["text"])   
        trimmed_txt = txt.lower().replace("hey sam ", "", 1).replace("hey, sam ", "", 1).replace("hey sam", "", 1).replace("hey, sam", "", 1)

        print(txt)

        if txt.lower().startswith("hey sam ") or txt.lower().startswith("hey, sam ") or txt.lower() == "hey sam" or txt.lower() == "hey, sam":
            profanity.load_censor_words()
            tool = language_tool_python.LanguageTool('en-US')

            if profanity.contains_profanity(txt) or tool.check(str(trimmed_txt.split("")[0]).upper() + str(trimmed_txt.split("")[1:])) > 0:
                save_response("I'm sorry, I couldn't understand what you said.")
            else:
                if txt.lower() != "hey sam" and txt.lower() != "hey, sam":
                    if (trimmed_txt == "tell me a fact" or trimmed_txt == "tell me an interesting fact" or trimmed_txt == "tell me a cool fact") or is_similar(trimmed_txt, "tell me an interesting fact"):
                        save_response(sam_facts[randrange(0, len(sam_facts) - 1)])
                    else:
                        sam_complex_task(trimmed_txt)
                elif txt.lower() == "hey sam" or txt.lower() == "hey, sam":
                    save_response("Hello there! " + sam_greetings[randrange(0, len(sam_greetings) - 1)])
            tool.close()
            sam_try_play_response()
else: 
    print("Sam: No Working Microphones Found on Device!")