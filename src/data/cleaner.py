import re
import unicodedata


class TextCleaner:

    def clean(self, text: str) -> str:
        if not text:
            return ""

        text = self._normalize_unicode(text)
        text = self._fix_hyphenation(text)
        text = self._remove_page_numbers(text)
        text = self._collapse_whitespace(text)

        return text.strip()

    def _normalize_unicode(self, text: str) -> str:

        return unicodedata.normalize("NFKC", text)

    def _fix_hyphenation(self, text: str) -> str:

        return re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    def _remove_page_numbers(self, text: str) -> str:

        return re.sub(r"\n\s*\d{1,4}\s*\n", "\n", text)

    def _collapse_whitespace(self, text: str) -> str:
        # Plusieurs espaces → un seul espace
        text = re.sub(r"[ \t]+", " ", text)
        # Plus de 2 sauts de ligne → 2 maximum
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text
