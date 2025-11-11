# """
# PDF to EPUB Converter - Enhanced with Debug Mode
# Better text extraction + Image support
# """

# import os
# import fitz  # PyMuPDF
# from ebooklib import epub
# from datetime import datetime
# import html as html_module
# import base64

# def debug_pdf_content(pdf_path):
#     """
#     PDF content ko debug karta hai - text ya images check karta hai
#     """
#     print("\n🔍 Debugging PDF Content:")
#     print("="*60)
    
#     doc = fitz.open(pdf_path)
    
#     for page_num in range(len(doc)):
#         page = doc[page_num]
#         text = page.get_text("text")
#         blocks = page.get_text("blocks")
#         images = page.get_images()
        
#         print(f"\nPage {page_num + 1}:")
#         print(f"  Text length: {len(text)} characters")
#         print(f"  Text blocks: {len(blocks)}")
#         print(f"  Images: {len(images)}")
        
#         if text and len(text.strip()) > 0:
#             preview = text[:100].replace('\n', ' ')
#             print(f"  Preview: {preview}...")
#         else:
#             print(f"  ⚠️ No text found - might be scanned/image-based PDF")
    
#     doc.close()
#     print("="*60)


# def create_epub_with_images(pdf_path, epub_path, title="Converted Book", author="Unknown", language="en"):
#     """
#     Text + Images dono ko handle karta hai
#     """
    
#     try:
#         print(f"\n📖 Reading PDF: {pdf_path}")
        
#         # First debug the PDF
#         debug_pdf_content(pdf_path)
        
#         # PDF open karo
#         pdf_doc = fitz.open(pdf_path)
#         total_pages = len(pdf_doc)
#         print(f"\n📄 Converting {total_pages} pages...")
        
#         # EPUB book create karo
#         book = epub.EpubBook()
        
#         # Metadata
#         book.set_identifier(f'id_{datetime.now().timestamp()}')
#         book.set_title(title)
#         book.set_language(language)
#         book.add_author(author)
        
#         # CSS with better image support
#         style = '''
#         @namespace epub "http://www.idpf.org/2007/ops";
#         body {
#             font-family: 'Noto Sans', 'Noto Sans Devanagari', 'Arial Unicode MS', Arial, sans-serif;
#             line-height: 1.8;
#             margin: 1.5em;
#             text-align: justify;
#         }
#         h1, h2 {
#             text-align: left;
#             font-size: 1.2em;
#             margin: 1em 0 0.5em 0;
#             font-weight: bold;
#         }
#         p {
#             margin: 0.8em 0;
#             text-indent: 1em;
#         }
#         .page-number {
#             text-align: center;
#             font-size: 0.9em;
#             color: #666;
#             margin: 2em 0 1em 0;
#             border-top: 1px solid #ddd;
#             padding-top: 1em;
#         }
#         img {
#             max-width: 100%;
#             height: auto;
#             display: block;
#             margin: 1em auto;
#         }
#         .no-content {
#             text-align: center;
#             color: #999;
#             font-style: italic;
#             padding: 2em;
#         }
#         '''
        
#         nav_css = epub.EpubItem(
#             uid="style_nav",
#             file_name="style/nav.css",
#             media_type="text/css",
#             content=style
#         )
#         book.add_item(nav_css)
        
#         chapters = []
#         spine = ['nav']
#         image_counter = 0
        
#         # Har page ko process karo
#         for page_num in range(total_pages):
#             try:
#                 page = pdf_doc[page_num]
                
#                 # Method 1: Simple text extraction
#                 text = page.get_text("text")
                
#                 # Method 2: Text blocks with formatting
#                 blocks = page.get_text("blocks")
                
#                 # Method 3: HTML extraction (better formatting)
#                 html_text = page.get_text("html")
                
#                 # Images extract karo
#                 images = page.get_images()
                
#                 content_parts = []
                
#                 # Text ko process karo
#                 if text and len(text.strip()) > 10:
#                     text = text.strip()
#                     text_escaped = html_module.escape(text)
                    
#                     # Lines ko paragraphs mein convert karo
#                     lines = text_escaped.split('\n')
#                     for line in lines:
#                         line = line.strip()
#                         if line:
#                             # Check if it's a heading (short + uppercase start)
#                             if len(line) < 80 and line[0].isupper() and not line.endswith('.'):
#                                 content_parts.append(f'<h2>{line}</h2>')
#                             else:
#                                 content_parts.append(f'<p>{line}</p>')
                
#                 # Images ko add karo
#                 if images:
#                     print(f"   Page {page_num + 1}: Found {len(images)} images")
#                     for img_index, img in enumerate(images):
#                         try:
#                             xref = img[0]
#                             base_image = pdf_doc.extract_image(xref)
#                             image_bytes = base_image["image"]
#                             image_ext = base_image["ext"]
                            
#                             # Image ko EPUB mein add karo
#                             image_counter += 1
#                             image_name = f"image_{image_counter}.{image_ext}"
                            
