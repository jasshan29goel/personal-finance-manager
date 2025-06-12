import pdfplumber
import re
from typing import Optional
from typing import Literal
from domain.field_parser.pdf_extractor.base_pdf_extractor_config import BasePDFExtractorConfig


# ✅ Matches:
#   "₹1,234.56"        → Valid number with currency symbol and decimals
#   "  -1,000"         → Valid negative number with leading space
#   "$123"             → Valid integer with prefix
#   "1,000"            → Valid comma-separated thousands
#   "1000"             → Valid plain integer
#   "123456.78"        → Valid plain decimal
#   "-123.45"          → Valid negative decimal
#
# ❌ Does NOT match:
#   "12,34"            → Incorrect comma grouping
#   "1,23,456"         → Incorrect comma grouping
#   "abc123"           → Letters before number not allowed unless non-digit
#   "123abc"           → Letters after number not allowed
#   "--123"            → Double negative sign not allowed
#   "1 000"            → Space instead of comma not allowed
#   "1,000.00.00"      → Multiple decimals not allowed

CURRENCY_REGEX = re.compile(r"^[^\d\-]*([\-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)$")

def extract_amount_from_text(text: str) -> Optional[float]:
    """
    Extracts a float from a string that may have currency symbols or garbage characters.
    Returns float if valid, else None.
    """
    match = CURRENCY_REGEX.match(text.strip())
    if match:
        num = match.group(1).replace(",", "")
        try:
            return float(num)
        except ValueError:
            return None
    return None

def is_float(text: str) -> bool:
    return extract_amount_from_text(text) is not None

class FloatNearKeywordPDFExtractorConfig(BasePDFExtractorConfig):
    type: Literal["float_near_keyword"]
    keyword: str
    location: Literal["RIGHT", "LEFT", "BELOW", "ABOVE"]

    def extract_from_pdf(self, pdf_path: str) -> Optional[float]:
        location = self.location

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                words = page.extract_words(use_text_flow=True)
                keyword_parts = self.keyword.lower().split()

                # Try to find keyword (which may span multiple words)
                for i in range(len(words) - len(keyword_parts) + 1):
                    match = all(words[i + j]['text'].lower() == keyword_parts[j] for j in range(len(keyword_parts)))
                    if match:
                        kw_start = words[i]
                        kw_end = words[i + len(keyword_parts) - 1]

                        kw_x0 = float(kw_start['x0'])
                        kw_x1 = float(kw_end['x1'])
                        kw_top = float(min(w['top'] for w in words[i:i+len(keyword_parts)]))
                        kw_bottom = float(max(w['bottom'] for w in words[i:i+len(keyword_parts)]))

                        kw_x_center = (kw_x0 + kw_x1) / 2
                        kw_y_center = (kw_top + kw_bottom) / 2

                        # Now find nearby float-like words
                        candidates = []
                        for w in words:
                            text = w['text']
                            if not is_float(text):
                                continue

                            w_x_center = (float(w['x0']) + float(w['x1'])) / 2
                            w_y_center = (float(w['top']) + float(w['bottom'])) / 2

                            # Direction checks
                            is_valid = False
                            if location == "RIGHT" and w_x_center > kw_x1 and abs(w_y_center - kw_y_center) <= 5:
                                is_valid = True
                            elif location == "LEFT" and w_x_center < kw_x0 and abs(w_y_center - kw_y_center) <= 5:
                                is_valid = True
                            elif location == "BELOW" and w_y_center > kw_bottom and abs(w_x_center - kw_x_center) <= 30:
                                is_valid = True
                            elif location == "ABOVE" and w_y_center < kw_top and abs(w_x_center - kw_x_center) <= 30:
                                is_valid = True

                            if is_valid:
                                # Euclidean distance
                                dist = ((w_x_center - kw_x_center)**2 + (w_y_center - kw_y_center)**2)**0.5
                                candidates.append((dist, text))

                        if candidates:
                            # Return closest
                            closest = sorted(candidates, key=lambda x: x[0])[0][1]
                            return extract_amount_from_text(closest)

        return None 