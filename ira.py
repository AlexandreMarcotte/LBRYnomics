#!/usr/bin/env python3 -u

#from pybry import LbryApi
#import pybry

import sys, os, time
import urllib.parse, urllib.request, json

from queue import Queue, Empty
from threading import Thread, Lock

# should I resolve twice to discover the
# canonical permanent_url (the one with the channel reference)?
RESOLVE_TWICE = False
SEARCH_LIMIT = 50
NUM_THREADS = 100
cachedLBRY = None


class lbryRPC():
    """s
    I encapsulate a portion of the LBRY api documented at these sites:
    https://github.com/lbryio/lbry/blob/master/docs/api.json
    https://lbry.tech/api/sdk

    I'm built up ad hoc to the needs of ira.py

    The idea is to get away from the complexity of pybry

    (it's just a web request, y'all...)
    """

    def __init__ (self):
        self.RPC_URL = "http://localhost:5279"

    def lbry_call(self, method, params=None):
        params = params or {}
        headers = {
            "Content-Type": "application/json"
        }
        data = {"method": method, "params": params}
        data = json.dumps(data).encode('utf8')
        request = urllib.request.Request(self.RPC_URL, data, headers)
        with urllib.request.urlopen(request) as response:
            # for now, return the response code with it
            res = json.loads(response.read())

            if 'error' in res:
                return (res, response.getcode())
            try:
                return (res['result'], response.getcode())
            except KeyError as e:
                print (res, file=sys.stderr)
                return ({'error': str(e) }, response.getcode())

    def resolve(self, url):
        "resolve a single url or a list of urls"
        urls = url
        #print(url, file=sys.stderr)
        if type(urls) != list:
            urls = [urls]

        response = self.lbry_call("resolve", {"urls": urls})
        return  response

    def resolveOrNone(self, url):
        "resolve, return the record. If it doesn't, return none"
        res = self.resolve(url)[0]
        if 'error' in res: return None
        res = res[url]
        if 'error' in res: return None
        return res

    def claim_list_by_channel(self, uris, page=0, page_size=0):
        URI = uris
        if type(uris) == str:
            URI = [uris]

        extraURIs = URI[1:] or []
        uri = URI[0]

        return self.lbry_call("claim_list_by_channel", {
            "uri":uri,
            "uris":extraURIs,
            "page": page,
            "page_size": page_size} )

    def claim_list(self, name):
        return self.lbry_call("claim_list",
            {"name": name})

    def get(self, uri, file_name=None, timeout=None ):
        params = {"uri": uri}
        if file_name: params['file_name'] = file_name
        if timeout: params['timeout'] = timeout

        return self.lbry_call("get", params)

    def file_list(self, **kwargs):
        return self.lbry_call("file_list", kwargs)

    def version(self):
        return self.lbry_call("version")

def fixedAPI():
    global cachedLBRY

    if cachedLBRY: return cachedLBRY

    cachedLBRY = lbryRPC()
    return cachedLBRY

def niceGetter(thing, *args):
    """
    Given a nested dictionary "thing", Get any nested field by the path described:
    eg niceGetter(thing, 'cars', 'mustang', 'cobra')
    will return thing['cars']['mustang']['cobra']
    or None if such item doesn't exist.
    """
    if thing == None: return None
    subthing = thing
    for arg in args:
        if arg not in subthing: return None
        subthing = subthing[arg]

    return subthing

def recGetter(thing, *keypath):
    """
    For nested dictionaries, just get the damned thing specified by 'keypath',
    no matter how deep it is.
    return None if no such key exists.
    """
    if thing == None: return None
    if type(thing) != dict: return None
    if len(thing.keys()) == 0: return None

    if keypath[0] in thing:
        if len(keypath) > 1:
            return recGetter(thing[keypath[0]], *keypath[1:])
        else:
            return thing[keypath[0]]
    else:
        for t in thing.keys():
            # print(t, keypath)
            response = recGetter(thing[t], *keypath)
            if response != None:
                return response
        return None

def usage():
    print(f"""
    USAGE:
        {sys.argv[0]} [command] [options] [list of urls, probably]

    for a lot more information, type:
        {sys.argv[0]} bore me
    """, file=sys.stderr)

def downloadThread(qin, args, lock):
    l = fixedAPI()
    while True:
        a = qin.get().rstrip()
        lock.acquire()
        print(f"Downloading '{a}'...", file=sys.stderr)
        lock.release()
        res = l.get(a, timeout=4)
        if 'error' not in res:
            lock.acquire()
            print(a.rstrip(), flush=True)
            lock.release()
        qin.task_done()

