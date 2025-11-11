# """
# Advanced PDF to EPUB Converter with OCR Support
# Supports multi-language PDFs with image-based text extraction
# """

# import os
# import sys
# from pathlib import Path
# from typing import List, Tuple
# import logging

# # Required libraries
# try:
#     import fitz  # PyMuPDF
#     from PIL import Image
#     import pytesseract
#     from ebooklib import epub
#     import io
#     from tqdm import tqdm
# except ImportError as e:
#     print(f"Error: Missing required library - {e}")
#     print("\nPlease install required packages:")
#     print("pip install PyMuPDF Pillow pytesseract ebooklib tqdm")
#     sys.exit(1)

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)


# class PDFToEPUBConverter:
#     """Advanced PDF to EPUB converter with OCR capabilities"""
    
#     def __init__(self, ocr_languages: str = 'eng+hin'):
#         """
#         Initialize converter
        
#         Args:
#             ocr_languages: Tesseract language codes (e.g., 'eng', 'hin', 'eng+hin')
#                           Common codes: eng(English), hin(Hindi), ara(Arabic), 
#                           fra(French), deu(German), spa(Spanish), chi_sim(Chinese)
#         """
#         self.ocr_languages = ocr_languages
#         self.dpi = 300  # High quality for OCR
#         self.min_text_length = 10  # Minimum text length to consider valid
        
#     def extract_text_from_page(self, page) -> str:
#         """Extract text directly from PDF page"""
#         try:
#             text = page.get_text()
#             if text and len(text.strip()) > self.min_text_length:
#                 return text
#         except Exception as e:
#             logger.warning(f"Text extraction failed: {e}")
#         return ""
    
#     def ocr_page(self, page) -> str:
#         """Perform OCR on PDF page"""
#         try:
#             # Convert page to image
#             mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
#             pix = page.get_pixmap(matrix=mat)
            
#             # Convert to PIL Image
#             img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
#             # Perform OCR
#             text = pytesseract.image_to_string(
#                 img,
#                 lang=self.ocr_languages,
#                 config='--psm 1 --oem 3'  # Auto page segmentation with LSTM
#             )
            
#             return text
#         except Exception as e:
#             logger.error(f"OCR failed: {e}")
#             return ""
    
#     def extract_images(self, page) -> List[Tuple[bytes, str]]:
#         """Extract images from PDF page"""
#         images = []
#         try:
#             image_list = page.get_images(full=True)
            
#             for img_index, img in enumerate(image_list):
#                 xref = img[0]
#                 base_image = page.parent.extract_image(xref)
#                 image_bytes = base_image["image"]
#                 image_ext = base_image["ext"]
#                 images.append((image_bytes, image_ext))
                
#         except Exception as e:
#             logger.warning(f"Image extraction failed: {e}")
        
#         return images
    
#     def create_epub(self, pdf_path: str, output_path: str = None, 
#                     use_ocr: bool = True, extract_imgs: bool = True) -> str:
#         """
#         Convert PDF to EPUB
        
#         Args:
#             pdf_path: Path to input PDF file
#             output_path: Path for output EPUB file (optional)
#             use_ocr: Use OCR if direct text extraction fails
#             extract_imgs: Extract and include images in EPUB
            
#         Returns:
#             Path to created EPUB file
#         """
#         # Validate input
#         if not os.path.exists(pdf_path):
#             raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
#         # Set output path
#         if output_path is None:
#             output_path = str(Path(pdf_path).with_suffix('.epub'))
        
#         logger.info(f"Starting conversion: {pdf_path} -> {output_path}")
        
#         # Open PDF
#         pdf_document = fitz.open(pdf_path)
#         total_pages = len(pdf_document)
        
#         # Create EPUB book
#         book = epub.EpubBook()
        
#         # Set metadata
#         book_title = Path(pdf_path).stem
#         book.set_identifier(f'id_{book_title}')
#         book.set_title(book_title)
#         book.set_language('en')
#         book.add_author('PDF Converter')
        
