#! /usr/bin/python3

############################################################
##                                                        ##
##                        IMPORTS                         ##
##                                                        ##
############################################################

import argparse
import datetime
import json
import logging
import pathlib
import re
import requests
import sys
import xml.dom.minidom
import xml.etree.ElementTree

############################################################
##                                                        ##
##                        GLOBALS                         ##
##                                                        ##
############################################################

EMAIL = 'foo@bar.com'

CREF_API_URL = 'https://api.crossref.org'
PREFIX       = '10.5948'
ENDPOINTS    = [ 'prefixes', PREFIX, 'works' ]
FILTERS      = {
    'select': 'DOI,resource',
    'rows':   1000,
    'cursor': '*',
}

############################################################
##                                                        ##
##                        OPTIONS                         ##
##                                                        ##
############################################################

parser = argparse.ArgumentParser(
    description = (
        "A script for generating update forms for the "
        "Crossref admin tool" 
    )
)

cache_group = parser.add_mutually_exclusive_group()

cache_group.add_argument(
    "--cache",
    dest    = "use_cache",
    action  = "store_true",
    default = True,
    help    = (
        "Attempt to use cached data insteading of "
        "generating it on the fly."
    )
)

cache_group.add_argument(
    "--no-cache",
    dest    = "use_cache",
    action  = "store_false",
    default = True,
    help    = (
        "Generate data on the fly instead of using cached "
        "data" 
    )
)

parser.add_argument(
    '--update-cache',
    dest    = 'update_cache',
    action  = 'store_true',
    default = True,
    help    = (
        "Update cached data. Note: Only does something if "
        "you're not using cached data."
    )
)

parser.add_argument(
    '--rows',
    type    = int,
    default = 2950,
    help    = (
        "Specify the maximum number of rows in a given "
        "update file. Crossref wants you to limit them to "
        "at most 3000 per file. Default: 2950."
    )
)

parser.add_argument(
    '--email',
    type    = str,
    default = EMAIL,
    help    = (
        "Specify the email address to use in the header "
        "line to the update files."
    )
)

parser.add_argument(
    '--compare-mismatches',
    dest    = 'cmp_mismatch',
    action  = 'store_true',
    default = True,
    help    = (
        "If a Crossref DOI is not found in the gentag "
        "DOIs, but it's uppercase is, compare the "
        "differences between the Crossref DOI and the "
        "uppercased DOI."
    )
)

OPTS = parser.parse_args()

############################################################
##                                                        ##
##                        LOGGING                         ##
##                                                        ##
############################################################

Log = logging.getLogger(__name__)

Log.setLevel(logging.DEBUG)

timestamp = str(datetime.datetime.now());
timestamp = re.sub(r"( |\.|:)", '', timestamp)

LogFile = f"logs/{timestamp}.log"

term_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(LogFile)

term_formatter = logging.Formatter('%(message)s')
file_formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(name)s | line: %(lineno)d | %(message)s')

term_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

term_handler.setFormatter(term_formatter)
file_handler.setFormatter(file_formatter)

Log.addHandler(term_handler)
Log.addHandler(file_handler)

############################################################
##                                                        ##
##                    CROSSREF QUERIES                    ##
##                                                        ##
############################################################