def downloadT(args):
    qin = Queue(maxsize=0)
    lock = Lock()
    for x in range (NUM_THREADS):
        worker = Thread(target=downloadThread, args=(qin, args, lock))
        worker.setDaemon(True)
        worker.start()

    if sys.stdin.isatty():
        for a in args:
            qin.put(a)
    else:
        for line in sys.stdin:
            qin.put(line.rstrip())

    qin.join()

def download(args):
    """
    download all urls in list 'args'
    """
    return downloadT(args)

    # print(args,file=sys.stderr)
    if type(args) != list: args=[args]

    if len(args) < 1:
        print("ERROR: Download needs a url to download.", file=sys.stderr)
        usage()
        sys.exit(1)

    l = fixedAPI()
    for a in args:
        print(f"Downloading '{a}'...", file=sys.stderr)
        res = l.get(a, timeout=4)
        if 'error' not in res:
            #print ("PRINTING", file=sys.stderr)
            print(a.rstrip(), flush=True)
            #os.fsync(sys.stdout)
        else:
            sys.stdout.flush()

def ls_streamed(args):
    "list, but as they come in the pipe"
    l = fixedAPI()
    for line in sys.stdin:
        url = line.strip().split()[0]
        ls([url], lbry=l)


def ls(args): #FIXME whatta mess
    l = fixedAPI()

    # no arguments, list the locally downloaded files.
    if len(args) == 0:
        theList = l.file_list()
        if 'error' in theList:
            print(theList['error'], file=sys.stderr)
            return [] #FIXME should throw

        theList = theList[0]

        # SADLY, I can't just get the permalink for locally downloaded files.
        # Doesn't exist. Instead, I must re-resolve their names to get a good permalink with the @channel
        # at front (since @channel is missing from metadata in file_list())
        result = []
        for item in theList: # build a URL per file
            try:
                result.append(niceGetter(item, 'claim_name')+ '#' + niceGetter(item, 'claim_id'))
            except TypeError:
                pass
        if RESOLVE_TWICE:
            resMod = [] # try to get a url with channel name included, aka "permanent_url"
            for r in result: # keep order by using the list (not the dictionary result2)
                fullentry=l.resolveOrNone(r)
                if not fullentry: continue
                #print(fullentry)
                permalink = niceGetter(recGetter(fullentry, 'claim'), 'permanent_url')
                resMod.append(permalink)
        else:
            resMod = result

        for r in resMod:
            print(r, flush=True)
        return resMod

    # if ls is called with an argument, assume a @channel name.
    result = []
    PAGE_SIZE =500
    for a in args:
        if a[0] == "@" and a.find('/') < 0: # it's a channel permaurl probably
            claimlist = l.claim_list_by_channel(a)
            if 'error' not in claimlist[0][a]:
                count = int(claimlist[0][a]['claims_in_channel'])
                pagecount = 1+count//PAGE_SIZE
                if count == 0: continue
                for page in range(pagecount):
                    print(f"{a} Page {page+1}/{pagecount}...", file=sys.stderr, flush=True)
                    claimlist = l.claim_list_by_channel(a, page=page+1, page_size=PAGE_SIZE)
                    claimlist = claimlist[0][a]['claims_in_channel'] # note: now it's data as a list, not a count **SIGH***
                    for c in claimlist:
                        perma = recGetter(c, 'permanent_url')
                        result.append(perma)
                        print(perma, flush=True)
        else:
            #presume it's a lookup
            claim = l.resolveOrNone(a)

            if claim:
                perma = niceGetter(claim,'claim')['permanent_url']
                result.append(perma)
                print(perma, flush=True)
    return result

mediaKinds = ["application", "video", "audio", "text", "image"]
claimKinds = ["file", "channel"]

def doSearchOpts(args, max_results=SEARCH_LIMIT):
    "Construct a search url based on the args provided."

    opts = [option[1:] for option in args if option and option[0] == '-']
    terms = [term for term in args if term and term[0] != '-']

    mediaTypes = [aType for aType in opts if aType in mediaKinds]
    claimTypes = [aType for aType in opts if aType in claimKinds]

    nsfwString = ""
    if 'nsfw' in opts:
        nsfwString="&nsfw=true"

    if 'sfw' in opts:
        nsfwString="&nsfw=false"


    mediaString = ""
    for m in mediaTypes:
        mediaString += m + ","
    if mediaString: mediaString = "&mediaType=" + mediaString[:-1]

    claimString = ""
    for c in claimTypes:
        claimString += c + ","
    if claimString: claimString = "&claimType=" + claimString[:-1]

    termString = "s=" + "+".join(terms)

    #print(termString)

    url = "https://lighthouse.lbry.io/search?" + termString + "&size=" + str(max_results) + mediaString + claimString + nsfwString
    #print(url, file=sys.stderr)
    return url