#         # Process pages
#         chapters = []
#         image_counter = 0
        
#         for page_num in tqdm(range(total_pages), desc="Processing pages"):
#             page = pdf_document[page_num]
            
#             # Extract text
#             text = self.extract_text_from_page(page)
            
#             # Use OCR if needed
#             if use_ocr and len(text.strip()) < self.min_text_length:
#                 logger.info(f"Using OCR for page {page_num + 1}")
#                 text = self.ocr_page(page)
            
#             # Create chapter
#             chapter_title = f'Page {page_num + 1}'
#             chapter = epub.EpubHtml(
#                 title=chapter_title,
#                 file_name=f'chap_{page_num:04d}.xhtml',
#                 lang='en'
#             )
            
#             # Build chapter content
#             content = f'<h2>{chapter_title}</h2>'
            
#             # Add images if enabled
#             if extract_imgs:
#                 images = self.extract_images(page)
#                 for img_bytes, img_ext in images:
#                     image_counter += 1
#                     img_name = f'image_{image_counter}.{img_ext}'
                    
#                     # Create image item
#                     img_item = epub.EpubItem(
#                         uid=f'img_{image_counter}',
#                         file_name=f'images/{img_name}',
#                         media_type=f'image/{img_ext}',
#                         content=img_bytes
#                     )
#                     book.add_item(img_item)
                    
#                     # Add image to content
#                     content += f'<img src="images/{img_name}" alt="Image {image_counter}"/>'
            
#             # Add text content
#             if text.strip():
#                 content += f'<div>{self._format_text(text)}</div>'
            
#             chapter.content = content
#             book.add_item(chapter)
#             chapters.append(chapter)
        
#         # Close PDF
#         pdf_document.close()
        
#         # Define Table of Contents
#         book.toc = tuple(chapters)
        
#         # Add navigation files
#         book.add_item(epub.EpubNcx())
#         book.add_item(epub.EpubNav())
        
#         # Define spine
#         book.spine = ['nav'] + chapters
        
#         # Add default CSS
#         style = '''
#         body { font-family: Arial, sans-serif; line-height: 1.6; margin: 2em; }
#         h2 { color: #333; margin-top: 1em; }
#         img { max-width: 100%; height: auto; margin: 1em 0; }
#         p { margin: 0.5em 0; text-align: justify; }
#         '''
#         nav_css = epub.EpubItem(
#             uid="style_nav",
#             file_name="style/nav.css",
#             media_type="text/css",
#             content=style
#         )
#         book.add_item(nav_css)
        
#         # Write EPUB file
#         epub.write_epub(output_path, book, {})
        
#         logger.info(f"✓ EPUB created successfully: {output_path}")
#         logger.info(f"  Total pages processed: {total_pages}")
#         logger.info(f"  Images extracted: {image_counter}")
        
#         return output_path
    
#     def _format_text(self, text: str) -> str:
#         """Format text for EPUB with proper paragraphs"""
#         paragraphs = text.split('\n\n')
#         formatted = []
        
#         for para in paragraphs:
#             para = para.strip().replace('\n', ' ')
#             if para:
#                 formatted.append(f'<p>{para}</p>')
        
#         return '\n'.join(formatted) if formatted else f'<p>{text}</p>'


# def main():
#     """Main function for command-line usage"""
#     import argparse
    
#     parser = argparse.ArgumentParser(
#         description='Convert PDF to EPUB with OCR support'
#     )
#     parser.add_argument(
#         'pdf_path',
#         help='Path to input PDF file'
#     )
#     parser.add_argument(
#         '-o', '--output',
#         help='Output EPUB file path (optional)',
#         default=None
#     )
#     parser.add_argument(
#         '-l', '--languages',
#         help='OCR languages (e.g., eng, hin, eng+hin+ara)',
#         default='eng+hin'
#     )
#     parser.add_argument(
#         '--no-ocr',
#         action='store_true',
#         help='Disable OCR (only extract existing text)'
#     )
#     parser.add_argument(
#         '--no-images',
#         action='store_true',
#         help='Do not extract images'
#     )
    
