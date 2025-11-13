from models.book_models import BookInDB
import json
from utils.r2_utils import download_from_r2, upload_to_r2
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import collections
from database.connection import database, books_collection
from bson import ObjectId
from fastapi import HTTPException
from utils.CalibreEPUBtoPDF import CalibreEPUBtoPDF
from weasyprint import HTML
import tempfile
from utils.CalibreDocumentConverter import CalibreDocumentConverter, CalibreSpecializedConverters
from document_converter.EPUBToPDFConverter import convert_epub_to_pdf
from document_converter.PDFToEPUBConverter import pdf_to_epub_with_cover

class BookConvertor:

    def __init__(self, book: BookInDB):
        self.book = book
        self.bucket = os.environ["R2_BUCKET"]
        # print('book : ', book.book_content_url.epub)
        # print(json.dumps(book.model_dump(), indent=2, default=str))
        # here we download files
        self.should_download()

        # get extention of file
        self.ext = self.check_file_extions(self.local_path)["ext"]
        print("ext -> ", self.ext)

        # self.converter = CalibreDocumentConverter();
        # self.specialize = CalibreSpecializedConverters(converter=self.converter)
        # self.specialize.docx_to_epub("./documents/ebook_final.docx", "./documents/ebook_final.epub")
        # self.specialize.docx_to_pdf("./documents/ebook_final.docx","./documents/ebook_final.pdf")
        # convert_epub_to_pdf("./documents/ebook_final.epub", "./documents/ebook_final_converted.pdf")
        # pdf_to_epub_with_cover("./documents/ebook_final_converted.pdf", "./documents/ebook_final.epub",  dpi=300, verbose=True)
        # try to convert pdf to epub using easyOCR
        
        # decide what to do
        if self.ext == "epub":
            """
            1. extract chapter from epub files store it in chapters{title: '', page_number:''}
            2. convert it into pdf and store in r2 and link store in book_content_url
            """
            # step 1:
            # self.robust_toc_extractor(self.local_path)
            # self.robust_toc_extractor_from_epub("./documents/book_epub.epub")

            # step 2 -> epub to pdf
            # self.convertor = CalibreEPUBtoPDF();
            # self.convertor.convert_epub_to_pdf("./documents/book_epub.epub")
            # self.convertor.convert(
            #     self.local_path,
            #     f"{self.check_file_extions(self.local_path)['base']}.pdf",
            # )
            
        elif self.ext == "pdf":
            """
            1. extract chapte from pdf files and  store it
            2. create epub files and store it
            """
            print("pdf")
        elif self.ext == "docx":
            """
            1. create epub files from it  and store it
            2. extract chapter from epub files and store it
            3. create pdf files from it and store it

            """
            self.specialize.docx_to_epub("./documents/ebook_final.docx")
            self.specialize.docx_to_pdf("./documents/ebook_final.docx")
            print("docx")

    def should_download(self):
        for ext, url in self.book.book_content_url:
            if url:
                self.local_path = f"./documents/{os.path.basename(str(url))}"
                self.key = f"documents/{os.path.basename(str(url))}"
                download_from_r2(self.bucket, self.key, self.local_path)

    def check_file_extions(self, path) -> dict:
        return {"base": path.split(".")[-1], "ext": path.split(".")[-1]}

    def store_chapters_in_db(self, id, chapters):
        print("i am storing.......")
        try:
            # Validate book_id
            if not ObjectId.is_valid(book_id):
                raise HTTPException(status_code=400, detail="Invalid book ID format")

            # Prepare update data
            update_data = {
                "$set": {"chapters": chapters_data, "updated_at": datetime.utcnow()}
            }

            # Update document
            result = books_collection.find_one_and_update(
                {"_id": ObjectId(book_id)}, update_data
            )

            if not result:
                raise HTTPException(status_code=404, detail="Book not found")

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error updating chapters: {str(e)}"
            )

    def robust_toc_extractor_from_epub(self, epub_path, debug: bool = False):
        """
        Ultra-robust EPUB TOC extractor:
        - Traverses deeply nested TOC (recursive)
        - Handles epub.Link, epub.Section, tuple formats
        - Preserves TOC hierarchy
        - Cleans HTML titles and fixes Unicode
        - Skips duplicates safely
        - store chapter in mongodb
        """

        def clean_title(title: str) -> str:
            """Clean HTML tags and normalize spaces."""
            if not title:
                return ""
            title = BeautifulSoup(title, "html.parser").get_text()
            title = re.sub(r"\s+", " ", title).strip()
            return title

        try:
            book = epub.read_epub(epub_path)
            toc = getattr(book, "toc", None)
            if not toc:
                if debug:
                    print("⚠️ No TOC found in EPUB.")
                return []

            all_chapters = []

            def traverse_toc(items, level=0):
                """Recursive traversal to flatten TOC completely."""
                chapters = []
                for item in items:
                    # Case 1: epub.Link object
                    if isinstance(item, epub.Link):
                        title = clean_title(getattr(item, "title", "Untitled"))
                        href = getattr(item, "href", "")
                        chapters.append({"title": title, "href": href, "level": level})

                    # Case 2: epub.Section
                    elif isinstance(item, epub.Section):
                        section_title = clean_title(getattr(item, "title", ""))
                        if section_title:
                            chapters.append(
                                {"title": section_title, "href": "", "level": level}
                            )
                        # Deep traverse into nested items
                        section_items = getattr(item, "items", [])
                        if section_items:
                            chapters.extend(traverse_toc(section_items, level + 1))

                    # Case 3: Tuple structure
                    elif isinstance(item, (tuple, list)):
                        # Sometimes tuple -> (title, href) or (Link, subitems)
                        if len(item) == 2 and isinstance(item[0], str):
                            title = clean_title(item[0])
                            href = str(item[1]) if isinstance(item[1], str) else ""
                            chapters.append(
                                {"title": title, "href": href, "level": level}
                            )
                        else:
                            # Mixed nested structures
                            for sub in item:
                                chapters.extend(traverse_toc([sub], level))

                    # Unknown structure - skip
                    else:
                        if debug:
                            print(
                                f"⚠️ Unknown TOC item type: {type(item)} -> {repr(item)[:120]}"
                            )

                return chapters

            # Fully flatten the TOC
            all_chapters = traverse_toc(toc)

            # Deduplicate by title + href
            seen = set()
            unique_chapters = []
            for ch in all_chapters:
                key = (ch["title"], ch["href"])
                if key not in seen and ch["title"]:
                    unique_chapters.append(ch)
                    seen.add(key)

            if debug:
                print(f"✅ Extracted {len(unique_chapters)} chapters:")
                for ch in unique_chapters:
                    indent = "  " * ch["level"]
                    print(f"{indent}- {ch['title']} ({ch['href']})")

            # store chapter in mongo db
            self.store_chapters_in_db(self.book.id, unique_chapters)
            return unique_chapters

        except Exception as e:
            if debug:
                print(f"❌ Error reading EPUB: {e}")
            return []

    def epub_to_pdf(self, epub_path, pdf_path):
        """
        Convert EPUB file to PDF format

        Args:
            epub_path (str): Path to input EPUB file
            pdf_path (str): Path to output PDF file

        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            # Read EPUB file
            book = epub.read_epub(epub_path)

            # Extract all text content from EPUB
            html_content = ""

            for item in book.get_items():
                if item.get_type() == epub.ebooklib.ITEM_DOCUMENT:
                    # Parse HTML content
                    soup = BeautifulSoup(item.get_content(), "html.parser")

                    # Remove unwanted tags
                    for tag in soup(["script", "style", "nav"]):
                        tag.decompose()

                    html_content += str(soup) + "<br/>"

            # Convert HTML to PDF
            HTML(string=html_content).write_pdf(pdf_path)

            print(f"Successfully converted {epub_path} to {pdf_path}")
            return True

        except Exception as e:
            print(f"Error converting EPUB to PDF: {str(e)}")
            return False

    def epub_to_pdf_enhanced(self, epub_path, pdf_path, css_styles=None):
        """
        Enhanced EPUB to PDF converter with better formatting

        Args:
            epub_path (str): Path to input EPUB file
            pdf_path (str): Path to output PDF file
            css_styles (str): Custom CSS styles for PDF formatting

        Returns:
            bool: True if conversion successful, False otherwise
        """

        # Default CSS styles for better PDF formatting
        default_css = """
        @page {
            size: A4;
            margin: 1in;
        }
        body {
            font-family: "Times New Roman", serif;
            font-size: 12pt;
            line-height: 1.6;
        }
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        """

        css_styles = css_styles or default_css

        try:
            # Read EPUB file
            book = epub.read_epub(epub_path)

            # Get book metadata
            title = "Unknown Title"
            if book.get_metadata("DC", "title"):
                title = book.get_metadata("DC", "title")[0][0]

            # Build complete HTML document
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{title}</title>
                <style>{css_styles}</style>
            </head>
            <body>
                <h1>{title}</h1>
            """

            # Extract and process all document items
            for item in book.get_items():
                if item.get_type() == epub.ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), "html.parser")

                    # Clean up HTML
                    for element in soup(["script", "style", "nav", "header", "footer"]):
                        element.decompose()

                    # Add page breaks between chapters
                    full_html += '<div style="page-break-before: always;"></div>'
                    full_html += str(soup)

            full_html += "</body></html>"

            # Convert to PDF
            HTML(string=full_html).write_pdf(pdf_path)

            print(f"✅ Successfully converted '{epub_path}' to '{pdf_path}'")
            print(f"📄 Output file size: {os.path.getsize(pdf_path)} bytes")
            return True

        except FileNotFoundError:
            print(f"❌ Error: EPUB file not found at {epub_path}")
            return False
        except Exception as e:
            print(f"❌ Error converting EPUB to PDF: {str(e)}")
            return False
