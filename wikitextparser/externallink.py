﻿"""Define the ExternalLink class."""

from typing import Optional

from .spans import parse_to_spans
from .wikitext import SubWikiText


class ExternalLink(SubWikiText):

    """Create a new ExternalLink object."""

    @property
    def _shadow(self):
        """Replace main span types with underscores.

        Override the _shadow of SubWikiText to replace comments with
        underscores. This helps to keep them part of the external link.
        """
        ss, se = self._span
        string = self._lststr[0][ss:se]
        cached_string, cached_shadow = getattr(
            self, '_shadow_cache', (None, None)
        )
        if cached_string == string:
            return cached_shadow
        shadow = bytearray(string.encode('ascii', 'replace'))
        spans = parse_to_spans(shadow)
        for s, e in spans['Comment']:
            shadow[s:e] = b'_' * (e - s)
        shadow = shadow.decode()
        self._shadow_cache = (string, shadow)
        return shadow

    @property
    def url(self) -> str:
        """Return the url part of the ExternalLink."""
        if self[0] == '[':
            return self[1:self._shadow.find(' ')]
        return self.string

    @url.setter
    def url(self, newurl: str) -> None:
        """Set a new url for the current ExternalLink."""
        if self[0] == '[':
            url = self.url
            self[1:len('[' + url)] = newurl
        else:
            url = self.url
            self[0:len(url)] = newurl

    @property
    def text(self) -> Optional[str]:
        """Return the display text of the external link.

        Return self.string if this is a bare link.
        Return None if external link is in brackets but has no link text.
        """
        if self[0] == '[':
            s = self._shadow.find(' ')
            if s == -1:
                return None
            return self[s + 1:-1]
        return self.string

    @text.setter
    def text(self, newtext: str) -> None:
        """Set a new text for the current ExternalLink.

        Automatically put the ExternalLink in brackets if it's not already.
        """
        string = self.string
        if string[0] == '[':
            text = self.text
            if text:
                self[-len(text) - 1:-1] = newtext
                return
            self.insert(-1, ' ' + newtext)
            return
        self.insert(len(string), ' ' + newtext + ']')
        self.insert(0, '[')

    @property
    def in_brackets(self) -> bool:
        """Return true if the ExternalLink is in brackets. False otherwise."""
        # Todo: Deprecate?
        # warn(
        #     'ExternalLink.in_brackets is deprecated. '
        #     'Use external_link[0] == "[" instead',
        #     DeprecationWarning,
        # )
        return self[0] == '['