def search(args, max_results=50, noYouTube=False, NSFW=True, printIt=True):
    url = doSearchOpts(args, max_results=max_results)

    #print(f"Searching with '{url}'...", file=sys.stderr)
    lbry = fixedAPI()

    with urllib.request.urlopen(url) as response:
        results = response.read()

    results = json.loads(results)
    permaurls = []
    for r in results:
        # print (f"NAME: {r['name']}, CLAIM: {r['claimId']}, {type(r['name'])}, {type(r['claimId'])}", file=sys.stderr)
        url = f"{r['name']}#{r['claimId']}"
        if noYouTube:
            desc = recGetter(r, 'description')
            if desc != None:
                desc = desc.lower().split()
                if len(desc) > 0:
                    if desc[-1].find('youtube') >= 0:
                        continue
        if not NSFW:
            if recGetter(r, 'nsfw') == True:
                continue

        if RESOLVE_TWICE:
            r = lbry.resolveOrNone(url)
            if r:
                perma = recGetter(recGetter(r[0], 'claim'), 'permanent_url')
                if perma == None:
                    perma = niceGetter(recGetter(r[0], 'certificate'), 'permanent_url')

                if perma != None:
                    permaurls.append(perma)
                    if printIt: print(perma, flush=True)
                    sys.stdout.flush()

        else:
            permaurls.append(url)
            if printIt: print(url, flush=True)


    return permaurls

def related(args, max_results=50, noYouTube=False, NSFW=True, skip=None):
    skip = skip or []

    l = fixedAPI()
    results = []
    origList = {}
    for a in args:
        if a in skip: continue
        result = l.resolveOrNone(a)
        if result:
            perma = recGetter(result, 'claim', 'permanent_url')
            raw  = f"{recGetter(result, 'claim', 'name')}#{recGetter(result, 'claim', 'claim_id')}"

            origList[a.rstrip()] = True
            if perma:
                origList[perma.rstrip()] = True

            origList[raw.rstrip()] = True

            title = recGetter(result, 'title')
            if title:
                results.extend(search(title.split(), max_results=max_results,  noYouTube=noYouTube, NSFW=NSFW, printIt=False))

    # weed out the inputted urls
    results_final = [url for url in results if url not in origList]


    # print (origList, file=sys.stderr)
    for url in results_final:
        print (url.strip())

    return results_final

def flattened(aDict):
    flat = {}
    for k in aDict.keys():
        flat[k] = aDict[k] # keep heirarchy, kind of (unless overridden below)
        if type(aDict[k]) == dict:
            squish = flattened(aDict[k])
            for f in squish.keys(): flat[f] =squish[f]
    return flat

#######stock filters

def _filt_tube(r):
    url = recGetter(r, "permanent_url")
    #print(f"checking notube for {url}...", file=sys.stderr)

    if 'description' in r and len(r['description']) > 0:
        return  r['description'].lower().split()[-1].find('youtube') >= 0
    else: return False

def _matches_contentType(record, contentTypeStr):
    if 'contentType' in record.keys():
        #print(f"{record['contentType']}", file=sys.stderr)
        return record['contentType'].find(contentTypeStr)>= 0
    return False

def _filt_video(r):
    #print("hello from fitl_video", file=sys.stderr)
    return _matches_contentType(r, "video")

def _filt_image(r):
    return _matches_contentType(r, "image")

def _filt_audio(r):
    return _matches_contentType(r, "audio")

def _filt_mp4(r):
    return _matches_contentType(r, "mp4")

def _filt_fee(r):
    if 'fee' in r.keys():
        return True
    else:
        return False

def _filt_sfw(r):
    if 'nsfw' in r:
        return not r['nsfw']
    else:
        return True # prolly a channel if it doesn't have nsfw tag

def _filt_haschannel(r):
    #print(f"{r}", file=sys.stderr)

    res = recGetter(r, "channel_name")
    if res:
        return True

    res = recGetter(r, "certificate")
    if res:
        return True

    return False

def _filt_ischannel(r):
    #print(f"{r}", file=sys.stderr)

    res = recGetter(r, "certificate")
    if not res:
        return False

    res = recGetter(r, "claim")

    if res: # claims aren't channels
        return False

    return True

