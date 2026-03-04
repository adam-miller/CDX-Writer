# cdx_writer
Python script to create CDX index files of WARC data.

[![Build Status](https://travis-ci.org/internetarchive/CDX-Writer.png?branch=master)](https://travis-ci.org/internetarchive/CDX-Writer)

## Usage
Usage: `cdx_writer [options] warc.gz [output.cdx]`

Options:

    -h, --help                  show this help message and exit
    --format=FORMAT             A space-separated list of fields [default: 'N b a m s k r M S V g']
    --use-full-path             Use the full path of the warc file in the 'g' field
    --file-prefix=FILE_PREFIX   Path prefix for warc file name in the 'g' field.
                                Useful if you are going to relocate the warc.gz file
                                after processing it.
    --all-records               By default we only index http responses. Use this flag
                                to index all WARC records in the file
    --screenshot-mode           Special Wayback Machine mode for handling WARCs
                                containing screenshots
    --exclude-list=EXCLUDE_LIST File containing url prefixes to exclude
    --stats-file=STATS_FILE     Output json file containing statistics

If `output.cdx` (second argument) is omitted,
output is written to stdout. The first line of output is the CDX header.
This header line begins with a space so that the cdx file can be passed
through `sort` while keeping the header at the top.

## Format
The supported format options are:

    M meta tags (AIF) *
    N massaged url
    S compressed record size
    V compressed arc file offset *
    a original url **
    b date **
    g file name
    k new style checksum *
    m mime type of original document *
    r redirect *
    s response code *
    Q language-codes
    C simhash
    T sha 256 checksum

    * in alexa-made dat file
    ** in alexa-made dat file meta-data line

More information about the CDX format syntax can be found here:
http://www.archive.org/web/researcher/cdx_legend.php


## Installation

Version 0.4.0 changed the source code layout. `CDX_Writer` is now more like a regular Python library
package. There no longer is `cdx_writer.py` script in the
source tree; `cdx_writer` script will be created
through package installation with `pip`.

It is recommended to install this package into its own
virtualenv, or create a PEX.

Install into a vitualenv with`:

```
$ virtualenv /opt/cdx_writer
$ /opt/cdx_writer/bin/pip install -r requirements.txt .
```
This will install Command line script `cdx_writer` into `/opt/cdx_writer/bin`.

Create PEX with:
```
$ pex -r requirements.txt -o cdx_writer.pex -m cdx_writer .
```
Note that `setup.py` does not specify full dependencies because this package
depends on non-published version of `warctools`. Please install dependencies
through `requirements.txt`.

**Another option is to run `cdx_writer` using the provided `Dockerfile`.**

## Differences from archive-access cdx files

The CDX files produced by the [archive-access](http://sourceforge.net/projects/archive-access/)
and that produced by `cdx_writer` differ in these cases:

### SURT:

* archive-access doesn't encode the %7F character in SURTs

### MIME Type:

* archive-access does not parse mime type for large warc payloads, and just returns `unk`
* If the HTTP `Content-Type` header is sent with a blank value, archive-access
returns the value of the previous header as the mime type. cdx_writer
returns `unk` in this case. Example WARC Record (returns `close` as the mime type):
    <code>...Content-Length: 0\r\nConnection: close\r\nContent-Type: \r\n\r\n\r\n\r\n</code>

### Redirect URL:

* archive-access does not escape whitespace, cdx_writer uses `%20` escaping so we can split these files on whitespace.
* archive-access removes unicode characters from redirect URLs, cdx_writer version keeps them
* archive-access does not decode HTML entities in redirect URLs
* archive-access sometimes does not turn relative URLs into absolute urls
* archive-access sometimes does not remove `/../` from redirect URLs
* archive-access uses the value from the previous HTTP header for the redirect URL if the `Location` header is empty
* cdx_writer only looks for `http-equiv=refresh` meta tag inside `HEAD` element

### Meta Tag:

* cdx_writer only looks for meta tags in the `HEAD` element
* archive-access version doesn't parse multiple HTML meta tags, only the first one
* archive-access misses `FI` meta tags sometimes
* cdx_writer always returns tags in `A`, `F`, `I` order. archive-access does not use a consistent order


### HTTP Response Code:
* archive-access returns response code `0` if HTTP header line contains non-ascii bytes:
    <code>HTTP/1.1 302 D\xe9plac\xe9 Temporairement\r\n...</code>
