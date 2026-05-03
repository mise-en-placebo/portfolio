# gen-doi-updates

I was once asked to update a company's DOIs so that all DOIs
pointed to HTTPS resources (instead of just HTTP). There
were many, many ways to go about this, but due to the number
of resources (approximately 150,000, of which about 75,000
needed to be updated), I determined that the best approach
would be to [generate bulk update
files](https://www.crossref.org/documentation/register-maintain-records/maintaining-your-metadata/updating-your-metadata/#00172).

Clearly, this could not be done by hand, so I developed
`gen-doi-updates` to generate the update files for me. I
then manually submitted the update files to Crossref to
update the resources.

Note that this Python script is dependent on the existence
of something called a 'gentag' file. These are simply
XML-based metadata files for any resource. In particular,
these files contain both the DOI for a given resource, as
well as the path that the DOI should point to. However,
these are private files and, for that reason, I did not
include any of these files. Thus the script, while it should
run, won't do much.

## Implementation

The structure of the script is relatively straightforward.

1. First, using the Crossref metadata retrieval API, pull
down relevant metadata for every resource.

2. Next, collect and parse all the local metadata files.

3. Compare the resources between what Crossref has, and what
the local metadata files have. For each DOI, if the DOI is
found in a local metadata file use the resource specified in
the local metadata file.

4. Run various analyses on the updates to be made.

5. If DOIs are to be updated, generated the bulk update
files.

6. Since this pulls down a good amount of information _and_
this information is relatively static, cache the downloaded
data for subsequent runs.

## Notes

As previously mentioned, this script essentially does
nothing as it has none of the local metadata files to work
with. It will, however, pull information down from
Crossref. The information it pulls from Crossref is based on
a hard-coded `PREFIX` value. I have chosen a prefix at
random that returns relatively few results (~1000). Feel
free to change this hard-coded value in the script,
_however_ understand that you may be pulling large amounts
of data from Crossref.

## Running

I have provided one fake metadata file
([`metadata.xml`](./metadata.xml)). Note that if you
change the `PREFIX` value in the script itself, you should
also use a DOI belonging to that prefix in `metadata.xml`.

Then, simply run `./gen-doi-updates --no-cache`. It will:

1. Leave a time-stamped log in `logs/`.

2. Cache the data downloaded from Crossref in
`cache/dois.json`, cache the data extracted from metadata
files in `cache/gentags.json`, and various DOIs in the
`cache/mismatches.json` and `cache/no-updates.json` files.

3. Generate update files in the `updates/` directory. Note
that it will likely only generate one file unless you wish
to generate many fake metadata files.

4. Return a brief summary about the data collected and
updated to `STDOUT`.