class CrossrefQuery:

    def __generate_url(self):
        url = self.base_url

        if self.endpoints is None:
            return url

        for endpoint in self.endpoints:
            url += f"/{endpoint}"

        if self.filters:
            url += '?'
            for filter in self.filters:
                url += f"{filter}={self.filters[filter]}&"

        return url

    def __extract_message(self, response):
        if response is None:
            return None

        try:
            response = response.json()
        except json.JSONDecodeError as exception:
            Log.error(f"Could not convert response as JSON: {exception}")
            reponse = None

        if response is not None:
            message = response['message']

        return message

    def __extract_cursor(self, message):
        if message is None:
            return None
        
        Log.debug("Attempting to extract cursor from message")

        if 'next-cursor' in message:
            cursor = message['next-cursor']
            Log.debug(f"Found cursor {cursor}")
        else:
            cursor = None
            Log.debug("No cursor found")

        if 'items' in message:

            """
            Something annoying here. Crossref uses a
            pagination/cursor scheme; you can request up to
            1000 rows (records) at a time. If your request
            _would_ return more than 1000 rows, it will also
            return a "cursor": basically a unique token that
            will automatically generate the _next_ request
            for you that you can then submit. Unfortunately,
            even once you have reached the end of all the
            possible records, Crossref's API **still**
            returns a cursor, so you end up in an infinite
            loop if you count on the cursor terminating. So
            we'll just do this instead.
            """
            
            if len(message['items']) < self.filters['rows']:
                cursor = None

            return cursor

    def __extract_dois(self, message):
        if message is None:
            return None
        
        Log.debug("Attempting to extract DOIs from response.")
        
        if 'items' not in message:
            Log.warning("No items found in message")
            return None

        dois = {}

        for item in message['items']:
            doi = item['DOI']

            try:
                url = item['resource']['primary']['URL']
            except (KeyError, TypeError) as exception:
                Log.warning(f"Could not find URL for doi {doi}")
                url = None

            dois[doi] = url

        return dois
    
    def __init__(
            self,
            base_url  = CREF_API_URL,
            endpoints = ENDPOINTS,
            filters   = FILTERS,
    ):
        self.base_url  = base_url
        self.endpoints = endpoints
        self.filters   = filters
        self.url       = self.__generate_url();

    def submit(self):
        url = self.url

        Log.debug(f"Attempting GET on {url}")
        
        try:
            response = requests.get(url)
        except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout
        ) as exception:
            Log.error(f"Could not perform GET on {url}: {exception}")
            response = None

        dois   = {}
        cursor = None
            
        if response is not None:
            Log.debug(f"Attempting to convert GET response to JSON")
            message = self.__extract_message(response)
            
            cursor = self.__extract_cursor(message)
            dois   = self.__extract_dois(message)

        self.cursor = cursor

        return dois
    
    def get_total_dois(self):
        url = self.url

        Log.debug(f"Attempting GET on {url}")
        
        try:
            response = requests.get(url)
        except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout
        ) as exception:
            Log.error(f"Could not perform GET on {url}: {exception}")
            response = None

        if response is not None:
            Log.debug(f"Attempting to convert GET response to JSON")
            message = self.__extract_message(response)

            if 'total-results' in message:
                return message['total-results']
            else:
                return 0
            
    def next_query(self, submit = False):
            cursor    = self.cursor
            base_url  = self.base_url
            endpoints = self.endpoints
            filters   = self.filters

            if cursor is None:
                return None

            filters['cursor'] = cursor

            next = CrossrefQuery(
                base_url  = base_url,
                endpoints = endpoints,
                filters   = filters
            )

            return next
        
############################################################
##                                                        ##
##                       FUNCTIONS                        ##
##                                                        ##
############################################################

def get_protocol(url):
    match = re.search(r"^(.*?)://", url)

    if match:
        return match.group(1)
    else:
        Log.debug(f"Could not extract protocol from {url}")

    return None

def uses_https(url):
    protocol = get_protocol(url)

    if protocol is None:
        return False

    return True if protocol == 'https' else False

def download_dois():
    Log.info("Downloading DOI data from Crossref")

    dois  = {}   
    query = CrossrefQuery()

    total_dois = query.get_total_dois()

    while query is not None:
        Log.info(f"{len(dois)}/{total_dois} DOIs downloaded")

        dois.update(query.submit())

        query = query.next_query()

    return dois

def is_gentag(path):
    Log.debug(f"Checking if {path} is a gentag file")
    
    dom = xml.dom.minidom.parse(str(path))

    doctype = ''
    
    if dom.doctype is not None:
        if dom.doctype.systemId:
            doctype = dom.doctype.systemId

    match = re.search(r"^gentag", doctype)

    return True if match else False
        
def find_gentag_files(path):
    Log.info(f"Finding gentags at {path}")

    paths = path.rglob('*.xml')

    gentags = []
    
    for path in paths:
        # Let's ignore hidden files

        if path.name.startswith('.'):
            continue

        # Same for hosted?
        
        if '/hosted/' in f"{path}":
            continue

        if not path.is_file():
            continue
        
        if not is_gentag(path):
            continue

        gentags.append(path)

    return gentags

def parse_gentags(gentag_paths):
    Log.info("Parsing gentag files")

    gentags = {}
    
    for path in gentag_paths:

        Log.debug(f"Parsing gentag file {path}")
        
        gentag = xml.etree.ElementTree.parse(path)

        doi = gentag.find('doi')

        if doi is None:
            Log.warning(f"No DOI found in getag {path}")
            continue

        doi = doi.text

        if doi in gentags:
            Log.warning(
                f"Gentag {path} contains DOI {doi} which "
                f"is already defined as {gentags[doi]}. "
                f"Overwriting it."
            )
        
        uri = gentag.find('uri')

        if uri is None:
            Log.warning(f"No URI found in gentag {path}")
            gentags[doi] = None
            continue

        scheme = None
        
        if uri.attrib and 'scheme' in uri.attrib:
            scheme = uri.attrib['scheme']
            
        host = uri.find('host')
        path = uri.find('path')

        uri = ''

        if scheme is not None:
            uri += f"{scheme}://"
        
        if host is not None:
            uri += host.text

        if path is not None:
            uri += path.text

        gentags[doi] = uri

    return gentags
        