stockFilters = {
        "tube": _filt_tube,
        "notube": lambda r: not _filt_tube(r),
        "video": _filt_video,
        "novideo": lambda r: not _filt_video(r),
        "videos": _filt_video,
        "novideos": lambda r: not _filt_video(r),
        "image": _filt_image,
        "images": _filt_image,
        "noimage": lambda r: not _filt_image(r),
        "noimages": lambda r: not _filt_image(r),
        "audio": _filt_audio,
        "noaudio": lambda r: not _filt_audio(r),
        "mp4": _filt_mp4,
        "nomp4": lambda r: not _filt_mp4(r),
        "fee": _filt_fee,
        "nofee": lambda r: not _filt_fee(r),
        "sfw": _filt_sfw,
        "nsfw": lambda r: not _filt_sfw(r),
        "nosfw":  lambda r: not _filt_sfw(r), # alias for consistency
        "haschannel": _filt_haschannel,
        "nochannel": lambda r: not _filt_haschannel(r),
        "ischannel": _filt_ischannel,
        "isfile": lambda r: not _filt_ischannel(r),
        "isntchannel": lambda r: not _filt_ischannel(r) # same as above
            }

def doFilterThread(qin, args, lock):
    lbry = fixedAPI()
    while True:
        url = qin.get()
        #print(f"checking {url}", file=sys.stderr)
        claim = lbry.resolveOrNone(url)
        if not claim:
            qin.task_done()
            continue
        passed = False
        theName = recGetter(claim, "permanent_url")

        for arg in args:
            if arg not in stockFilters: continue
            filt = stockFilters[arg]
            result = flattened(claim)
            if filt(result):
                passed = result['permanent_url']
            else:
                passed = False
                break
        if passed:
            lock.acquire()
            print(passed.rstrip(), flush=True)
            lock.release()
        qin.task_done()


def doFilterT(args):
    qin = Queue(maxsize=0)
    qout = Queue(maxsize=0)
    lock = Lock()
    for i in range(NUM_THREADS):
        worker = Thread(target=doFilterThread, args=(qin, args, lock))
        worker.setDaemon(True)
        worker.start()

    for line in sys.stdin:
        qin.put (line.split()[0])

    qin.join()


def doFilter(args):
    return doFilterT(args)
    global stockFilters
    l = fixedAPI()
    for line in sys.stdin:
        thing = None
        url = line.split()[0]
        claim = l.resolveOrNone(url)
        if  not claim: continue
        passed = False
        for arg in args:
            if arg not in stockFilters: continue
            filt = stockFilters[arg]
            result = flattened(claim)
            if filt(result):
                passed = result['permanent_url']
            else:
                passed = False
                break
        if passed:
            print(passed.rstrip(), flush=True)

def linkify(aString):
    if aString.find("lbry://") == 0:
        return aString
    else:
        return "lbry://" + aString # FIXME, more elegant, pls

def asLinks(thing):
    return linkify(thing)

def asFileList(thing):
    l = fixedAPI()
    res = l.resolveOrNone(thing)
    if  res:
        claim_id = niceGetter(res, 'claim', 'claim_id')
        #print(claim_id, file=sys.stderr)
        #print(res[0][thing]['claim']['claim_id'], file=sys.stderr)
        if not claim_id:
            return None

        thefile = l.file_list(claim_id=claim_id)
        if not thefile:
            print(f"as file: No file for '{thing}'... skipping", file=sys.stderr)
            return None

        if not thefile[0]:
            print(f"as file: No file for '{thing}'... skipping", file=sys.stderr)
            return None


        if thefile[0][0]:
            return recGetter(thefile[0][0], "download_path")
        else:
            print(f"as file: no attached file for '{thing}'... skipping", file=sys.stderr)
            return None

def asSearchLine(thing):
    """
    a search line is a dump of all the information on a claim in one line so you can
    grep it
    """
    l = fixedAPI()
    res = l.resolveOrNone(thing)
    if res:
        return (f"{thing}\t{res[0]}")

def asNiceURL(thing):
    """
    a nice url shows the channel the url belongs to, if any
    """
    l = fixedAPI()
    res=l.resolveOrNone(thing)
    if not res: return None

    permalink = recGetter(res, 'claim', 'permanent_url')

    if not permalink:
        permalink = recGetter(res, 'permanent_url')

    return permalink

def asRawURL(url):
    """
    rawURL is just the name followed by the claim_id, without channel info, like
    blog#4fa3e1b8c62e9b41e6cf4a3eb9faafe3778f1445
    """
    l = fixedAPI()
    res = l.resolveOrNone(url)
    if not res: return None

    permalink = ""
    claimID = recGetter(res, 'claim', 'claim_id')

    if not claimID:
        permalink = recGetter(res, 'permanent_url') # any perma url will do
    else:
        permalink = recGetter(res, 'claim', 'name') + "#" + claimID

    return permalink

