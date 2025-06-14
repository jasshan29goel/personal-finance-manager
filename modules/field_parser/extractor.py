import pdfplumber
from typing import Dict, Type, List, Optional, Callable
from domain.field_parser_config import BetweenPDFExtractorConfig
from domain.field_parser_config import FloatNearKeywordPDFExtractorConfig
from modules.field_parser.field_parser_utils import extract_amount_from_text, is_float

def extract_between_from_pdf(config: BetweenPDFExtractorConfig, pdf_path: str) -> List[str]:
        results = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text(layout=True) or ""
                    start_idx = text.find(config.start)
                    if start_idx == -1:
                        continue # skip page if marker not found

                    if config.end:
                        end_idx = text.find(config.end, start_idx)
                        content = text[start_idx:end_idx].strip() if end_idx != -1 else text[start_idx:].strip()
                    else:
                        content = text[start_idx:].strip()

                    results.append(content)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

        return results


def extract_float_near_keyword_from_pdf(config: FloatNearKeywordPDFExtractorConfig, pdf_path: str) -> Optional[float]:
    location = config.location

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(use_text_flow=True)
            keyword_parts = config.keyword.lower().split()

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


PDF_EXTRACTOR_DISPATCH: Dict[Type, Callable] = {
    BetweenPDFExtractorConfig: extract_between_from_pdf,
    FloatNearKeywordPDFExtractorConfig: extract_float_near_keyword_from_pdf,
}

def extract_from_pdf(config, pdf_path: str):
    extractor = PDF_EXTRACTOR_DISPATCH[type(config)]
    return extractor(config, pdf_path)