#                             image_item = epub.EpubItem(
#                                 uid=f"img_{image_counter}",
#                                 file_name=f"images/{image_name}",
#                                 media_type=f"image/{image_ext}",
#                                 content=image_bytes
#                             )
#                             book.add_item(image_item)
                            
#                             # HTML mein image reference add karo
#                             content_parts.append(f'<img src="images/{image_name}" alt="Image {image_counter}"/>')
                        
#                         except Exception as e:
#                             print(f"   Warning: Could not extract image: {str(e)}")
                
#                 # Agar koi content nahi hai
#                 if not content_parts:
#                     content_parts.append(f'<div class="no-content">Page {page_num + 1} - No text content detected</div>')
                
#                 content_html = '\n        '.join(content_parts)
                
#                 # Chapter create karo
#                 c = epub.EpubHtml(
#                     title=f'Page {page_num + 1}',
#                     file_name=f'page_{page_num + 1}.xhtml',
#                     lang=language
#                 )
                
#                 c.content = f'''<!DOCTYPE html>
# <html xmlns="http://www.w3.org/1999/xhtml" lang="{language}">
# <head>
#     <meta charset="utf-8"/>
#     <title>Page {page_num + 1}</title>
#     <link href="style/nav.css" rel="stylesheet" type="text/css"/>
# </head>
# <body>
#     <div class="page-number">— Page {page_num + 1} —</div>
#     <div class="content">
#         {content_html}
#     </div>
# </body>
# </html>'''
                
#                 book.add_item(c)
#                 chapters.append(c)
#                 spine.append(c)
                
#                 print(f"   ✓ Page {page_num + 1}: {len(text)} chars, {len(images)} images")
            
#             except Exception as e:
#                 print(f"   ✗ Error on page {page_num + 1}: {str(e)}")
#                 continue
        
#         pdf_doc.close()
        
#         if not chapters:
#             print("\n❌ Error: No content extracted from PDF")
#             print("   This might be a scanned PDF without text layer")
#             return False
        
#         # Table of contents
#         book.toc = tuple(chapters)
        
#         # Add navigation
#         book.add_item(epub.EpubNcx())
#         book.add_item(epub.EpubNav())
        
#         # Spine
#         book.spine = spine
        
#         # Write EPUB
#         print(f"\n💾 Writing EPUB file...")
#         epub.write_epub(epub_path, book, {})
        
#         # File sizes
#         pdf_size = os.path.getsize(pdf_path) / 1024
#         epub_size = os.path.getsize(epub_path) / 1024
        
#         print(f"\n✅ Conversion successful!")
#         print(f"   Input PDF: {pdf_size:.2f} KB")
#         print(f"   Output EPUB: {epub_size:.2f} KB")
#         print(f"   Total chapters: {len(chapters)}")
#         print(f"   Total images: {image_counter}")
        
#         if epub_size < pdf_size * 0.1:
#             print(f"\n⚠️  Warning: EPUB is much smaller than PDF")
#             print(f"   This might be a scanned/image-based PDF")
#             print(f"   Consider using OCR to extract text first")
        
#         return True
        
#     except Exception as e:
#         print(f"\n❌ Error: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return False
# import pypandoc

# # Example usage
# if __name__ == "__main__":
#     print("="*60)
#     print("PDF to EPUB Converter with Debug Mode")
#     print("="*60)
    
#     # Convert PDF to EPUB
#     success = create_epub_with_images(
#         pdf_path=r"C:\Users\user\Desktop\readbucks.com\backend\uploads\test_pdf_to_epub.pdf",
#         epub_path=r"C:\Users\user\Desktop\readbucks.com\backend\uploads\test_pdf_to_epub.epub",
#         title="Test Book",
#         author="Author",
#         language="hi"
#     )
    


    
#     if success:
#         print("\n" + "="*60)
#         print("✅ Done! Try opening with:")
#         print("   1. Calibre (Best)")
#         print("   2. Microsoft Edge browser")
#         print("   3. Sumatra PDF")
#         print("="*60)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
import os
import fitz  # PyMuPDF
from ebooklib import epub
from datetime import datetime
import html as html_module
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tempfile

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["PATH"] += os.pathsep + r"C:\Release-25.07.0-0\poppler-25.07.0\Library\bin"

def ocr_extract_text(pdf_path, lang='hin+eng'):
    """
    OCR se har page ka text extract karta hai (Hindi/English)
    """
    print("\n🔍 OCR Mode Enabled: Extracting text from scanned pages...\n")
    text_pages = []

    with tempfile.TemporaryDirectory() as tempdir:
        images = convert_from_path(pdf_path, dpi=300, output_folder=tempdir)
        for i, img in enumerate(images):
            print(f"   🧾 OCR reading page {i+1} ...")
            text = pytesseract.image_to_string(img, lang=lang)
            text_pages.append(text.strip())

    return text_pages


