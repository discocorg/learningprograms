# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz


#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

# Problem 1

class NewsStory (object):
    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        return self.guid

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_link(self):
        return self.link

    def get_pubdate(self):
        return self.pubdate
    
#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

# PHRASE TRIGGERS

# Problem 2
class PhraseTrigger(Trigger):
    def __init__(self, phrase):
        self.phrase = phrase.lower()

    #String -> Boolean
    #returns true if the object string, phrase is in string text
    def is_phrase_in(self, text):
        text = text.lower()
        #Need to split but any punctuation or space
        for ch in string.punctuation:
            text = text.replace(ch, ' ')
        textwords = text.split()
        phrasewords = self.phrase.split()
        for word in phrasewords:
            if word in textwords:
                textwords_extras_removed = textwords[textwords.index(word):textwords.index(word)+len(phrasewords)]
                return textwords_extras_removed == phrasewords
            else: 
                return False
    
def test_is_phrase_in():
    exampletrigger = PhraseTrigger('my phrase')
    assert exampletrigger.is_phrase_in('is!my!! !phrase!! !here')== True 
    
def test_is_phrase_in_2():
    exampletrigger = PhraseTrigger('my phrase')
    assert exampletrigger.is_phrase_in('is..phrase.here my')== False 
# Problem 3
#Fires when a item title contains a given phrase
class TitleTrigger(PhraseTrigger):
    def evaluate(self, story):
       return self.is_phrase_in(story.get_title())

def test_TitleTrigger():
    exclaim   = NewsStory('', 'Purple!!! Cow!!!', '', '', datetime.now())
    plural    = NewsStory('', 'Purple cows are cool!', '', '', datetime.now())
    cuddly = NewsStory('', 'The purple cow is soft and cuddly.', '', '', datetime.now())
    separate  = NewsStory('', 'The purple blob over there is a cow.', '', '', datetime.now())
    s2  = TitleTrigger('purple cow')
    assert s2.evaluate(separate) == False 
# Problem 4
#Fires when a item description contains a given phrase
class DescriptionTrigger(PhraseTrigger):
    def evaluate(self, story):
        return self.is_phrase_in(story.get_description())
# TIME TRIGGERS

# Problem 5
class TimeTrigger(Trigger):
    def __init__(self, init_time):
        init_time = datetime.strptime(init_time, "%d %b %Y %H:%M:%S")
        self.time = init_time.replace(tzinfo=pytz.timezone("EST"))

    def get_time(self):
        return self.time
# Problem 6
class BeforeTrigger(TimeTrigger): 
    def evaluate(self, story):
        if self.time > story.get_pubdate(): 
            return True
        else:
            return False

class AfterTrigger(TimeTrigger):
    def evaluate(self, story):
        if self.time < story.get_pubdate(): 
            return True
        else:
            return False

def test_BeforeTrigger1():
    s1 = BeforeTrigger('12 Oct 2016 23:59:59')
    ancient_time = datetime(1987, 10, 15)
    ancient_time = ancient_time.replace(tzinfo=pytz.timezone("EST"))
    ancient = NewsStory('', '', '', '', ancient_time)
    assert s1.evaluate(ancient) == True 
# COMPOSITE TRIGGERS

# Problem 7
class NotTrigger(Trigger):
    def __init__(self, trigger):
        self.trigger = trigger
    
    def evaluate(self, story):
        return not self.trigger.evaluate(story)

# Problem 8
class AndTrigger(Trigger):
    def __init__(self, trigger_one, trigger_two):
        self.trigger_one = trigger_one
        self.trigger_two = trigger_two
    def evaluate(self, story):
        return self.trigger_one.evaluate(story) and self.trigger_two.evaluate(story)


# Problem 9
# TODO: OrTrigger
class OrTrigger(Trigger):
    def __init__(self, trigger_one, trigger_two):
        self.trigger_one = trigger_one
        self.trigger_two = trigger_two
    def evaluate(self, story):
        return self.trigger_one.evaluate(story) or  self.trigger_two.evaluate(story)


#======================
# Filtering
#======================

# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    newstorylist = []
    for story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(story) == True:
                newstorylist.append(story)
    return newstorylist


#======================
# User-Specified Triggers
#======================
# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)

    # TODO: Problem 11
    # line is the list of lines that you need to parse and for which you need
    # to build triggers

    print(lines) # for now, print it so you see what it contains!



SLEEPTIME = 120 #seconds -- how often we poll

def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        t1 = TitleTrigger("Japan")
        t2 = DescriptionTrigger("death")
        t3 = DescriptionTrigger("killing")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1, t4]

        # Problem 11
        # TODO: After implementing read_trigger_config, uncomment this line 
        # triggerlist = read_trigger_config('triggers.txt')
        
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")

            # Get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://news.yahoo.com/rss/topstories"))

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