# note: this global stuff is OK only because each invocation of ira
# performs exactly one command:
alreadyChannel = {}
def asChannels(url):
    """
    find the channel name and display it
    """
    global alreadyChannel

    l = fixedAPI()

    res = l.resolveOrNone(url)
    if res:
        channel = recGetter(res, "certificate", "permanent_url") #"channel_name")
        if channel not in alreadyChannel:
            alreadyChannel[channel] = True
        return channel
    return None

def asJSON(urls=None):
    urls = [] if urls==None else urls

    if not sys.stdin.isatty():
        for line in sys.stdin:
            url = line.split()[0].rstrip()
            urls.append(url)

    if not urls: return None

    l = fixedAPI()
    result = l.resolve(urls)[0]
    if 'error' in result:
        print("[]") #FIXME this is bad news
        return None

    data = []
    for url in urls:
        if url in result:
            if 'error' not in result[url]:
                data.append(result[url])
            del result[url]

    JSON = json.dumps(data, indent=2)
    print(JSON)

def asVanity(url):
    """
    show the url as its name only
    """
    l = fixedAPI()
    res = l.resolve(url)[0][url]
    if 'error' not in res:
        name = recGetter(res, "claim", "name")
        if not name:
            name = recGetter(res, "name")
        return name
    return none


def dump(fname):
    """
    dump stdin to a file and continue piping it
    This is useful for complex workflows
    """
    with open(fname, "w") as file:
        while True:
            line = sys.stdin.readline()
            if not line: break
            file.write(line)
            print(line, end='', flush=True) # no newline

converters = {
    "links": asLinks,
    "link": asLinks,
    "filelist": asFileList,
    "searchline": asSearchLine,
    "niceurl": asNiceURL,
    "niceurls": asNiceURL,
    "rawurl": asRawURL,
    "rawurls": asRawURL,
    "channels": asChannels,
    "channel": asChannels,
    "vanity": asVanity
}

# converters that need the whole list
# at once. Not 'pipe' efficient, but sometimes necessary
globalConverters = {
    "json": asJSON
}

def makethreads(function, args):
    for x in range(NUM_THREADS):
        worker = Thread(target=function, args=args)
        worker.setDaemon(True)
        worker.start()

def doAsT(qin, func, lock):

    while True:
        url = qin.get()
        result =func(url)
        if result:
            lock.acquire()
            print(result, flush=True)
            lock.release()
        qin.task_done()

def doAs(toThis, urls=None):
    "convert urls on stdin to specified format toThis"

    if toThis.lower() in converters:
        qin = Queue(maxsize=0)
        lock = Lock()
        makethreads(doAsT, (qin, converters[toThis.lower()], lock))

        if urls:
            for url in urls:
                qin.put(url)

        if not sys.stdin.isatty():
            for line in sys.stdin:
                if len(line.split()):
                    url = line.split()[0]
                    qin.put(url)

        qin.join()
    elif toThis.lower() in globalConverters:
        globalConverters[toThis.lower()](urls)

def claims(things):
    "print all claims against the given urls"
    if not things: return None

    urls = things
    if type(urls) == str: urls = [things]

    l = fixedAPI()

    #print(f"URLS: {urls}", file=sys.stderr)
    for url in urls:
        # for fully-qualified urls
        # I look for claims on the vanity name it uses
        if url.find('#') >= 0:
            res = l.resolve(url)[0][url]
            url = recGetter(res, 'claim', 'name')
            if not url:
                url = recGetter(res, 'name')

        res = l.claim_list (url)[0]

        if 'error' in res: return None
        res = res['claims']
        for claim in res:
            print(recGetter(claim, "permanent_url"))

def doColumnsThread(qin, args, lock):
    "Single worker thread that prints column content for the urls in qin"
    lbry = fixedAPI()
    while True:
        url = qin.get()
        result = lbry.resolve(url)[0][url]
        if 'error' not in result:
            claim = result
            #recGetter(result, "claim")
            #if not claim:
            #    claim = recGetter(result, "certificate")

            if claim:
                theLine = url
                for a in args:
                    # 'path' is so that user can specify
                    # fields in dot-notation on the command line
                    # like: source.contentType
                    # in case of ambiguity
                    path = a.split('.')
                    # print(path, file=sys.stderr)
                    theValue = recGetter(claim, *path)
                    if theValue:
                        munged = repr(str(theValue))[1:-1]
                        theLine += f"\t{munged}"
                    else:
                        theLine += "\tN/A"

                lock.acquire()
                print(theLine, flush=True)
                lock.release()
        qin.task_done()