def collect_gentags(
        # These Paths have been obfuscated for the public portfolio.
        
        paths = [
            pathlib.Path('.'),
        ]
):

    Log.info("Collecting gentag files")

    gentag_files = []
        
    for path in paths:
        gentag_files = gentag_files + find_gentag_files(path)

    gentags = parse_gentags(gentag_files)

    return gentags
    
def cache_data(data, file, indent = 4):
    file = pathlib.Path(f"cache/{file}.json")

    Log.debug(f"Attempting to open cache file {file}")

    try:
        with open(file, 'w') as cache_file:
            try:
                json.dump(data, cache_file, indent = indent)
            except Exception:
                Log.error(f"Could not cache data in {file}: {Exception}")

    except FileNotFoundError:
        Log.error("Could not find cache file")
    except ValueError as exception:
        Log.error(f"Error processing contents of {file}: {exception}")
        
def load_cache(file):
    file = pathlib.Path(f"cache/{file}.json")

    Log.debug(f"Loading cache file {file}")
    
    data = None

    try:
        with open(file) as cache_file:
            try:
                data = json.load(cache_file)
            except Exception:
                Log.error(f"Could not cache data in {file}: {Exception}")

    except FileNotFoundError:
        Log.error("Could not find cache file")
    except ValueError as exception:
        Log.error(f"Error processing contents of {file}: {exception}")

    return data

def compare_mismatch(cref_doi, gentag_doi):
    chars = []

    for i in range(len(cref_doi)):

        if cref_doi[i] != gentag_doi[i]:
            
            chars.append({
                'index':  i,
                'cref':   cref_doi[i],
                'gentag': gentag_doi[i],
            })

    return chars

def compare_dois(dois, gentags):
    Log.info(
        "Comparing DOIs from Crossref with DOIs from "
        "gentags"
    )

    mismatches = {}

    for doi in dois:

        if doi in gentags:
            continue

        upper = doi.upper()

        if upper in gentags:

            mismatch = {
                'cref_doi': doi,
                'gentag_doi': upper,
            }
            
            chars = compare_mismatch(doi, upper)
            
            mismatch['chars'] = chars

            if len(chars) not in mismatches:
                mismatches[len(chars)] = []                

            mismatches[len(chars)].append(mismatch)

    return mismatches

def analyze_mismatches(mismatches):
    Log.debug("Analyzing mismatches")

    total = 0

    for num in mismatches:
        total += len(mismatches[num])

    if not total:
        return
        
    Log.debug(f"Total mismatches: {total}")
    
    most_chars_changed = max(mismatches.keys())

    Log.debug(
        f"Largest number of mismatched characters: "
        f"{most_chars_changed}"
    )

    for i in range(1, most_chars_changed + 1):

        num_dois = len(mismatches[i])

        Log.debug(
            f"{num_dois} have {i} letter(s) uppercased."
        )

    s_and_x_only = 0

    for mismatch in mismatches[1]:

        chars = mismatch['chars'][0]

        if chars['cref'] != 's' and chars['cref'] != 'x':
            continue

        s_and_x_only += 1

    Log.debug(
        f"{s_and_x_only}/{len(mismatches[1])} one-change "
        f"DOIs only uppercase an 's' or 'x' (PIIs?)."
    )

    s_and_x_only = 0
    
    for mismatch in mismatches[2]:

        chars = mismatch['chars']

        if chars[0]['cref'] != 's' and chars[0]['cref'] != 'x':
            continue

        if chars[0]['cref'] == 's' and chars[1]['cref'] != 'x':
            continue

        if chars[0]['cref'] == 'x' and chars[1]['cref'] != 's':
            continue

        s_and_x_only += 1

    Log.debug(
        f"{s_and_x_only}/{len(mismatches[2])} two-change "
        f"DOIs only uppercase an 's' or 'x' (PIIs?)."
    )