#     args = parser.parse_args()
    
#     # Create converter
#     converter = PDFToEPUBConverter(ocr_languages=args.languages)
    
#     # Convert
#     try:
#         output_path = converter.create_epub(
#             pdf_path=args.pdf_path,
#             output_path=args.output,
#             use_ocr=not args.no_ocr,
#             extract_imgs=not args.no_images
#         )
#         print(f"\n✓ Success! EPUB created: {output_path}")
        
#     except Exception as e:
#         logger.error(f"Conversion failed: {e}")
#         sys.exit(1)


# if __name__ == "__main__":
#     # Example usage
#     if len(sys.argv) > 1:
#         main()
#     else:
#         print("PDF to EPUB Converter with OCR")
#         print("\nUsage:")
#         print("  python converter.py input.pdf")
#         print("  python converter.py input.pdf -o output.epub")
#         print("  python converter.py input.pdf -l eng+hin")
#         print("\nProgrammatic usage:")
#         print("  converter = PDFToEPUBConverter(ocr_languages='eng+hin')")
#         print("  converter.create_epub('input.pdf', 'output.epub')")





"""
Advanced PDF to EPUB Converter with OCR Support
Supports multi-language PDFs with image-based text extraction
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple
import logging

# Required libraries
try:
    import fitz  # PyMuPDF
    from PIL import Image
    import pytesseract
    from ebooklib import epub
    import io
    from tqdm import tqdm
    import langdetect
    from langdetect import detect_langs
except ImportError as e:
    print(f"Error: Missing required library - {e}")
    print("\nPlease install required packages:")
    print("pip install PyMuPDF Pillow pytesseract ebooklib tqdm langdetect")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFToEPUBConverter:
    """Advanced PDF to EPUB converter with OCR capabilities"""
    
    # Language mapping for OCR
    LANG_MAP = {
        'en': 'eng', 'hi': 'hin', 'ar': 'ara', 'zh-cn': 'chi_sim', 
        'zh-tw': 'chi_tra', 'fr': 'fra', 'de': 'deu', 'es': 'spa',
        'it': 'ita', 'ja': 'jpn', 'ko': 'kor', 'pt': 'por', 'ru': 'rus',
        'tr': 'trk', 'vi': 'vie', 'th': 'tha', 'bn': 'ben', 'ta': 'tam',
        'te': 'tel', 'mr': 'mar', 'gu': 'guj', 'kn': 'kan', 'ml': 'mal',
        'pa': 'pan', 'ur': 'urd'
    }
    
    def __init__(self, ocr_languages: str = None):
        """
        Initialize converter
        
        Args:
            ocr_languages: Tesseract language codes (auto-detect if None)
        """
        self.ocr_languages = ocr_languages
        self.dpi = 300  # High quality for OCR
        self.min_text_length = 10  # Minimum text length to consider valid
        self.detected_languages = set()
        
    def detect_language(self, text: str) -> str:
        """Detect language from text sample"""
        try:
            if len(text.strip()) < 20:
                return 'eng'
            
            langs = detect_langs(text[:1000])
            detected = langs[0].lang if langs else 'en'
            
            # Map to Tesseract language code
            ocr_lang = self.LANG_MAP.get(detected, 'eng')
            self.detected_languages.add(ocr_lang)
            
            return ocr_lang
        except:
            return 'eng'
    
    def extract_text_from_page(self, page) -> str:
        """Extract text directly from PDF page with formatting preservation"""
        try:
            # Extract text with layout preservation
            blocks = page.get_text("dict")["blocks"]
            text_parts = []
            
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        if line_text.strip():
                            text_parts.append(line_text.strip())
            
            text = "\n".join(text_parts)
            
            if text and len(text.strip()) > self.min_text_length:
                return text
        except Exception as e:
            logger.warning(f"Text extraction failed: {e}")
        return ""
    
    def ocr_page(self, page, lang: str = None) -> str:
        """Perform OCR on PDF page with auto language detection"""
        try:
            # Convert page to image
            mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Use provided language or detected languages
            ocr_lang = lang or self.ocr_languages or '+'.join(self.detected_languages) or 'eng'
            
            # Perform OCR
            text = pytesseract.image_to_string(
                img,
                lang=ocr_lang,
                config='--psm 1 --oem 3'  # Auto page segmentation with LSTM
            )
            
            return text
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
    
    def extract_images(self, page) -> List[Tuple[bytes, str]]:
        """Extract images from PDF page"""
        images = []
        try:
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                images.append((image_bytes, image_ext))
                
        except Exception as e:
            logger.warning(f"Image extraction failed: {e}")
        
        return images
    
    def create_epub(self, pdf_path: str, output_path: str = None, 
                    use_ocr: bool = True, extract_imgs: bool = True) -> str:
        """
        Convert PDF to EPUB
        
        Args:
            pdf_path: Path to input PDF file
            output_path: Path for output EPUB file (optional)
            use_ocr: Use OCR if direct text extraction fails
            extract_imgs: Extract and include images in EPUB
            
        Returns:
            Path to created EPUB file
        """
        # Validate input
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Set output path
        if output_path is None:
            output_path = str(Path(pdf_path).with_suffix('.epub'))
        
        logger.info(f"Starting conversion: {pdf_path} -> {output_path}")
        
        # Open PDF
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        
        # Create EPUB book
        book = epub.EpubBook()
        
        # Set metadata
        book_title = Path(pdf_path).stem
        book.set_identifier(f'id_{book_title}')
        book.set_title(book_title)
        book.set_language('en')
        book.add_author('PDF Converter')
        
        # Process pages
        chapters = []
        image_counter = 0
        auto_lang_mode = self.ocr_languages is None
        
        logger.info("Detecting document language..." if auto_lang_mode else f"Using languages: {self.ocr_languages}")
        
        for page_num in tqdm(range(total_pages), desc="Processing pages"):
            page = pdf_document[page_num]
            
            # Extract text with layout
            text = self.extract_text_from_page(page)
            
            # Auto-detect language from first pages
            if auto_lang_mode and page_num < 3 and text:
                self.detect_language(text)
            
            # Use OCR if needed
            if use_ocr and len(text.strip()) < self.min_text_length:
                logger.info(f"Using OCR for page {page_num + 1}")
                ocr_lang = '+'.join(self.detected_languages) if self.detected_languages else None
                text = self.ocr_page(page, lang=ocr_lang)
                
                # Detect language from OCR text if in auto mode
                if auto_lang_mode and page_num < 5 and text:
                    self.detect_language(text)
            
            # Create chapter
            chapter_title = f'Page {page_num + 1}'
            chapter = epub.EpubHtml(
                title=chapter_title,
                file_name=f'chap_{page_num:04d}.xhtml',
                lang='en'
            )
            
            # Build chapter content
            content = f'<h2>{chapter_title}</h2>'
            
            # Add images if enabled
            if extract_imgs:
                images = self.extract_images(page)
                for img_bytes, img_ext in images:
                    image_counter += 1
                    img_name = f'image_{image_counter}.{img_ext}'
                    
                    # Create image item
                    img_item = epub.EpubItem(
                        uid=f'img_{image_counter}',
                        file_name=f'images/{img_name}',
                        media_type=f'image/{img_ext}',
                        content=img_bytes
                    )
                    book.add_item(img_item)
                    
                    # Add image to content
                    content += f'<img src="images/{img_name}" alt="Image {image_counter}"/>'
            
            # Add text content
            if text.strip():
                content += f'<div>{self._format_text(text)}</div>'
            
            chapter.content = content
            book.add_item(chapter)
            chapters.append(chapter)
        
        # Close PDF
        pdf_document.close()
        
        # Log detected languages
        if auto_lang_mode and self.detected_languages:
            logger.info(f"Detected languages: {', '.join(self.detected_languages)}")
        
        # Define Table of Contents
        book.toc = tuple(chapters)
        
        # Add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Define spine
        book.spine = ['nav'] + chapters
        
        # Add default CSS
        style = '''
        @charset "UTF-8";
        
        body { 
            font-family: Georgia, "Times New Roman", serif;
            line-height: 1.8;
            margin: 1.5em;
            padding: 0;
            color: #333;
            text-align: left;
            font-size: 1em;
        }
        
        h1, h2, h3, h4, h5, h6 { 
            font-family: Arial, Helvetica, sans-serif;
            color: #1a1a1a;
            margin: 1.2em 0 0.6em 0;
            line-height: 1.3;
            font-weight: 600;
        }
        
        h2 { 
            font-size: 1.5em;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.3em;
        }
        
        p { 
            margin: 0.8em 0;
            text-align: justify;
            text-indent: 0;
            orphans: 2;
            widows: 2;
        }
        
        img { 
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5em auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .page-content {
            margin-bottom: 2em;
            page-break-after: auto;
        }
        
        /* Support for RTL languages */
        [dir="rtl"] {
            text-align: right;
            direction: rtl;
        }
        
        /* Better readability */
        blockquote {
            margin: 1em 2em;
            padding: 0.5em 1em;
            border-left: 3px solid #ccc;
            font-style: italic;
        }
        '''
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style
        )
        book.add_item(nav_css)
        
        # Write EPUB file
        epub.write_epub(output_path, book, {})
        
        logger.info(f"✓ EPUB created successfully: {output_path}")
        logger.info(f"  Total pages processed: {total_pages}")
        logger.info(f"  Images extracted: {image_counter}")
        if self.detected_languages:
            logger.info(f"  Languages detected: {', '.join(self.detected_languages)}")
        
        return output_path
    
    def _format_text(self, text: str) -> str:
        """Format text for EPUB with proper paragraphs and structure"""
        if not text or not text.strip():
            return '<p></p>'
        
        # Split into paragraphs (double newline or single newline with significant indent)
        lines = text.split('\n')
        paragraphs = []
        current_para = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
            else:
                current_para.append(line)
        
        # Add last paragraph
        if current_para:
            paragraphs.append(' '.join(current_para))
        
        # Format paragraphs
        formatted = []
        for para in paragraphs:
            if para:
                # Clean up excessive spaces
                para = ' '.join(para.split())
                formatted.append(f'<p>{para}</p>')
        
        return '<div class="page-content">\n' + '\n'.join(formatted) + '\n</div>' if formatted else '<p></p>'


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert PDF to EPUB with OCR support'
    )
    parser.add_argument(
        'pdf_path',
        help='Path to input PDF file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output EPUB file path (optional)',
        default=None
    )
    parser.add_argument(
        '-l', '--languages',
        help='OCR languages (e.g., eng, hin, eng+hin) - Auto-detect if not specified',
        default=None
    )
    parser.add_argument(
        '--no-ocr',
        action='store_true',
        help='Disable OCR (only extract existing text)'
    )
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Do not extract images'
    )
    
    args = parser.parse_args()
    
    # Create converter
    converter = PDFToEPUBConverter(ocr_languages=args.languages)
    
    # Convert
    try:
        output_path = converter.create_epub(
            pdf_path=args.pdf_path,
            output_path=args.output,
            use_ocr=not args.no_ocr,
            extract_imgs=not args.no_images
        )
        print(f"\n✓ Success! EPUB created: {output_path}")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        main()
    else:
        print("PDF to EPUB Converter with OCR")
        print("\nUsage:")
        print("  python converter.py input.pdf")
        print("  python converter.py input.pdf -o output.epub")
        print("  python converter.py input.pdf -l eng+hin  # Manual language")
        print("\nProgrammatic usage:")
        print("  # Auto-detect language")
        print("  converter = PDFToEPUBConverter()")
        print("  converter.create_epub('input.pdf', 'output.epub')")
        print("\n  # Manual language")
        print("  converter = PDFToEPUBConverter(ocr_languages='eng+hin')")
        print("  converter.create_epub('input.pdf')")