def doColumns(args):
    qin = Queue(maxsize=0)
    lock = Lock()

    # too hard to do case insensitive b/c of hashed keys in recGetter()
    #argsLower = [a.lower() for a in args]

    makethreads(doColumnsThread, (qin, args, lock))

    "print stuff in columns"
    if not sys.stdin.isatty():
        for line in sys.stdin:
            if len(line.split()):
                url = line.split()[0]
                qin.put(url)
        qin.join()

def doWait(args):
    "wait until any change at url, then print the url. On error, fail."
    l = fixedAPI()
    dickie = {} # a dictionary we use just for hash function
    url = args[0]
    r = l.resolve(url)[0][url]
    dickie[repr(r)] = True
    while True:
        r = l.resolve(url)[0][url]
        if repr(r) not in dickie: #detect a change in the string, which means a change in anything
            break
        time.sleep(10)

    theURL = recGetter(r, "claim", "permanent_url") or url
    if '@' == theURL[0] and '/' not in theURL:
            # it's a channel
            theURL = recGetter(r, "certificate", "permanent_url") or url

    print(theURL)

def doPublish(args):
    """
    Publish with the minimal amount of meta-info, automating as much as possible
    """
    if sys.stdin.isatty():
        # treat it as a text file?
        pass

    filename = args[0]
    title = description = ""

    if len(args) > 1:
        title = args[1]

    if len(args) > 2:
        description = args[2]

    for thing in [filename, title, description]:
        print(f"{thing}")

def testout():
    "A pipe tester b/c Mac buffered pipes are the sad"
    import time
    for count in range(1000):
        print("Ha", count, flush=True)
        time.sleep(1)


def main():

    global SEARCH_LIMIT
    global BORE_ME
    if len(sys.argv) < 2:
        print("ERROR: I need a command.", file=sys.stderr)
        usage()
        sys.exit(1)

    command = sys.argv[1]
    if "download"[:len(command)] == command:
        download(sys.argv[2:])

    if "ls"[:len(command)] == command:
        if sys.stdin.isatty():
            ls(sys.argv[2:])
        else:
            ls_streamed(sys.argv[2:])

    if "claims"[:len(command)] == command:
        if sys.stdin.isatty():
            claims(sys.argv[2:])
        else:
            for line in sys.stdin:
                thing = line.strip().split()[0]
                claims(thing)

    if "search"[:len(command)] == command:
        if 'IRA_SEARCH_LIMIT' in os.environ:
            SEARCH_LIMIT=int(os.environ['IRA_SEARCH_LIMIT'])

        search(sys.argv[2:], max_results=SEARCH_LIMIT)

    if "related"[:len(command)] == command:
        if 'IRA_SEARCH_LIMIT' in os.environ:
            SEARCH_LIMIT=int(os.environ['IRA_SEARCH_LIMIT'])

        if sys.stdin.isatty():
            related(sys.argv[2:], max_results=SEARCH_LIMIT)
        else:
            AlreadySeen = []
            for line in sys.stdin:
                AlreadySeen.extend(related([line.strip().split()[0]], max_results=SEARCH_LIMIT, skip=AlreadySeen))
                # print(AlreadySeen, file=sys.stderr)
    if "resolve"[:len(command)] == command:
        if sys.stdin.isatty():
            doAs("niceURL", sys.argv[2:])
        else:
            doAs("niceURL")

    if "filter"[:len(command)] == command:
        if sys.stdin.isatty():
            print("You must pipe me some content to be filtered, e.g:", file=sys.stderr)
            print("\tira.py search kittens | ira.py filter notube", file=sys.stderr)
            sys.exit(2)
        else:
            doFilter(sys.argv[2:])

    if "as"[:len(command)] == command:
        if len(sys.argv) > 3:
            doAs(sys.argv[2], sys.argv[3:])
        elif sys.stdin.isatty():
            print("You must pipe me some content to be converted, e.g:", file=sys.stderr)
            print("\tira.py search kittens | ira.py as links", file=sys.stderr)
            sys.exit(2)
        else:
            doAs(sys.argv[2])

    if "dump"[:len(command)] == command:
        if sys.stdin.isatty():
            print("You must pipe me some content to dump, e.g:", file=sys.stderr)
            print("\tira.py search kittens | ira.py dump kittensearch.txt", file=sys.stderr)
        else:
            dump(sys.argv[2])
    if "testout" == command:
        testout()

    if "help"[:len(command)] == command or "-help"[:len(command)] == command \
        or "--help"[:len(command)] == command:
        usage()
        sys.exit(0)

    if "columns"[:len(command)] == command:
        doColumns(sys.argv[2:])

    if "wait"[:len(command)] == command:
        doWait(sys.argv[2:])

    if "publish"[:len(command)] == command:
        doPublish(sys.argv[2:])

    if "bore" == command:
        print(BORE_ME.expandtabs(4))
        sys.exit(0)