def update_dois(dois, gentags):
    Log.info("Updating DOIs with gentag URLs")

    updated_dois = []
    no_updates   = []
    
    for doi in dois:

        if doi in gentags:

            if dois[doi] == gentags[doi]:
                continue

            updated_dois.append({
                'doi':   doi,
                'old':   dois[doi],
                'new':   gentags[doi],
                'upper': False, 
            })

        elif doi.upper() in gentags:

            Log.debug(
                f"DOI {doi} not found in gentags, but "
                f"{doi.upper()} is."
            )

            if len(compare_mismatch(doi, doi.upper())) > 2:

                Log.debug(
                    f"DOI {doi} differs too much from the "
                    f"gentag; skipping."
                )

                no_updates.append(doi)

                continue

            else:

                Log.debug(
                    f"DOI {doi} only differs in one or two "
                    f"characters; based on my research, "
                    f"it's PROBABLY just an incorrectly "
                    f"uppercased PII. Probably"
                )

            if dois[doi] == gentags[doi.upper()]:
                continue

            updated_dois.append({
                'doi':   doi,
                'old':   dois[doi],
                'new':   gentags[doi.upper()],
                'upper': True,
            })

        else:

            no_updates.append(doi)

    return updated_dois, no_updates

def make_header(
        email  = OPTS.email,
        prefix = PREFIX,
):
    return f"H: email={email};fromPrefix={prefix}"

def make_update_file(filename, header, data):
    lines = [header + "\n"]

    for doi in data:
        lines.append(f"{doi['doi']}\t{doi['new']}\n")

    Log.info(f"Writing out to {filename}")
        
    with open(f"updates/{filename}.txt", 'w') as file:
        file.writelines(lines)

def make_update_files(
        data,
        dois_per      = OPTS.rows,
        filename_root = 'DOI-update',
        email         = OPTS.email,
):

    Log.info("Making update files")

    num_updates = len(data)

    count = 0

    while count * dois_per < num_updates:
        make_update_file(
            f"{filename_root}-{count}",
            make_header(),
            data[count * dois_per: (count + 1) * dois_per]
        )

        count += 1

def generate_doi_updates():
    Log.info("Generating DOI update files")

    if OPTS.use_cache:
        Log.info("Attempting to load data from cache")

        dois    = load_cache('dois')
        gentags = load_cache('gentags')
    else:
        Log.info("Collecting data from various sources")

        dois    = download_dois()
        gentags = collect_gentags()

    if OPTS.cmp_mismatch:

        mismatches = compare_dois(dois, gentags)

        analyze_mismatches(mismatches)

        cache_data(mismatches, 'mismatches')

    if OPTS.update_cache:
        
        if OPTS.use_cache:
            
            Log.info(
                "Used cache to load data; not updating"
            )
            
        else:
            
            Log.info("Caching data")

            cache_data(dois, 'dois')
            cache_data(gentags, 'gentags')

    updated_dois, no_updates = update_dois(dois, gentags)

    cache_data(sorted(no_updates), 'no-updates')
    
    make_update_files(updated_dois)

    Log.info("\n----------SUMMARY----------\n")

    if OPTS.use_cache:
        Log.info(f"Data was loaded from caches.")
    else:
        Log.info(f"Data was newly harvested.")

    Log.info(f"{len(dois)} DOIs collected from Crossref.")
    Log.info(f"{len(gentags)} DOIs collected from Gentags.")

    num_cref_non_https = 0
    num_gentags_non_https = 0

    for doi in dois:
        if not uses_https(dois[doi]):
            num_cref_non_https += 1

    for doi in gentags:
        if gentags[doi] is not None:
            if  not uses_https(gentags[doi]):
                num_gentags_non_https += 1
    
    Log.info(
        f"{num_cref_non_https}/{len(dois)} Crossref DOIs "
        f"don't use https."
    )
    Log.info(
        f"{num_gentags_non_https}/{len(gentags)} Gentag "
        f"DOIs don't use https." 
    )

    Log.info(
        f"{len(updated_dois)} DOIs are to be updated."
    )

    Log.info(
        f"{len(no_updates)} DOIs will not be updated (could not "
        f"find gentag for DOI; DOI from gentag differs too "
        f"much, resource has not changed, etc)."
    )

    remaining_non_https = 0

    for doi in no_updates:
        if not uses_https(dois[doi]):
            remaining_non_https += 1

    Log.info(
        f"{remaining_non_https}/{len(no_updates)} still don't "
        f"use https."
    )

############################################################
##                                                        ##
##                          MAIN                          ##
##                                                        ##
############################################################

generate_doi_updates()