def create_epub_with_images_and_ocr(pdf_path, epub_path, title="Converted Book", author="Unknown", language="hi"):
    """
    Text + Images dono handle karta hai, aur agar text layer missing ho to OCR fallback use karta hai
    """
    try:
        print(f"\n📖 Reading PDF: {pdf_path}")
        pdf_doc = fitz.open(pdf_path)
        total_pages = len(pdf_doc)
        print(f"📄 Total pages: {total_pages}")

        # EPUB initialize
        book = epub.EpubBook()
        book.set_identifier(f'id_{datetime.now().timestamp()}')
        book.set_title(title)
        book.set_language(language)
        book.add_author(author)

        style = '''
        body { font-family: 'Noto Sans Devanagari', 'Nirmala UI', 'Arial Unicode MS', sans-serif; line-height: 1.8; margin: 1.5em; }
        h2 { text-align: left; font-size: 1.1em; margin: 0.5em 0; }
        p { text-indent: 1em; margin: 0.5em 0; }
        .page-number { text-align: center; color: #666; margin: 2em 0 1em 0; border-top: 1px solid #ddd; padding-top: 0.5em; }
        img { max-width: 100%; margin: 1em auto; display: block; }
        '''
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

        chapters = []
        spine = ['nav']
        image_counter = 0
        text_found = False

        # Pass 1: try normal extraction
        extracted_texts = []

        for page_num in range(total_pages):
            page = pdf_doc[page_num]
            text = page.get_text("text")
            extracted_texts.append(text.strip() if text else "")

        # Check if most pages are empty
        non_empty_pages = sum(1 for t in extracted_texts if len(t) > 20)
        if non_empty_pages < total_pages * 0.3:
            print("\n⚠️ Detected mostly image-based PDF — switching to OCR mode\n")
            extracted_texts = ocr_extract_text(pdf_path, lang='hin+eng')

        # Generate EPUB content
        for page_num, text in enumerate(extracted_texts):
            page = pdf_doc[page_num]
            images = page.get_images()

            content_parts = []
            if text and len(text.strip()) > 0:
                text_found = True
                safe_text = html_module.escape(text)
                lines = safe_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if len(line) < 80 and not line.endswith('.'):
                        content_parts.append(f"<h2>{line}</h2>")
                    else:
                        content_parts.append(f"<p>{line}</p>")

            if images:
                print(f"   📸 Page {page_num+1}: Found {len(images)} images")
                for img_index, img in enumerate(images):
                    try:
                        xref = img[0]
                        base_image = pdf_doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        image_counter += 1
                        image_name = f"image_{image_counter}.{image_ext}"
                        image_item = epub.EpubItem(uid=f"img_{image_counter}", file_name=f"images/{image_name}",
                                                   media_type=f"image/{image_ext}", content=image_bytes)
                        book.add_item(image_item)
                        content_parts.append(f'<img src="images/{image_name}" alt="Image {image_counter}"/>')
                    except Exception as e:
                        print(f"      ⚠️ Could not extract image: {e}")

            if not content_parts:
                content_parts.append(f'<div class="no-content">Page {page_num+1} - No readable content</div>')

            content_html = '\n'.join(content_parts)

            chapter = epub.EpubHtml(title=f"Page {page_num + 1}",
                                    file_name=f"page_{page_num + 1}.xhtml",
                                    lang=language)
            chapter.content = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{language}">
<head><meta charset="utf-8"/><title>Page {page_num + 1}</title>
<link href="style/nav.css" rel="stylesheet" type="text/css"/></head>
<body>
<div class="page-number">— Page {page_num + 1} —</div>
<div>{content_html}</div>
</body></html>"""

            book.add_item(chapter)
            chapters.append(chapter)
            spine.append(chapter)

        pdf_doc.close()

        if not text_found:
            print("\n⚠️ No extractable text found — OCR may not have detected properly.")
            return False

        # Final EPUB structure
        book.toc = tuple(chapters)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = spine

        epub.write_epub(epub_path, book)
        print(f"\n✅ EPUB generated successfully: {epub_path}")
        return True

    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False


# Example usage
if __name__ == "__main__":
    success = create_epub_with_images_and_ocr(
        pdf_path=r"C:\Users\user\Desktop\readbucks.com\backend\uploads\book.pdf",
        epub_path=r"C:\Users\user\Desktop\readbucks.com\backend\uploads\book.epub",
        title="Hindi OCR Book",
        author="Amit Dhidhi",
        language="hi"
    )
    # from converter import PDFToEPUBConverter

# Hindi + English support
    # converter = PDFToEPUBConverter(ocr_languages='eng+hin')
    # converter = PDFToEPUBConverter()
    # converter.create_epub(r'C:\Users\user\Desktop\readbucks.com\backend\uploads\test_pdf_to_epub.pdf', r'C:\Users\user\Desktop\readbucks.com\backend\uploads\test_pdf_to_epub.epub')

# Only English
    # converter = PDFToEPUBConverter(ocr_languages='eng')
    # converter.create_epub('document.pdf')
    
    if success:
        print("\n🎉 Done! Open EPUB in Calibre or Edge browser to check result.")
