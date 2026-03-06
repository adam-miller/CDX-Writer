class PrefixExclusion(object):
    def __init__(self, exclude_list, canonicalizer):
        """Default exclusion implementation that reads URLs from file
        `exclude_list` to compile a list of canonicalized prefixes to be
        matched against ``massaged_url`` of each record.

        :param exclude_list: path of file containing list of URLs to be excluded.
        :param canonicalizer: URL canonicalizer
        """
        self.urlkey = canonicalizer
        self.excludes = []
        with open(exclude_list, 'r') as f:
            for line in f:
                if '' == line.strip():
                    continue
                url = line.split()[0]
                self.excludes.append(self.urlkey(url.encode('latin1')))

    def excluded(self, urlkey):
        # XXX linear search - could be a little more efficient
        for prefix in self.excludes:
            if urlkey.startswith(prefix):
                return True
        return False
