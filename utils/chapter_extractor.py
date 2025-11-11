import re
import pdfplumber

def extract_toc_and_chapters(pdf_path: str, max_pages_for_toc=30):
    toc_list = []
    chapters = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Try PDF outline first
            if hasattr(pdf, 'outline') and pdf.outline:
                for item in pdf.outline:
                    if hasattr(item, 'page_number'):
                        toc_list.append({
                            "title": getattr(item, 'title', str(item)),
                            "page_number": item.page_number - 1
                        })
    except Exception as e:
        print(f"Outline extraction failed: {e}")

    # Fallback text-based TOC detection if no outline found
    if not toc_list:
        print("⚙️ No outline found — using fallback TOC detection...")
        toc_list = fallback_toc_detection(pdf_path, max_pages_for_toc)

    # Chapter detection from full text
    chapters = detect_chapters(pdf_path)

    return {
        "toc": toc_list,
        "chapters": chapters
    }

def fallback_toc_detection(pdf_path, max_pages=30):
    toc_items = []
    with pdfplumber.open(pdf_path) as pdf:
        toc_started = False
        toc_ended = False
        for page_index, page in enumerate(pdf.pages[:max_pages]):
            try:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split('\n')
                found_on_this_page = False

                for line in lines:
                    clean_line = line.strip()
                    if not clean_line:
                        continue

                    # TOC start (supports Hindi and English)
                    if not toc_started and any(k in clean_line.lower() for k in 
                        ['table of contents', 'contents', 'विषयसूची']):
                        toc_started = True
                        continue

                    # Detect TOC lines like "Chapter 1 .... 5" or "प्रकरण 1 .... 10"
                    if toc_started and re.match(r'.+\.+\s*\d+$', clean_line):
                        found_on_this_page = True
                        title = re.sub(r'\.+\s*\d+$', '', clean_line).strip()
                        page_num_match = re.search(r'(\d+)$', clean_line)
                        if title and page_num_match:
                            toc_items.append({
                                "title": title,
                                "page_number": int(page_num_match.group(1)) - 1
                            })

                    # TOC end (detect start of chapters)
                    if toc_started and not found_on_this_page:
                        if re.search(r'^(introduction|chapter\s*1|प्रस्तावना|प्रकरण\s*1)', clean_line.lower()):
                            toc_ended = True
                            break

                if toc_ended:
                    break

            except Exception as e:
                print(f"Error on page {page_index}: {e}")
                continue

    print(f"✅ Extracted {len(toc_items)} TOC entries")
    return toc_items


def detect_chapters(pdf_path):
    """
    Detect chapter start pages using text patterns in both English and Hindi.
    """
    chapters = []
    chapter_pattern = re.compile(
        r'^(chapter\s*\d+|chap\.?\s*\d+|प्रकरण\s*\d+|अध्याय\s*\d+|अध्याय|chapter|section\s*\d+)',
        re.IGNORECASE
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            try:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split('\n')
                for line in lines[:20]:  # Only check top lines — titles are usually at top
                    clean_line = line.strip()
                    if not clean_line:
                        continue

                    # Match English or Hindi chapter headers
                    if chapter_pattern.match(clean_line.lower()):
                        lang = "hindi" if re.search(r'[अ-ह]', clean_line) else "english"
                        chapters.append({
                            "title": clean_line,
                            "start_page": page_index,
                            "language_guess": lang
                        })
                        break
            except Exception as e:
                print(f"Error reading page {page_index}: {e}")
                continue

    # Add next_chapter_page for convenience
    for i in range(len(chapters) - 1):
        chapters[i]["next_chapter_page"] = chapters[i + 1]["start_page"]

    print(f"📖 Detected {len(chapters)} chapter starts")
    return chapters