BORE_ME = """
HELP FOR IRA
------------
    Hey There! I'm upside (lbry://@upside#e365bc85c2b0ca05ab61486d43d8b728d4d39653),
    the creator of 'ira'. I hope you find it useful.

    ira is a "monolithic" command-line tool that allows you to use the LBRY daemon in
    interesting ways. It's DESIGNED FOR PIPING so you can stack IRA commands
    together to get powerful results.

    It's currently in alpha, so you'll have to use "./ira.py" or create your own
    alias, etc. for the faster "ira" command. See CAVEATS at the bottom for information
    on ira's requirements and quiddities.

    In general, you will type:
        ira [some_command] [optional options] [more_stuff]

    Example:
        ira search -audio punk  # search for audio files described by "punk"

    and pipe results together like:

    ira search kitten | ira filter images nofee | head -n 10 | ira download | \\
        ira as filelist | xargs -E '\\n' -J % open %

    which does a lot of stuff, but basically downloads the first 10 kitten images on
    LBRY to disk and then calls the "open" command on them.

    Let's just get to it. Here is a list of commands:
        resolve  -- resolve name into permanentUrl form
        ls       -- list files
        search   -- search for stuff
        related  -- find related content
        filter   -- weed out certain content
        download -- download file(s)
        as       -- convert incoming list to something else
        claims   -- show all urls sharing a given name
        dump     -- dump incoming pipe to disk and continue on
        columns  -- add columns to the output
        wait     -- wait until an URL changes. Nice for triggers.

    All commands work with piped lists of urls. Most commands work with arguments,
    too. The idea is that you'll be doing a lot of piping to get the results you
    want.

resolve | GET ADDRESS
---------------------
    example:
        ira resolve @upside # returns @upside#e365bc85c2b0ca05ab61486d43d8b728d4d39653
        ira resolve blog    # returns @upside#e365bc85c2b0ca05ab61486d43d8b728d4d39653/blog
        ira resolve one     # returns one#008401a48cecef2a13cf5376b696169bb36b18c6

    ira will try to get the channel info inside the URL, if available. This command does
    the same thing as "ira as niceURL"


ls | LIST FILES
---------------
    WARNING: ls is going through some changes ATM. Some things might not work as
             expected.

    example:
            ira ls @upside # list all urls in channel @upside
            ira ls # list all of your downloaded files
            ira ls three # show the permaurl for name "three"
            ira search bitcoin | ira ls # list all content & channels w bitcoin

search | SEARCH FOR STUFF
-------------------------
    This will typically be the first action in a pipeline.

    examples:
            ira search game of thrones # find content matching "game of thrones"
            ira search -audio -file techno # find techno audio files

    supported switches for search:
            -audio          -- search for audio files
            -video          -- search for video files
            -text           -- search for text files
            -application    -- search for application files
            -channel        -- only search for channels
            -file           -- search for downloadable files (aka not channels)

    By default, search will search for every file type.

related | FIND SIMILAR STUFF
----------------------------
    NOTE: this command is being worked on. Currently, it only produces the related
    stuff and deletes the original URL (I've yet to decide if this is OK)

    Used against a known url usually. Produces what you'd see on the "related"
    sidebar.

    examples:
            ira search football | ira related # find a bunch of football stuff

filter | WEED OUT STUFF
-----------------------
    Use stock filters to select the stuff you want

    examples:
            ira search cat | ira filter image # find images of cats on LBRY
            ira search cat | ira filter image nofee # same as above, but free stuff

    supported filters:
            tube        cross posted on youtube?
            notube      not cross-posted at youtube
            video[s]    is video?
            novideo[s]
            image[s]    is image?
            noimage[s]
            audio       is audio?
            noaudio
            mp4         is an mp4?
            nomp4
            fee         costs money?
            nofee
            sfw         is safe for work?
            nsfw
            nosfw       same as nsfw
            haschannel  belongs to a channel
            nochannel   is "anonymous"
            ischannel   url refers to channel?
            isfile      url refers to a downloadable file?
            isntchannel same as above

    If the default filters are not enough for you, see "as searchline" and grep your
    own up.

download | DOWNLOAD THE FILES
-----------------------------
    So this one's risky, unless you trust a channel IMO. You could be downloading
    huge amounts of stuff. And if you don't filter by 'nofee', you'll be paying for
    it. But it's up to you!

    examples:
            ira ls @doggos | ira download # download every damn thing from @Luke
            ira ls @doggos | head -n 10 | ira download # or just the latest 10 things

as | CONVERT THE LIST
---------------------
    Some stock converters so you can use the data elsewhere.

    examples:
            ira search cat | ira as links # show as lbry:// links
            ira search cat | ira download | ira as filelist # show as local file path
            ira as json @upside # get all info on @upside as a json dictionary

    available converters:
            links       -- insert "lbry://" before the URL
            niceurl(s)  -- convert generic urls to complete, @channel-prefixed urls if possible
            rawurl(s)   -- to simple name#claimID form
            filelist    -- replace with full path of download file on disk, if available
            json        -- create a list of json data from running resolve() on every url
            channels    -- show only the @channels the files belong to, and nothing else.
            vanity      -- just the name, without the claimID noise
            searchline  -- a messy metadata dump for searching with grep

    searchline deserves special mention! It's basically a dump of all the
    information in a claim on one line, like this:
    [claim url]\\t[textdump of resolve()]

    the purpose is so that you can search or filter with UNIX like tools to do as
    you like with the list before passing it back to ira. For example:

            ira search cat | ira as searchline | grep -i cute | ira download

    This will download all "cat" related stuff with the word "cute" somewhere.

            ira search bond | ira as searchline | grep -i octet-stream

    This will find those "other" files.

    PLEASE NOTE: there is no real format for "searchline"; it's just a dump right
    now. In the future it may be more semantically interesting and parseable.

claims | SEEKING DEEP
---------------------
    To see all the urls contesting for a claim, use "claims"
    example:
            ira claims one two three

    This will show all the claims vying for the top 3 spots on "Community Bids", even
    if their files have been abandoned

dump | CREATE A SIDE FILE
-------------------------
    You may want to dump information to a file for later processing. This can help in
    creating more complex workflows.

    example:
            ira search movies | ira dump movieurls.txt | ira download > moviefiles.txt

    This downloads movies, keeps a record of their urls and their filenames in movieurls.txt
    and moviefiles.txt respectively.

columns | CONSTRUCT COLUMNAR DATA
---------------------------------
    This one is so you can take the resuts into a .csv type table, or sort by column in
    clever unixy way.

    example:
            ira search lbry | ira column channel_name effective_amount

    This will search for claims matching 'lbry' and list the URL, channel_name, and
    bid amount ("effective_amount") in a table.

    You can use any term in the LBRY SCHEMA for a column. If there's namespace ambiguity,
    you can use dot-notation, like:
            ira claims one two three | ira columns certificate.claim_id

    If you're confused as to all the different field names, try an "as JSON" to see them
            ira as JSON @upside/blog

wait | WAIT FOR CHANGES
-----------------------
    The wait command sits until something happens at a url, so it can be
    used as a remote trigger, for monitoring a URL, or polling for content.

    example:
            ira wait trigger-url | ira download | ffplay myalarm.mp3

    This will wait until the url trigger-url is changed in any way, download
    it, then play myalarm.mp3

    When "trigger-url" changes, its permanent url is printed to stdout for your
    use.  This can be used for remote triggering (obviously) or simply
    monitoring a URL for changes.

    This works on permanent URLs, URLs without content, and @channel names.

    By default, ANY change (including tips, etc) to the location will trigger
    output. In the future, I may create switches so you can monitor for just
    content changes, etc.

    NOTE: this is special, and will only monitor one URL. If piped, only the
    first line is read and used. This may change in the future to act more like
    a select() where you can monitor multiple locations for changes at once

    You need not pipe, rather you might: ira wait trigger-url &&
    some-triggered-command.sh

    So in case of any failure (network, other), the command won't be triggered.

CAVEATS
-------
    ira used to depend upon the pybry wrapper ("pip3 install pybry"). However, pybry
    generates its own code on install using a NON-DETERMINISTIC web address whose
    API syntax and semantics are essentially unknown at time of install.

    Now, ira sports its own wrapper around a subset of lbry api calls. This may break
    future stuff! Just be aware that as the API changes, ira will have to change
    alongside (at least for the parts of the API it uses)

    ira uses threading so that your day isn't wasted. Currently, this means that if you expect
    stuff to remain in a certain order, well, IT WON'T. I'm going to fix this, too, but
    for the time being realize that ira could mix the order up.

FUTURE STUFF
------------
    ira will eventually be able to (re)publish, render to HTML, and so on.
    There's just so much stuff I'd like to be able to do with it, and so little
    time...

    Okay, that's it. Have fun!

"""

if __name__ == "__main__":

    # allow piped readers to end the process early:
    from signal import signal, SIGPIPE, SIG_DFL
    signal(SIGPIPE, SIG_DFL)
    main()

    # "Thread" version
    #worker = Thread(target=main, args=())
    #worker.start()
    #worker.join()
    #main()
