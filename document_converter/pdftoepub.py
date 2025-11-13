
# import os
# import re
# import subprocess
# import tempfile
# import numpy as np
# from pdf2image import convert_from_path
# import fitz  # PyMuPDF
# import easyocr
# from ebooklib import epub
# from concurrent.futures import ThreadPoolExecutor

# # ---------------------------
# # CONFIG
# # ---------------------------
# PDF_PATH = "documents/ocr.pdf"
# OUTPUT_EPUB = "documents/ocr.epub"
# MAX_THREADS = 4
# LANGUAGES = ['hi', 'en']
# CALIBRE_CMD = "ebook-convert"  # Calibre CLI command

# # ---------------------------
# # STEP 1: TEXT LAYER ANALYSIS
# # ---------------------------
# def is_page_textual(pdf_path, page_num):
#     """Detect if PDF page contains selectable text."""
#     with fitz.open(pdf_path) as doc:
#         page = doc.load_page(page_num)
#         text = page.get_text("text")
#         # If Hindi text contains dotted circles or missing glyphs, consider non-textual
#         if not text.strip():
#             return False
#         if re.search(r"[◌□�]", text):
#             return False
#         return True

# # ---------------------------
# # STEP 2: OCR PAGE FUNCTION (FIXED)
# # ---------------------------
# def ocr_page(reader, page_image, page_num):
#     """OCR a single page image - converts PIL Image to numpy array"""
#     try:
#         # Convert PIL Image to numpy array for EasyOCR
#         image_array = np.array(page_image)
        
#         text_lines = reader.readtext(image_array, detail=0, paragraph=True)
#         text = "\n".join(text_lines)
#         text = re.sub(r'\n{2,}', '\n', text).strip()
#         print(f"🔸 OCR done for page {page_num}")
#         return f"<h2>Page {page_num}</h2><p>{text}</p>"
#     except Exception as e:
#         print(f"❌ Error in OCR for page {page_num}: {str(e)}")
#         return f"<h2>Page {page_num}</h2><p>Error processing page: {str(e)}</p>"

# # ---------------------------
# # STEP 3: HYBRID PROCESSING
# # ---------------------------
# def hybrid_convert(pdf_path, output_epub):
#     print("🔹 Analyzing PDF pages...")
#     with fitz.open(pdf_path) as doc:
#         total_pages = len(doc)
#         text_flags = [is_page_textual(pdf_path, i) for i in range(total_pages)]
#     text_pages = sum(text_flags)
#     print(f"🔍 {text_pages}/{total_pages} pages are textual.")

#     # CASE 1: Mostly text → Use Calibre
#     # if text_pages / total_pages > 0.8:
#     #     print("✅ Mostly text-based. Using Calibre for conversion...")
#     #     cmd = [CALIBRE_CMD, pdf_path, output_epub, "--language", "hi"]
#     #     subprocess.run(cmd, check=True)
#     #     print(f"🎉 EPUB created using Calibre: {output_epub}")
#     #     return

#     # CASE 2: Mostly scanned or broken → Use OCR
#     print("⚙️ Detected image-based/mixed content. Switching to OCR mode...")

#     # Convert to images
#     print("📄 Converting PDF pages to images...")
#     pages = convert_from_path(pdf_path, dpi=250)
    
#     print("🔧 Initializing EasyOCR reader...")
#     reader = easyocr.Reader(LANGUAGES, gpu=False)

#     # OCR with threads
#     results = []
#     print(f"🚀 Starting OCR processing with {MAX_THREADS} threads...")
#     with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
#         for i, page in enumerate(pages, start=1):
#             # print(f"🔍 Submitting page {i} for OCR...")
#             # results.append(executor.submit(ocr_page, reader, page, i))
#             if text_flags[i - 1]:
#                 # Extract text layer for partial textual pages
#                 print(f"📝 Extracting text from page {i} (textual)")
#                 with fitz.open(pdf_path) as doc:
#                     page_obj = doc.load_page(i - 1)
#                     text = page_obj.get_text("text").strip()
#                 html = f"<h2>Page {i}</h2><p>{text}</p>"
#                 results.append(html)
#             else:
#                 print(f"🔍 Submitting page {i} for OCR...")
#                 results.append(executor.submit(ocr_page, reader, page, i))

#     # Collect OCR results
#     print("⏳ Collecting OCR results...")
#     final_pages = [r.result() if not isinstance(r, str) else r for r in results]

#     # Build EPUB
#     print("📚 Building EPUB from OCR and text mix...")
#     book = epub.EpubBook()
#     book.set_identifier("hybrid_pdf_to_epub")
#     book.set_title("Hybrid OCR eBook")
#     book.set_language("hi")

#     # Add chapters
#     for i, content in enumerate(final_pages, start=1):
#         ch = epub.EpubHtml(title=f"Page {i}", file_name=f"page_{i}.xhtml", lang="hi")
#         ch.content = content
#         book.add_item(ch)
#         book.spine.append(ch)

#     # Add TOC + Styling
#     book.add_item(epub.EpubNav())
#     book.add_item(epub.EpubNcx())
#     css = 'body { font-family: "Noto Sans Devanagari", "Arial Unicode MS"; line-height: 1.6; }'
#     book.add_item(epub.EpubItem(uid="style", file_name="style.css", media_type="text/css", content=css))
    
#     print(f"💾 Writing EPUB file to {output_epub}...")
#     epub.write_epub(output_epub, book)
#     print(f"🎉 EPUB created successfully: {output_epub}")

# # ---------------------------
# # RUN
# # ---------------------------
# if __name__ == "__main__":
#     hybrid_convert(PDF_PATH, OUTPUT_EPUB)

###########################################################################
# using tesseract instead of easyocr for better Hindi support
# import os
# import re
# import subprocess
# from pdf2image import convert_from_path
# import fitz  # PyMuPDF
# import pytesseract
# from PIL import Image
# from ebooklib import epub
# from concurrent.futures import ThreadPoolExecutor

# # ---------------------------
# # CONFIG
# # ---------------------------
# PDF_PATH = "documents/ocr.pdf"
# OUTPUT_EPUB = "documents/ocr.epub"
# MAX_THREADS = 8  # Tesseract is faster, can use more threads
# CALIBRE_CMD = "ebook-convert"

# # Set Tesseract path (Windows)
# # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # ---------------------------
# # STEP 1: TEXT LAYER ANALYSIS
# # ---------------------------
# def is_page_textual(pdf_path, page_num):
#     """Detect if PDF page contains selectable text."""
#     with fitz.open(pdf_path) as doc:
#         page = doc.load_page(page_num)
#         text = page.get_text("text")
#         # If Hindi text contains dotted circles or missing glyphs, consider non-textual
#         if not text.strip():
#             return False
#         if re.search(r"[◌□�]", text):
#             return False
#         return True

# # ---------------------------
# # STEP 2: OCR PAGE FUNCTION (TESSERACT)
# # ---------------------------
# def ocr_page_tesseract(page_image, page_num):
#     """OCR a single page using Tesseract - supports PIL Image directly"""
#     try:
#         # Tesseract accepts PIL Image directly - no conversion needed!
#         # Configure for Hindi + English
#         custom_config = r'--oem 3 --psm 6'
#         text = pytesseract.image_to_string(
#             page_image, 
#             lang='hin+eng',  # Hindi + English
#             config=custom_config
#         )
        
#         # Clean up text
#         text = text.strip()
#         text = re.sub(r'\n{3,}', '\n\n', text)  # Remove excessive newlines
        
#         print(f"🔸 OCR done for page {page_num}")
#         return f"<h2>Page {page_num}</h2><p>{text}</p>"
    
#     except Exception as e:
#         print(f"❌ Error in OCR for page {page_num}: {str(e)}")
#         return f"<h2>Page {page_num}</h2><p>Error processing page: {str(e)}</p>"

# # ---------------------------
# # STEP 3: HYBRID PROCESSING
# # ---------------------------
# def hybrid_convert(pdf_path, output_epub):
#     print("🔹 Analyzing PDF pages...")
#     with fitz.open(pdf_path) as doc:
#         total_pages = len(doc)
#         text_flags = [is_page_textual(pdf_path, i) for i in range(total_pages)]
    
#     text_pages = sum(text_flags)
#     print(f"🔍 {text_pages}/{total_pages} pages are textual.")

#     # CASE 1: Mostly text → Use Calibre
#     # if text_pages / total_pages > 0.95:
#     #     print("✅ Almost all pages are textual. Using Calibre for faster conversion...")
#     #     try:
#     #         cmd = [CALIBRE_CMD, pdf_path, output_epub, "--language", "hi"]
#     #         subprocess.run(cmd, check=True)
#     #         print(f"🎉 EPUB created using Calibre: {output_epub}")
#     #         return
#     #     except Exception as e:
#     #         print(f"⚠️ Calibre failed: {e}. Falling back to OCR...")

#     # CASE 2: Mixed/Scanned → Use OCR
#     print("⚙️ Detected image-based/mixed content. Using Tesseract OCR...")

#     # Convert to images
#     print("📄 Converting PDF pages to images...")
#     pages = convert_from_path(pdf_path, dpi=300)  # Higher DPI for better accuracy
    
#     print(f"🚀 Starting OCR with Tesseract ({MAX_THREADS} threads)...")

#     # OCR with threads
#     results = []
#     with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
#         for i, page in enumerate(pages, start=1):
#             print(f"🔍 Submitting page {i} for OCR...")
#             results.append(executor.submit(ocr_page_tesseract, page, i))
           
#     # Collect OCR results
#     print("⏳ Collecting OCR results...")
#     final_pages = [r.result() if not isinstance(r, str) else r for r in results]

#     # Build EPUB
#     print("📚 Building EPUB from OCR and text mix...")
#     book = epub.EpubBook()
#     book.set_identifier("hybrid_pdf_to_epub")
#     book.set_title("Hybrid OCR eBook")
#     book.set_language("hi")

#     # Add chapters
#     for i, content in enumerate(final_pages, start=1):
#         ch = epub.EpubHtml(
#             title=f"Page {i}", 
#             file_name=f"page_{i}.xhtml", 
#             lang="hi"
#         )
#         ch.content = f'<html><body>{content}</body></html>'
#         book.add_item(ch)
#         book.spine.append(ch)

#     # Add TOC + Styling
#     book.add_item(epub.EpubNav())
#     book.add_item(epub.EpubNcx())
    
#     # Better CSS for Hindi
#     css = '''
#     body { 
#         font-family: "Noto Sans Devanagari", "Mangal", "Arial Unicode MS", sans-serif;
#         line-height: 1.8;
#         font-size: 1.1em;
#         padding: 1em;
#         text-align: justify;
#     }
#     h2 {
#         color: #333;
#         border-bottom: 2px solid #ddd;
#         padding-bottom: 0.5em;
#         margin-top: 1em;
#     }
#     p {
#         margin: 1em 0;
#     }
#     '''
    
#     book.add_item(epub.EpubItem(
#         uid="style", 
#         file_name="style.css", 
#         media_type="text/css", 
#         content=css
#     ))
    
#     print(f"💾 Writing EPUB file to {output_epub}...")
#     epub.write_epub(output_epub, book)
#     print(f"🎉 EPUB created successfully: {output_epub}")

# # ---------------------------
# # RUN
# # ---------------------------
# if __name__ == "__main__":
#     # Test Tesseract installation
#     try:
#         print("🔧 Testing Tesseract installation...")
#         version = pytesseract.get_tesseract_version()
#         print(f"✅ Tesseract version: {version}")
#     except Exception as e:
#         print(f"❌ Tesseract not found! Error: {e}")
#         print("Please install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
#         exit(1)
    
#     hybrid_convert(PDF_PATH, OUTPUT_EPUB)
################################  ye kaam kar raha hai lekin design apne hai pdf ke nahi  ########################################

# import os
# import re
# from pdf2image import convert_from_path
# import fitz  # PyMuPDF
# import pytesseract
# from PIL import Image
# from concurrent.futures import ThreadPoolExecutor
# import html
# import zipfile
# import json
# from datetime import datetime

# # ---------------------------
# # CONFIG
# # ---------------------------
# PDF_PATH = "documents/ocr.pdf"
# OUTPUT_EPUB = "documents/ocr.epub"
# MAX_THREADS = 4
# DPI = 300

# # Set Tesseract path (Windows)
# # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # ---------------------------
# # STEP 1: PDF METADATA EXTRACTION
# # ---------------------------
# def extract_pdf_metadata(pdf_path):
#     """Extract basic metadata from PDF"""
#     with fitz.open(pdf_path) as doc:
#         metadata = doc.metadata
#         toc = doc.get_toc()
#         total_pages = len(doc)
        
#         return {
#             'title': metadata.get('title', 'OCR Converted Document'),
#             'author': metadata.get('author', 'Unknown Author'),
#             'total_pages': total_pages,
#             'toc': toc
#         }

# # ---------------------------
# # STEP 2: SIMPLIFIED OCR PROCESSING
# # ---------------------------
# def ocr_page(page_image, page_num):
#     """OCR a single page using Tesseract"""
#     try:
#         # Tesseract configuration for Hindi + English
#         custom_config = r'--oem 3 --psm 6'
        
#         # Perform OCR
#         text = pytesseract.image_to_string(
#             page_image, 
#             lang='hin+eng',
#             config=custom_config
#         )
        
#         # Clean and format the text
#         html_content = format_ocr_text(text, page_num)
        
#         print(f"✅ OCR completed for page {page_num}")
#         return html_content
    
#     except Exception as e:
#         print(f"❌ OCR failed for page {page_num}: {str(e)}")
#         return format_error_page(page_num, str(e))

# def format_ocr_text(text, page_num):
#     """Format OCR text into HTML with basic structure"""
#     text = text.strip()
#     text = re.sub(r'\n{3,}', '\n\n', text)
    
#     paragraphs = text.split('\n\n')
    
#     html_content = f'''<div class="page" id="page-{page_num}">
#     <h2 class="page-header">Page {page_num}</h2>
#             '''
                
#     for para in paragraphs:
#         para = para.strip()
#         if para:
#             if len(para.split()) <= 6 and not para.endswith(('.', ',', ';')):
#                 html_content += f'    <h3 class="section-heading">{html.escape(para)}</h3>\n'
#             else:
#                 html_content += f'    <p class="paragraph">{html.escape(para)}</p>\n'
    
#     if not any(para.strip() for para in paragraphs):
#         html_content += '    <p class="empty">[No text detected on this page]</p>\n'
    
#     html_content += '</div>'
#     return html_content

# def format_error_page(page_num, error_msg):
#     """Create error page HTML"""
#     return f'''<div class="page" id="page-{page_num}">
#     <h2 class="page-header">Page {page_num}</h2>
#     <p class="error">Error processing page: {html.escape(error_msg)}</p>
#             </div>'''

# # ---------------------------
# # STEP 3: MANUAL EPUB CREATION (MORE RELIABLE)
# # ---------------------------
# def create_epub_manual(metadata, html_contents, output_path):
#     """Create EPUB manually using zipfile for better reliability"""
    
#     # Create temporary directory
#     temp_dir = "temp_epub"
#     os.makedirs(temp_dir, exist_ok=True)
#     os.makedirs(os.path.join(temp_dir, "META-INF"), exist_ok=True)
#     os.makedirs(os.path.join(temp_dir, "OEBPS"), exist_ok=True)
#     os.makedirs(os.path.join(temp_dir, "OEBPS", "Styles"), exist_ok=True)
    
#     try:
#         # 1. Create mimetype file (must be first and uncompressed)
#         with open(os.path.join(temp_dir, "mimetype"), "w", encoding="utf-8") as f:
#             f.write("application/epub+zip")
        
#         # 2. Create container.xml
#         container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
#             <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
#                 <rootfiles>
#                     <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
#                 </rootfiles>
#             </container>'''
                    
#         with open(os.path.join(temp_dir, "META-INF", "container.xml"), "w", encoding="utf-8") as f:
#             f.write(container_xml)
        
#         # 3. Create CSS
#         css_content = '''@namespace epub "http://www.idpf.org/2007/ops";

#                 body {
#                     font-family: "Noto Sans Devanagari", "Mangal", "Arial Unicode MS", "Nirmala UI", sans-serif;
#                     line-height: 1.8;
#                     font-size: 1.1em;
#                     text-align: justify;
#                     margin: 0;
#                     padding: 2em;
#                     color: #333;
#                     background-color: #fff;
#                     word-spacing: 0.1em;
#                     letter-spacing: 0.02em;
#                 }

#                 .container {
#                     max-width: 800px;
#                     margin: 0 auto;
#                 }

#                 .page {
#                     margin-bottom: 3em;
#                     page-break-inside: avoid;
#                 }

#                 .page-header {
#                     color: #2c3e50;
#                     border-bottom: 2px solid #3498db;
#                     padding-bottom: 0.5em;
#                     margin-top: 2em;
#                     margin-bottom: 1.5em;
#                     font-size: 1.4em;
#                     font-weight: 600;
#                     text-align: center;
#                 }

#                 .section-heading {
#                     color: #34495e;
#                     margin-top: 1.5em;
#                     margin-bottom: 1em;
#                     font-size: 1.2em;
#                     font-weight: 500;
#                     text-align: left;
#                     border-left: 4px solid #3498db;
#                     padding-left: 1em;
#                 }

#                 .paragraph {
#                     margin: 1em 0;
#                     text-indent: 1.5em;
#                     text-align: justify;
#                 }

#                 .error {
#                     color: #e74c3c;
#                     background-color: #fdf2f2;
#                     padding: 1em;
#                     border-radius: 4px;
#                     border-left: 4px solid #e74c3c;
#                     font-style: italic;
#                 }

#                 .empty {
#                     color: #999;
#                     font-style: italic;
#                     text-align: center;
#                     margin: 2em 0;
#                 }'''
        
#         with open(os.path.join(temp_dir, "OEBPS", "Styles", "style.css"), "w", encoding="utf-8") as f:
#             f.write(css_content)
        
#         # 4. Create XHTML files
#         manifest_items = []
#         spine_items = []
        
#         for i, content in enumerate(html_contents):
#             page_num = i + 1
#             filename = f"page_{page_num}.xhtml"
            
#             xhtml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
#             <!DOCTYPE html>
#             <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="hi">
#             <head>
#                 <title>Page {page_num}</title>
#                 <link rel="stylesheet" type="text/css" href="Styles/style.css"/>
#             </head>
#             <body>
#                 <div class="container">
#                     {content}
#                 </div>
#             </body>
#             </html>'''
            
#             with open(os.path.join(temp_dir, "OEBPS", filename), "w", encoding="utf-8") as f:
#                 f.write(xhtml_content)
            
#             manifest_items.append(f'    <item id="page_{page_num}" href="{filename}" media-type="application/xhtml+xml"/>')
#             spine_items.append(f'    <itemref idref="page_{page_num}"/>')
        
#         # 5. Create content.opf
#         current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
#         content_opf = f'''<?xml version="1.0" encoding="UTF-8"?>
#             <package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid">
#                 <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
#                     <dc:identifier id="uid">urn:uuid:{metadata['title'].replace(' ', '_')}_{current_time}</dc:identifier>
#                     <dc:title>{html.escape(metadata['title'])}</dc:title>
#                     <dc:creator>{html.escape(metadata['author'])}</dc:creator>
#                     <dc:language>hi</dc:language>
#                     <dc:date>{current_time}</dc:date>
#                     <meta property="dcterms:modified">{current_time}</meta>
#                 </metadata>
#                 <manifest>
#                     <item id="style" href="Styles/style.css" media-type="text/css"/>
#                     <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
#             {chr(10).join(manifest_items)}
#                 </manifest>
#                 <spine>
#             {chr(10).join(spine_items)}
#                 </spine>
#             </package>'''
        
#         with open(os.path.join(temp_dir, "OEBPS", "content.opf"), "w", encoding="utf-8") as f:
#             f.write(content_opf)
        
#         # 6. Create nav.xhtml
#         nav_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
#                 <!DOCTYPE html>
#                 <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="hi">
#                 <head>
#                     <title>Table of Contents</title>
#                     <link rel="stylesheet" type="text/css" href="Styles/style.css"/>
#                 </head>
#                 <body>
#                     <nav epub:type="toc">
#                         <h1>Table of Contents</h1>
#                         <ol>
#                 '''
        
#         for i in range(len(html_contents)):
#             page_num = i + 1
#             nav_xhtml += f'            <li><a href="page_{page_num}.xhtml">Page {page_num}</a></li>\n'
        
#         nav_xhtml += '''        </ol>
#                         </nav>
#                     </body>
#                     </html>'''
        
#         with open(os.path.join(temp_dir, "OEBPS", "nav.xhtml"), "w", encoding="utf-8") as f:
#             f.write(nav_xhtml)
        
#         # 7. Create EPUB zip file
#         with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as epub_zip:
#             # Add mimetype first without compression
#             epub_zip.write(os.path.join(temp_dir, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
            
#             # Add all other files
#             for root, dirs, files in os.walk(temp_dir):
#                 for file in files:
#                     if file == "mimetype":
#                         continue  # Already added
#                     file_path = os.path.join(root, file)
#                     arcname = os.path.relpath(file_path, temp_dir)
#                     epub_zip.write(file_path, arcname)
        
#         print(f"✅ EPUB created successfully: {output_path}")
        
#     finally:
#         # Cleanup temporary directory
#         import shutil
#         shutil.rmtree(temp_dir, ignore_errors=True)

# # ---------------------------
# # STEP 4: MAIN PROCESSING
# # ---------------------------
# def process_pdf_with_ocr(pdf_path, output_epub):
#     """Convert PDF to EPUB using OCR for all pages"""
#     print("📖 Starting PDF to EPUB conversion using OCR...")
    
#     # Extract metadata
#     print("🔹 Extracting PDF metadata...")
#     metadata = extract_pdf_metadata(pdf_path)
#     total_pages = metadata['total_pages']
    
#     print(f"📄 Converting {total_pages} PDF pages to images (DPI: {DPI})...")
    
#     # Convert all pages to images
#     try:
#         page_images = convert_from_path(pdf_path, dpi=DPI)
#         print(f"✅ Successfully converted {len(page_images)} pages to images")
#     except Exception as e:
#         print(f"❌ Failed to convert PDF to images: {e}")
#         return
    
#     # Process pages with OCR
#     print(f"🚀 Starting OCR processing with {MAX_THREADS} threads...")
    
#     final_contents = []
#     with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
#         futures = []
#         for i in range(len(page_images)):
#             future = executor.submit(ocr_page, page_images[i], i + 1)
#             futures.append((i, future))
        
#         for i, future in futures:
#             try:
#                 result = future.result()
#                 final_contents.append((i, result))
#                 print(f"✅ Processed page {i + 1}/{total_pages}")
#             except Exception as e:
#                 print(f"❌ Error processing page {i + 1}: {e}")
#                 final_contents.append((i, format_error_page(i + 1, str(e))))
    
#     # Sort by page number
#     final_contents.sort(key=lambda x: x[0])
#     html_contents = [content for _, content in final_contents]
    
#     # Build EPUB manually
#     print("📚 Building EPUB manually for better reliability...")
#     create_epub_manual(metadata, html_contents, output_epub)

# # ---------------------------
# # MAIN EXECUTION
# # ---------------------------
# if __name__ == "__main__":
#     # Verify dependencies
#     try:
#         print("🔧 Testing Tesseract installation...")
#         version = pytesseract.get_tesseract_version()
#         print(f"✅ Tesseract version: {version}")
#     except Exception as e:
#         print(f"❌ Tesseract not found! Error: {e}")
#         print("Please install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
#         exit(1)
    
#     try:
#         print("🔧 Testing PDF access...")
#         with fitz.open(PDF_PATH) as doc:
#             print(f"✅ PDF loaded: {len(doc)} pages")
#     except Exception as e:
#         print(f"❌ PDF loading failed: {e}")
#         exit(1)
    
#     # Ensure output directory exists
#     os.makedirs(os.path.dirname(OUTPUT_EPUB), exist_ok=True)
    
#     # Run OCR conversion
#     process_pdf_with_ocr(PDF_PATH, OUTPUT_EPUB)   
 
##################################################################
# goal preserve pdf styles- 
# conclustion - headings, paragraphs, images along with ocr text
# not truely copy style pdf to epub    
# import os
# import re
# import base64
# from io import BytesIO
# from pdf2image import convert_from_path
# import fitz  # PyMuPDF
# import pytesseract
# from PIL import Image, ImageDraw
# from concurrent.futures import ThreadPoolExecutor
# import html
# import zipfile
# import json
# from datetime import datetime
# import uuid

# # ---------------------------
# # CONFIG
# # ---------------------------
# PDF_PATH = "documents/ocr.pdf"
# OUTPUT_EPUB = "documents/ocr.epub"
# MAX_THREADS = 4
# DPI = 300
# PRESERVE_IMAGES = True
# EXTRACT_TOC = True

# # Set Tesseract path (Windows)
# # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # ---------------------------
# # STEP 1: ENHANCED PDF METADATA & STRUCTURE EXTRACTION
# # ---------------------------
# def extract_pdf_metadata_and_structure(pdf_path):
#     """Extract metadata, TOC, and document structure from PDF"""
#     try:
#         with fitz.open(pdf_path) as doc:
#             metadata = doc.metadata
#             toc = doc.get_toc()
#             total_pages = len(doc)
            
#             # Extract document structure (headings, paragraphs)
#             document_structure = []
#             for page_num in range(total_pages):
#                 page = doc[page_num]
#                 structure = extract_page_structure(page, page_num)
#                 document_structure.extend(structure)
            
#             return {
#                 'title': metadata.get('title', 'OCR Converted Document'),
#                 'author': metadata.get('author', 'Unknown Author'),
#                 'total_pages': total_pages,
#                 'toc': toc,
#                 'structure': document_structure,
#                 'metadata': metadata
#             }
#     except Exception as e:
#         print(f"❌ Error extracting PDF structure: {str(e)}")
#         return {
#             'title': 'OCR Converted Document',
#             'author': 'Unknown Author',
#             'total_pages': 0,
#             'toc': [],
#             'structure': [],
#             'metadata': {}
#         }

# def extract_page_structure(page, page_num):
#     """Extract structure (headings, paragraphs) from PDF page"""
#     structure = []
#     try:
#         # Extract text blocks with formatting information
#         blocks = page.get_text("dict")["blocks"]
        
#         for block in blocks:
#             if "lines" in block:  # Text block
#                 for line in block["lines"]:
#                     for span in line["spans"]:
#                         text = span["text"].strip()
#                         if text:
#                             structure.append({
#                                 'type': 'text',
#                                 'text': text,
#                                 'size': span["size"],
#                                 'flags': span["flags"],
#                                 'font': span["font"],
#                                 'bbox': span["bbox"],
#                                 'page': page_num
#                             })
#     except Exception as e:
#         print(f"⚠️ Could not extract structure from page {page_num}: {str(e)}")
    
#     return structure

# # ---------------------------
# # STEP 2: ENHANCED OCR WITH IMAGE PRESERVATION
# # ---------------------------
# def extract_images_from_page(pdf_page, page_num):
#     """Extract images from PDF page"""
#     images = []
#     try:
#         image_list = pdf_page.get_images(full=True)
        
#         for img_index, img in enumerate(image_list):
#             try:
#                 xref = img[0]
#                 base_image = pdf_page.parent.extract_image(xref)
#                 image_bytes = base_image["image"]
#                 image_ext = base_image["ext"]
                
#                 # Convert to PIL Image
#                 pil_image = Image.open(BytesIO(image_bytes))
                
#                 images.append({
#                     'image': pil_image,
#                     'ext': image_ext,
#                     'index': img_index,
#                     'bbox': img[1:5] if len(img) > 5 else None
#                 })
                
#             except Exception as e:
#                 print(f"⚠️ Could not extract image {img_index} from page {page_num}: {str(e)}")
#                 continue
                
#     except Exception as e:
#         print(f"⚠️ Error extracting images from page {page_num}: {str(e)}")
    
#     return images

# def ocr_page_with_images(pdf_page, page_num, preserve_images=True):
#     """OCR a single page with image preservation"""
#     try:
#         # Convert PDF page to image for OCR
#         pix = pdf_page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
#         img_data = pix.tobytes("ppm")
#         page_image = Image.open(BytesIO(img_data))
        
#         # OCR configuration for Hindi + English
#         custom_config = r'--oem 3 --psm 6'
        
#         # Perform OCR
#         text = pytesseract.image_to_string(
#             page_image, 
#             lang='hin+eng',
#             config=custom_config
#         )
        
#         # Extract images if requested
#         images_data = []
#         if preserve_images:
#             images_data = extract_images_from_page(pdf_page, page_num)
        
#         # Format HTML content with images
#         html_content = format_ocr_text_with_images(text, page_num, images_data)
        
#         print(f"✅ OCR completed for page {page_num} ({len(images_data)} images)")
#         return html_content
    
#     except Exception as e:
#         print(f"❌ OCR failed for page {page_num}: {str(e)}")
#         return format_error_page(page_num, str(e))

# def format_ocr_text_with_images(text, page_num, images_data):
#     """Format OCR text into HTML with images and better structure"""
#     text = text.strip()
#     text = re.sub(r'\n{3,}', '\n\n', text)
    
#     paragraphs = text.split('\n\n')
    
#     html_content = f'''<div class="page" id="page-{page_num}">
#     <h2 class="page-header">Page {page_num}</h2>
#     '''
    
#     # Add images at the beginning of the page
#     for img_data in images_data:
#         try:
#             # Convert image to base64 for embedding
#             buffered = BytesIO()
#             img_data['image'].save(buffered, format="PNG")
#             img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
#             html_content += f'''
#             <div class="image-container">
#                 <img src="data:image/png;base64,{img_base64}" 
#                      alt="Page {page_num} Image {img_data['index']}" 
#                      class="page-image"/>
#                 <div class="image-caption">Image {img_data['index'] + 1}</div>
#             </div>
#             '''
#         except Exception as e:
#             print(f"⚠️ Could not embed image from page {page_num}: {str(e)}")
    
#     # Add text content
#     for para in paragraphs:
#         para = para.strip()
#         if para:
#             # Detect headings based on text characteristics
#             if is_heading(para):
#                 html_content += f'    <h3 class="section-heading">{html.escape(para)}</h3>\n'
#             else:
#                 html_content += f'    <p class="paragraph">{html.escape(para)}</p>\n'
    
#     if not any(para.strip() for para in paragraphs) and not images_data:
#         html_content += '    <p class="empty">[No text or images detected on this page]</p>\n'
    
#     html_content += '</div>'
#     return html_content

# def is_heading(text):
#     """Determine if text is likely a heading"""
#     words = text.split()
#     if len(words) <= 8:
#         # Check for common heading patterns
#         if (text.isupper() or 
#             text.endswith(':') or 
#             any(word.isupper() for word in words if len(word) > 3)):
#             return True
#     return False

# def format_error_page(page_num, error_msg):
#     """Create error page HTML"""
#     return f'''<div class="page" id="page-{page_num}">
#     <h2 class="page-header">Page {page_num}</h2>
#     <p class="error">Error processing page: {html.escape(error_msg)}</p>
#     </div>'''

# # ---------------------------
# # STEP 3: ENHANCED EPUB CREATION WITH NAVIGATION
# # ---------------------------
# def create_enhanced_epub(metadata, html_contents, output_path):
#     """Create enhanced EPUB with proper navigation and styling"""
    
#     # Create temporary directory
#     temp_dir = "temp_epub"
#     os.makedirs(temp_dir, exist_ok=True)
#     os.makedirs(os.path.join(temp_dir, "META-INF"), exist_ok=True)
#     os.makedirs(os.path.join(temp_dir, "OEBPS"), exist_ok=True)
#     os.makedirs(os.path.join(temp_dir, "OEBPS", "Styles"), exist_ok=True)
    
#     try:
#         # 1. Create mimetype file (must be first and uncompressed)
#         with open(os.path.join(temp_dir, "mimetype"), "w", encoding="utf-8") as f:
#             f.write("application/epub+zip")
        
#         # 2. Create container.xml
#         container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
#                 <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
#                     <rootfiles>
#                         <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
#                     </rootfiles>
#                 </container>'''
                    
#         with open(os.path.join(temp_dir, "META-INF", "container.xml"), "w", encoding="utf-8") as f:
#             f.write(container_xml)
        
#         # 3. Create enhanced CSS
#         css_content = create_enhanced_css()
        
#         with open(os.path.join(temp_dir, "OEBPS", "Styles", "style.css"), "w", encoding="utf-8") as f:
#             f.write(css_content)
        
#         # 4. Create XHTML files with enhanced structure
#         manifest_items = []
#         spine_items = []
        
#         for i, content in enumerate(html_contents):
#             page_num = i + 1
#             filename = f"page_{page_num}.xhtml"
            
#             xhtml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
#         <!DOCTYPE html>
#         <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="hi">
#         <head>
#             <title>Page {page_num}</title>
#             <link rel="stylesheet" type="text/css" href="Styles/style.css"/>
#         </head>
#         <body>
#             <div class="container">
#                 {content}
#             </div>
#         </body>
#         </html>'''
            
#             with open(os.path.join(temp_dir, "OEBPS", filename), "w", encoding="utf-8") as f:
#                 f.write(xhtml_content)
            
#             manifest_items.append(f'    <item id="page_{page_num}" href="{filename}" media-type="application/xhtml+xml"/>')
#             spine_items.append(f'    <itemref idref="page_{page_num}"/>')
        
#         # 5. Create enhanced content.opf
#         content_opf = create_content_opf(metadata, manifest_items, spine_items)
        
#         with open(os.path.join(temp_dir, "OEBPS", "content.opf"), "w", encoding="utf-8") as f:
#             f.write(content_opf)
        
#         # 6. Create enhanced navigation with TOC
#         nav_xhtml = create_navigation_xhtml(metadata, len(html_contents))
        
#         with open(os.path.join(temp_dir, "OEBPS", "nav.xhtml"), "w", encoding="utf-8") as f:
#             f.write(nav_xhtml)
        
#         # 7. Create EPUB zip file
#         create_epub_zip(temp_dir, output_path)
        
#         print(f"✅ Enhanced EPUB created successfully: {output_path}")
        
#     except Exception as e:
#         print(f"❌ Error creating EPUB: {str(e)}")
#         raise
#     finally:
#         # Cleanup temporary directory
#         import shutil
#         shutil.rmtree(temp_dir, ignore_errors=True)

# def create_enhanced_css():
#     """Create enhanced CSS for EPUB"""
#     return '''@namespace epub "http://www.idpf.org/2007/ops";

#                 body {
#                     font-family: "Noto Sans Devanagari", "Mangal", "Arial Unicode MS", "Nirmala UI", "Segoe UI", sans-serif;
#                     line-height: 1.8;
#                     font-size: 1.1em;
#                     text-align: justify;
#                     margin: 0;
#                     padding: 2em;
#                     color: #2c3e50;
#                     background-color: #f8f9fa;
#                     word-spacing: 0.1em;
#                     letter-spacing: 0.02em;
#                     hyphens: auto;
#                 }

#                 .container {
#                     max-width: 800px;
#                     margin: 0 auto;
#                     background-color: white;
#                     padding: 3em;
#                     box-shadow: 0 0 20px rgba(0,0,0,0.1);
#                     border-radius: 8px;
#                 }

#                 .page {
#                     margin-bottom: 3em;
#                     page-break-inside: avoid;
#                 }

#                 .page-header {
#                     color: #2c3e50;
#                     border-bottom: 3px solid #3498db;
#                     padding-bottom: 0.8em;
#                     margin-top: 2em;
#                     margin-bottom: 2em;
#                     font-size: 1.6em;
#                     font-weight: 700;
#                     text-align: center;
#                     text-transform: uppercase;
#                     letter-spacing: 0.1em;
#                 }

#                 .section-heading {
#                     color: #34495e;
#                     margin-top: 2em;
#                     margin-bottom: 1.5em;
#                     font-size: 1.3em;
#                     font-weight: 600;
#                     text-align: left;
#                     border-left: 5px solid #3498db;
#                     padding-left: 1.2em;
#                     padding-top: 0.5em;
#                     padding-bottom: 0.5em;
#                     background-color: #f8f9fa;
#                     border-radius: 0 8px 8px 0;
#                 }

#                 .paragraph {
#                     margin: 1.2em 0;
#                     text-indent: 1.5em;
#                     text-align: justify;
#                     line-height: 1.8;
#                 }

#                 .image-container {
#                     text-align: center;
#                     margin: 2em 0;
#                     padding: 1em;
#                     background-color: #f8f9fa;
#                     border-radius: 8px;
#                     border: 1px solid #e9ecef;
#                 }

#                 .page-image {
#                     max-width: 100%;
#                     height: auto;
#                     border-radius: 4px;
#                     box-shadow: 0 4px 8px rgba(0,0,0,0.1);
#                 }

#                 .image-caption {
#                     font-style: italic;
#                     color: #6c757d;
#                     margin-top: 0.8em;
#                     font-size: 0.9em;
#                 }

#                 .error {
#                     color: #e74c3c;
#                     background-color: #fdf2f2;
#                     padding: 1.5em;
#                     border-radius: 8px;
#                     border-left: 5px solid #e74c3c;
#                     font-style: italic;
#                     margin: 1em 0;
#                 }

#                 .empty {
#                     color: #6c757d;
#                     font-style: italic;
#                     text-align: center;
#                     margin: 3em 0;
#                     padding: 2em;
#                     background-color: #f8f9fa;
#                     border-radius: 8px;
#                 }

#                 /* Navigation styles */
#                 .toc-container {
#                     margin: 2em 0;
#                 }

#                 .toc-level-1 {
#                     font-weight: 600;
#                     margin-top: 1em;
#                     color: #2c3e50;
#                 }

#                 .toc-level-2 {
#                     margin-left: 1.5em;
#                     font-weight: 500;
#                     color: #34495e;
#                 }

#                 .toc-level-3 {
#                     margin-left: 3em;
#                     color: #7f8c8d;
#                 }

#                 .toc-link {
#                     text-decoration: none;
#                     color: inherit;
#                     display: block;
#                     padding: 0.5em 0;
#                     border-bottom: 1px solid #ecf0f1;
#                 }

#                 .toc-link:hover {
#                     background-color: #ecf0f1;
#                     color: #3498db;
#                 }

#                 /* Responsive design */
#                 @media (max-width: 600px) {
#                     body {
#                         padding: 1em;
#                         font-size: 1em;
#                     }
                    
#                     .container {
#                         padding: 1.5em;
#                     }
                    
#                     .page-header {
#                         font-size: 1.3em;
#                     }
#                 }'''

# def create_content_opf(metadata, manifest_items, spine_items):
#     """Create enhanced content.opf file"""
#     current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
#     document_uuid = str(uuid.uuid4())
    
#     return f'''<?xml version="1.0" encoding="UTF-8"?>
#                 <package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid">
#                     <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
#                         <dc:identifier id="uid">urn:uuid:{document_uuid}</dc:identifier>
#                         <dc:title>{html.escape(metadata['title'])}</dc:title>
#                         <dc:creator>{html.escape(metadata['author'])}</dc:creator>
#                         <dc:language>hi</dc:language>
#                         <dc:date>{current_time}</dc:date>
#                         <dc:subject>OCR Converted Document</dc:subject>
#                         <dc:description>PDF converted to EPUB with OCR and image preservation</dc:description>
#                         <meta property="dcterms:modified">{current_time}</meta>
#                         <meta name="cover" content="cover-image"/>
#                     </metadata>
#                     <manifest>
#                         <item id="style" href="Styles/style.css" media-type="text/css"/>
#                         <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
#                 {chr(10).join(manifest_items)}
#                     </manifest>
#                     <spine>
#                 {chr(10).join(spine_items)}
#                     </spine>
#                 </package>'''

# def create_navigation_xhtml(metadata, total_pages):
#     """Create enhanced navigation with table of contents"""
    
#     # Build TOC from PDF structure if available
#     toc_content = ''
#     if metadata.get('toc'):
#         toc_content = '<h2>Table of Contents</h2>\n<nav epub:type="toc" id="toc">\n'
#         for item in metadata['toc']:
#             level, title, page = item
#             indent_class = f'toc-level-{level}'
#             toc_content += f'    <div class="{indent_class}">\n'
#             toc_content += f'        <a href="page_{page}.xhtml" class="toc-link">{html.escape(title)}</a>\n'
#             toc_content += '    </div>\n'
#         toc_content += '</nav>'
#     else:
#         # Fallback to page-based TOC
#         toc_content = '<h2>Table of Contents</h2>\n<nav epub:type="toc" id="toc">\n'
#         for i in range(total_pages):
#             page_num = i + 1
#             toc_content += f'    <div class="toc-level-1">\n'
#             toc_content += f'        <a href="page_{page_num}.xhtml" class="toc-link">Page {page_num}</a>\n'
#             toc_content += '    </div>\n'
#         toc_content += '</nav>'
    
#     return f'''<?xml version="1.0" encoding="UTF-8"?>
#                     <!DOCTYPE html>
#                     <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="hi">
#                     <head>
#                         <title>Table of Contents</title>
#                         <link rel="stylesheet" type="text/css" href="Styles/style.css"/>
#                     </head>
#                     <body>
#                         <div class="container">
#                             <h1 class="page-header">{html.escape(metadata['title'])}</h1>
#                             <div class="toc-container">
#                                 {toc_content}
#                             </div>
#                             <div class="document-info">
#                                 <h3>Document Information</h3>
#                                 <p><strong>Title:</strong> {html.escape(metadata['title'])}</p>
#                                 <p><strong>Author:</strong> {html.escape(metadata['author'])}</p>
#                                 <p><strong>Pages:</strong> {total_pages}</p>
#                                 <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
#                             </div>
#                         </div>
#                     </body>
#                     </html>'''

# def create_epub_zip(temp_dir, output_path):
#     """Create EPUB zip file with proper structure"""
#     with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as epub_zip:
#         # Add mimetype first without compression
#         epub_zip.write(os.path.join(temp_dir, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
        
#         # Add all other files
#         for root, dirs, files in os.walk(temp_dir):
#             for file in files:
#                 if file == "mimetype":
#                     continue  # Already added
#                 file_path = os.path.join(root, file)
#                 arcname = os.path.relpath(file_path, temp_dir)
#                 epub_zip.write(file_path, arcname)

# # ---------------------------
# # STEP 4: ENHANCED MAIN PROCESSING
# # ---------------------------
# def process_pdf_with_enhanced_ocr(pdf_path, output_epub):
#     """Convert PDF to EPUB using enhanced OCR with all features"""
#     print("📖 Starting Enhanced PDF to EPUB conversion...")
    
#     # Extract metadata and structure
#     print("🔹 Extracting PDF metadata and structure...")
#     metadata = extract_pdf_metadata_and_structure(pdf_path)
#     total_pages = metadata['total_pages']
    
#     print(f"📄 Processing {total_pages} PDF pages...")
    
#     # Open PDF document for processing
#     try:
#         pdf_document = fitz.open(pdf_path)
#     except Exception as e:
#         print(f"❌ Failed to open PDF: {e}")
#         return
    
#     # Process pages with enhanced OCR
#     print(f"🚀 Starting enhanced OCR processing with {MAX_THREADS} threads...")
    
#     final_contents = []
#     with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
#         futures = []
#         for page_num in range(total_pages):
#             pdf_page = pdf_document[page_num]
#             future = executor.submit(
#                 ocr_page_with_images, 
#                 pdf_page, 
#                 page_num + 1, 
#                 PRESERVE_IMAGES
#             )
#             futures.append((page_num, future))
        
#         for page_num, future in futures:
#             try:
#                 result = future.result(timeout=120)  # 2 minutes timeout per page
#                 final_contents.append((page_num, result))
#                 print(f"✅ Processed page {page_num + 1}/{total_pages}")
#             except Exception as e:
#                 print(f"❌ Error processing page {page_num + 1}: {e}")
#                 final_contents.append((page_num, format_error_page(page_num + 1, str(e))))
    
#     # Close PDF document
#     pdf_document.close()
    
#     # Sort by page number
#     final_contents.sort(key=lambda x: x[0])
#     html_contents = [content for _, content in final_contents]
    
#     # Build enhanced EPUB
#     print("📚 Building enhanced EPUB with navigation and images...")
#     create_enhanced_epub(metadata, html_contents, output_epub)

# # ---------------------------
# # ERROR HANDLING & VALIDATION
# # ---------------------------
# def validate_environment():
#     """Validate all required dependencies are available"""
#     errors = []
    
#     # Check Tesseract
#     try:
#         version = pytesseract.get_tesseract_version()
#         print(f"✅ Tesseract version: {version}")
#     except Exception as e:
#         errors.append(f"Tesseract not found: {e}")
    
#     # Check PyMuPDF
#     try:
#         import fitz
#         print("✅ PyMuPDF available")
#     except Exception as e:
#         errors.append(f"PyMuPDF not available: {e}")
    
#     # Check PDF access
#     try:
#         if not os.path.exists(PDF_PATH):
#             errors.append(f"PDF file not found: {PDF_PATH}")
#         else:
#             with fitz.open(PDF_PATH) as doc:
#                 print(f"✅ PDF accessible: {len(doc)} pages")
#     except Exception as e:
#         errors.append(f"PDF access failed: {e}")
    
#     # Check output directory
#     try:
#         os.makedirs(os.path.dirname(OUTPUT_EPUB), exist_ok=True)
#         print("✅ Output directory ready")
#     except Exception as e:
#         errors.append(f"Output directory creation failed: {e}")
    
#     return errors

# # ---------------------------
# # MAIN EXECUTION
# # ---------------------------
# if __name__ == "__main__":
#     print("🔧 Validating environment...")
#     environment_errors = validate_environment()
    
#     if environment_errors:
#         print("❌ Environment validation failed:")
#         for error in environment_errors:
#             print(f"   - {error}")
#         print("\nPlease fix the above issues and try again.")
#         exit(1)
    
#     print("✅ All dependencies validated successfully!")
    
#     try:
#         # Run enhanced OCR conversion
#         process_pdf_with_enhanced_ocr(PDF_PATH, OUTPUT_EPUB)
#         print(f"🎉 Conversion completed successfully! Output: {OUTPUT_EPUB}")
        
#     except KeyboardInterrupt:
#         print("\n⚠️ Conversion interrupted by user")
#         exit(1)
#     except Exception as e:
#         print(f"💥 Unexpected error during conversion: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         exit(1)
 
###############################################################
# attemp2
import os
import re
import base64
from pdf2image import convert_from_path
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import zipfile
import json
from datetime import datetime
import hashlib
from io import BytesIO
import logging

# ---------------------------
# CONFIG
# ---------------------------
PDF_PATH = "documents/ocr.pdf"
OUTPUT_EPUB = "documents/ocr.epub"
MAX_THREADS = 4
DPI = 300
EXTRACT_IMAGES = True
PRESERVE_STYLE = True

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------
# STEP 1: ENHANCED METADATA & TOC EXTRACTION
# ---------------------------
def extract_pdf_metadata(pdf_path):
    """Extract comprehensive metadata and TOC from PDF"""
    try:
        with fitz.open(pdf_path) as doc:
            metadata = doc.metadata
            toc = doc.get_toc()
            total_pages = len(doc)
            
            # Build enhanced TOC structure
            enhanced_toc = []
            for level, title, page_num in toc:
                enhanced_toc.append({
                    'level': level,
                    'title': title.strip() if title else f"Section {len(enhanced_toc) + 1}",
                    'page': page_num
                })
            
            # If no TOC exists, create basic chapter structure
            if not enhanced_toc:
                pages_per_chapter = max(10, total_pages // 10)
                for i in range(0, total_pages, pages_per_chapter):
                    enhanced_toc.append({
                        'level': 1,
                        'title': f"Chapter {i // pages_per_chapter + 1}",
                        'page': i + 1
                    })
            
            return {
                'title': metadata.get('title', 'OCR Converted Document'),
                'author': metadata.get('author', 'Unknown Author'),
                'subject': metadata.get('subject', ''),
                'keywords': metadata.get('keywords', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'total_pages': total_pages,
                'toc': enhanced_toc
            }
    except Exception as e:
        logger.error(f"Failed to extract PDF metadata: {e}")
        raise

# ---------------------------
# STEP 2: IMAGE EXTRACTION
# ---------------------------
# def extract_images_from_page(page, page_num):
#     """Extract all images from a PDF page"""
#     images = []
#     try:
#         image_list = page.get_images(full=True)
        
#         for img_index, img in enumerate(image_list):
#             try:
#                 xref = img[0]
#                 base_image = page.parent.extract_image(xref)
#                 image_bytes = base_image["image"]
#                 image_ext = base_image["ext"]
                
#                 # Generate unique image ID
#                 img_hash = hashlib.md5(image_bytes).hexdigest()
#                 img_filename = f"img_p{page_num}_{img_index}_{img_hash[:8]}.{image_ext}"
                
#                 print(f"Extracted image {img_filename} from page {page_num}")
            
#                 # Get image position on page
#                 img_rect = page.get_image_bbox(img)
                
#                 images.append({
#                     'filename': img_filename,
#                     'data': image_bytes,
#                     'ext': image_ext,
#                     'rect': img_rect,
#                     'page': page_num
#                 })
                
#             except Exception as e:
#                 logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
#                 continue
                
#     except Exception as e:
#         logger.error(f"Failed to extract images from page {page_num}: {e}")
    
#     return images

# ---------------------------
# STEP 3: STYLE EXTRACTION
# ---------------------------
# def extract_text_with_style(page, page_num):
#     """Extract text with styling information"""
#     try:
#         blocks = page.get_text("dict")["blocks"]
#         styled_content = []
        
#         for block in blocks:
#             if block.get("type") == 0:  # Text block
#                 for line in block.get("lines", []):
#                     for span in line.get("spans", []):
#                         text = span.get("text", "").strip()
#                         if text:
#                             styled_content.append({
#                                 'text': text,
#                                 'font': span.get("font", ""),
#                                 'size': span.get("size", 12),
#                                 'color': span.get("color", 0),
#                                 'flags': span.get("flags", 0),  # Bold, italic, etc.
#                                 'bbox': span.get("bbox", (0, 0, 0, 0))
#                             })
        
#         return styled_content
#     except Exception as e:
#         logger.error(f"Failed to extract styled text from page {page_num}: {e}")
#         return []

def rgb_from_int(color_int):
    """Convert integer color to RGB tuple"""
    r = (color_int >> 16) & 0xFF
    g = (color_int >> 8) & 0xFF
    b = color_int & 0xFF
    return (r, g, b)

# def format_styled_text(styled_content, images_on_page):
#     """Format styled text into HTML with proper tags"""
#     html_parts = []
#     current_paragraph = []
#     last_y = None
    
#     for item in styled_content:
#         text = html.escape(item['text'])
#         font_size = max(8, min(item['size'], 72))  # Clamp size
#         r, g, b = rgb_from_int(item['color'])
        
#         # Determine if it's a heading based on size
#         is_heading = font_size > 16
#         is_bold = item['flags'] & 2 ** 4  # Bold flag
#         is_italic = item['flags'] & 2 ** 1  # Italic flag
        
#         # Build style string
#         style_parts = [f"font-size: {font_size}pt"]
#         if r != 0 or g != 0 or b != 0:
#             style_parts.append(f"color: rgb({r}, {g}, {b})")
        
#         style_str = "; ".join(style_parts)
        
#         # Apply formatting
#         if is_bold:
#             text = f"<strong>{text}</strong>"
#         if is_italic:
#             text = f"<em>{text}</em>"
        
#         # Check for line breaks
#         curr_y = item['bbox'][1]
#         if last_y is not None and abs(curr_y - last_y) > font_size * 1.5:
#             if current_paragraph:
#                 para_text = " ".join(current_paragraph)
#                 if is_heading:
#                     html_parts.append(f'<h3 style="{style_str}">{para_text}</h3>')
#                 else:
#                     html_parts.append(f'<p style="{style_str}">{para_text}</p>')
#                 current_paragraph = []
        
#         current_paragraph.append(text)
#         last_y = curr_y
    
#     # Add remaining paragraph
#     if current_paragraph:
#         para_text = " ".join(current_paragraph)
#         html_parts.append(f'<p>{para_text}</p>')
    
#     # Insert images
#     for img in images_on_page:
#         html_parts.append(f'<div class="image-container"><img src="Images/{img["filename"]}" alt="Page image"/></div>')
    
#     return "\n".join(html_parts)

# ---------------------------
# STEP 4: HYBRID OCR + TEXT EXTRACTION
# ---------------------------
# def process_page_hybrid(page, page_image, page_num, extract_images=True):
#     """Process page using both text extraction and OCR as fallback"""
#     try:
#         # Try to extract text with style first
#         styled_content = extract_text_with_style(page, page_num)
        
#         # Extract images
#         images = []
#         if extract_images:
#             images = extract_images_from_page(page, page_num)
#             print(f"Extracted {len(images)} images from page {page_num}")
        
#         # If meaningful text found, use it
#         # total_text = "".join([item['text'] for item in styled_content])
#         # print(f"Extracted {len(total_text.strip())} characters of styled text from page {page_num}")
#         # if len(total_text.strip()) > 50:  # Threshold for meaningful text
#         #     html_content = format_styled_text(styled_content, images)
#         #     logger.info(f"✅ Extracted text with style from page {page_num}")
#         # else:
#         #     # Fall back to OCR
#         #     logger.info(f"🔍 Using OCR for page {page_num} (insufficient text)")
#         #     custom_config = r'--oem 3 --psm 6'
#         #     text = pytesseract.image_to_string(
#         #         page_image,
#         #         lang='hin+eng',
#         #         config=custom_config
#         #     )
#         #     html_content = format_ocr_text(text, images)
        
#         # Extract all text and count meaningful words
#         total_text = "".join([item['text'] for item in styled_content])

#         # Count words (not just spaces - filter out garbage)
#         words = [w for w in total_text.split() if len(w) > 1]  # Only words with 2+ chars
#         meaningful_words = [w for w in words if any(c.isalnum() for c in w)]  # Must have alphanumeric

#         print(f"Extracted {len(meaningful_words)} meaningful words from page {page_num}")

#         if len(meaningful_words) > 10:  # Threshold: 10+ meaningful words
#             html_content = format_styled_text(styled_content, images)
#             logger.info(f"✅ Extracted text with style from page {page_num}")
#         else:
#             # Fall back to OCR for garbage/unmeaningful text
#             logger.info(f"🔍 Using OCR for page {page_num} (only {len(meaningful_words)} meaningful words)")
#             custom_config = r'--oem 3 --psm 6'
#             text = pytesseract.image_to_string(
#                 page_image,
#                 lang='hin+eng',
#                 config=custom_config
#             )
#             html_content = format_ocr_text(text, images)
        
        
#         return {
#             'page_num': page_num,
#             'html': html_content,
#             'images': images,
#             'success': True
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Failed to process page {page_num}: {e}")
#         return {
#             'page_num': page_num,
#             'html': format_error_page(page_num, str(e)),
#             'images': [],
#             'success': False
#         }



######################################################################

# import langdetect
# from langdetect import detect, DetectorFactory
# DetectorFactory.seed = 0  # Consistent results



# def detect_primary_language(text_sample):
#     """Detect primary language from text sample"""
#     try:
#         if len(text_sample.strip()) < 20:
#             return "unknown"
        
#         lang = detect(text_sample)
#         logger.info(f"Detected language: {lang}")
#         return lang
#     except:
#         return "unknown"

# def is_english_dominant(styled_content):
#     """Check if content is primarily English"""
#     # Sample text from styled content
#     sample_texts = []
#     for item in styled_content[:50]:  # First 50 items for quick check
#         if item['text'].strip():
#             sample_texts.append(item['text'])
    
#     if not sample_texts:
#         return False
    
#     combined_text = " ".join(sample_texts)
    
#     # Method 1: Language detection
#     detected_lang = detect_primary_language(combined_text)
    
#     # Method 2: Character-based detection (more reliable for Hindi)
#     total_chars = len(combined_text)
#     if total_chars == 0:
#         return False
    
#     # Count Devanagari characters (Hindi)
#     devanagari_chars = sum(1 for c in combined_text if '\u0900' <= c <= '\u097F')
#     # Count English characters
#     english_chars = sum(1 for c in combined_text if c.isascii() and c.isalpha())
    
#     devanagari_ratio = devanagari_chars / total_chars
#     english_ratio = english_chars / total_chars
    
#     logger.info(f"Language analysis - Hindi: {devanagari_ratio:.2%}, English: {english_ratio:.2%}")
    
#     # Decision logic
#     if devanagari_ratio > 0.3:  # 30%+ Hindi characters
#         logger.info("📚 Hindi/Devanagari detected - Will use OCR")
#         return False
#     elif english_ratio > 0.5 or detected_lang == 'en':  # 50%+ English
#         logger.info("📚 English detected - Will try text extraction")
#         return True
#     else:
#         logger.info("📚 Other/Mixed language detected - Will use OCR")
#         return False

# def process_page_hybrid(page, page_image, page_num, extract_images=True):
#     """Process page with language-aware approach"""
#     try:
#         # Extract styled content
#         styled_content = extract_text_with_style(page, page_num)
        
#         # Extract images
#         images = []
#         if extract_images:
#             images = extract_images_from_page(page, page_num)
        
#         # Check if we have any content
#         if not styled_content or len(styled_content) == 0:
#             logger.info(f"🔍 No extractable text on page {page_num} - Using OCR")
#             return ocr_fallback(page_image, page_num, images)
        
#         # Language detection
#         is_english = is_english_dominant(styled_content)
        
#         if is_english:
#             # For English: Check meaningful words
#             total_text = "".join([item['text'] for item in styled_content])
#             words = [w for w in total_text.split() if len(w) > 1]
#             meaningful_words = [w for w in words if any(c.isalnum() for c in w)]
            
#             logger.info(f"📊 English content: {len(meaningful_words)} meaningful words")
            
#             if len(meaningful_words) > 10:
#                 html_content = format_styled_text(styled_content, images)
#                 logger.info(f"✅ Using text extraction for page {page_num}")
#             else:
#                 logger.info(f"🔍 Insufficient words - Using OCR for page {page_num}")
#                 return ocr_fallback(page_image, page_num, images)
#         else:
#             # For Hindi/Other languages: Always use OCR
#             logger.info(f"🔍 Non-English content detected - Using OCR for page {page_num}")
#             return ocr_fallback(page_image, page_num, images)
        
#         return {
#             'page_num': page_num,
#             'html': html_content,
#             'images': images,
#             'success': True
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Failed to process page {page_num}: {e}")
#         return {
#             'page_num': page_num,
#             'html': format_error_page(page_num, str(e)),
#             'images': [],
#             'success': False
#         }

# def ocr_fallback(page_image, page_num, images):
#     """OCR fallback function"""
#     try:
#         custom_config = r'--oem 3 --psm 6'
#         text = pytesseract.image_to_string(
#             page_image,
#             lang='hin+eng',
#             config=custom_config
#         )
#         html_content = format_ocr_text(text, images)
        
#         return {
#             'page_num': page_num,
#             'html': html_content,
#             'images': images,
#             'success': True
#         }
#     except Exception as e:
#         logger.error(f"❌ OCR failed for page {page_num}: {e}")
#         return {
#             'page_num': page_num,
#             'html': format_error_page(page_num, str(e)),
#             'images': [],
#             'success': False
#         }

# # Language mapping: langdetect code -> Tesseract language code
# TESSERACT_LANG_MAP = {
#     'en': 'eng',
#     'hi': 'hin',
#     'es': 'spa',
#     'fr': 'fra',
#     'de': 'deu',
#     'zh-cn': 'chi_sim',
#     'zh-tw': 'chi_tra',
#     'ja': 'jpn',
#     'ko': 'kor',
#     'ar': 'ara',
#     'ru': 'rus',
#     'pt': 'por',
#     'it': 'ita',
#     'bn': 'ben',
#     'pa': 'pan',  # Punjabi
#     'ta': 'tam',  # Tamil
#     'te': 'tel',  # Telugu
#     'mr': 'mar',  # Marathi
#     'gu': 'guj',  # Gujarati
#     'kn': 'kan',  # Kannada
#     'ml': 'mal',  # Malayalam
#     'ur': 'urd',  # Urdu
# }

# # Unicode ranges for different scripts
UNICODE_SCRIPT_RANGES = {
    'devanagari': (0x0900, 0x097F),  # Hindi, Marathi, Sanskrit
    'bengali': (0x0980, 0x09FF),
    'gurmukhi': (0x0A00, 0x0A7F),    # Punjabi
    'gujarati': (0x0A80, 0x0AFF),
    'tamil': (0x0B80, 0x0BFF),
    'telugu': (0x0C00, 0x0C7F),
    'kannada': (0x0C80, 0x0CFF),
    'malayalam': (0x0D00, 0x0D7F),
    'arabic': (0x0600, 0x06FF),
    'cyrillic': (0x0400, 0x04FF),    # Russian
    'cjk': (0x4E00, 0x9FFF),         # Chinese/Japanese
    'hangul': (0xAC00, 0xD7AF),      # Korean
}

def analyze_script_distribution(text):
    """Analyze Unicode script distribution in text"""
    script_counts = {script: 0 for script in UNICODE_SCRIPT_RANGES.keys()}
    ascii_count = 0
    total_chars = 0
    
    for char in text:
        if char.isspace():
            continue
        
        total_chars += 1
        code_point = ord(char)
        
        if char.isascii() and char.isalpha():
            ascii_count += 1
        else:
            for script, (start, end) in UNICODE_SCRIPT_RANGES.items():
                if start <= code_point <= end:
                    script_counts[script] += 1
                    break
    
    if total_chars == 0:
        return None
    
    # Calculate percentages
    script_percentages = {
        script: (count / total_chars * 100) 
        for script, count in script_counts.items() if count > 0
    }
    
    ascii_percentage = (ascii_count / total_chars * 100)
    
    return {
        'scripts': script_percentages,
        'ascii': ascii_percentage,
        'total_chars': total_chars
    }

# def detect_document_languages(styled_content):
#     """Detect primary and secondary languages with confidence"""
#     # Collect sample text
#     sample_texts = []
#     for item in styled_content[:100]:  # Sample from first 100 items
#         text = item['text'].strip()
#         if len(text) > 3:  # Skip very short fragments
#             sample_texts.append(text)
    
#     if not sample_texts:
#         return ['eng'], 'unknown'
    
#     combined_text = " ".join(sample_texts)
    
#     # Method 1: Script-based detection (most reliable)
#     script_analysis = analyze_script_distribution(combined_text)
    
#     if script_analysis is None:
#         return ['eng'], 'unknown'
    
#     logger.info(f"📊 Script analysis: {script_analysis['scripts']}")
#     logger.info(f"📊 ASCII percentage: {script_analysis['ascii']:.1f}%")
    
#     detected_languages = []
#     primary_script = None
    
#     # Determine primary script
#     if script_analysis['scripts']:
#         primary_script = max(script_analysis['scripts'], key=script_analysis['scripts'].get)
#         primary_percentage = script_analysis['scripts'][primary_script]
        
#         logger.info(f"🎯 Primary script: {primary_script} ({primary_percentage:.1f}%)")
        
#         # Map script to language
#         script_to_lang = {
#             'devanagari': 'hin',
#             'bengali': 'ben',
#             'gurmukhi': 'pan',
#             'gujarati': 'guj',
#             'tamil': 'tam',
#             'telugu': 'tel',
#             'kannada': 'kan',
#             'malayalam': 'mal',
#             'arabic': 'ara',
#             'cyrillic': 'rus',
#             'cjk': 'chi_sim',
#             'hangul': 'kor',
#         }
        
#         if primary_script in script_to_lang:
#             detected_languages.append(script_to_lang[primary_script])
    
#     # Method 2: langdetect as secondary confirmation
#     try:
#         lang_probs = detect_langs(combined_text)
#         logger.info(f"🔍 Language probabilities: {lang_probs}")
        
#         for lang_prob in lang_probs[:2]:  # Top 2 languages
#             lang_code = str(lang_prob).split(':')[0]
#             if lang_code in TESSERACT_LANG_MAP:
#                 tess_lang = TESSERACT_LANG_MAP[lang_code]
#                 if tess_lang not in detected_languages:
#                     detected_languages.append(tess_lang)
#     except Exception as e:
#         logger.warning(f"langdetect failed: {e}")
    
#     # Add English as fallback if ASCII content is significant
#     if script_analysis['ascii'] > 20 and 'eng' not in detected_languages:
#         detected_languages.append('eng')
    
#     # Default to English if nothing detected
#     if not detected_languages:
#         detected_languages = ['eng']
    
#     # Determine if we should use text extraction or OCR
#     use_extraction = (
#         script_analysis['ascii'] > 70 or  # Mostly English
#         (primary_script is None and script_analysis['ascii'] > 50)
#     )
    
#     approach = 'extraction' if use_extraction else 'ocr'
    
#     logger.info(f"✅ Detected languages for Tesseract: {'+'.join(detected_languages)}")
#     logger.info(f"📋 Recommended approach: {approach.upper()}")
    
#     return detected_languages, approach

def verify_tesseract_languages(lang_codes):
    """Verify if detected languages are available in Tesseract"""
    try:
        available_langs = pytesseract.get_languages()
        logger.info(f"Available Tesseract languages: {available_langs}")
        
        verified_langs = []
        for lang in lang_codes:
            if lang in available_langs:
                verified_langs.append(lang)
            else:
                logger.warning(f"⚠️ Language '{lang}' not available in Tesseract, skipping")
        
        # Always ensure at least English is available
        if not verified_langs and 'eng' in available_langs:
            verified_langs = ['eng']
        
        return verified_langs if verified_langs else lang_codes
    except Exception as e:
        logger.warning(f"Could not verify Tesseract languages: {e}")
        return lang_codes


# def ocr_with_languages(page_image, page_num, images, lang_codes):
#     """Perform OCR with specified language models"""
#     try:
#         # Combine language codes
#         lang_string = '+'.join(lang_codes)
        
#         # Tesseract configuration
#         custom_config = r'--oem 3 --psm 6'
        
#         logger.info(f"🔍 Running OCR on page {page_num} with languages: {lang_string}")
        
#         text = pytesseract.image_to_string(
#             page_image,
#             lang=lang_string,
#             config=custom_config
#         )
        
#         if not text.strip():
#             logger.warning(f"⚠️ OCR returned empty text for page {page_num}")
        
#         html_content = format_ocr_text(text, images)
        
#         return {
#             'page_num': page_num,
#             'html': html_content,
#             'images': images,
#             'success': True,
#             'method': f'ocr({lang_string})'
#         }
#     except Exception as e:
#         logger.error(f"❌ OCR failed for page {page_num}: {e}")
#         return {
#             'page_num': page_num,
#             'html': format_error_page(page_num, str(e)),
#             'images': [],
#             'success': False,
#             'method': 'error'
#         }



def detect_all_languages_in_content(styled_content, threshold=5.0):
    """Detect ALL languages present in content (not just dominant one)"""
    # Collect sample text
    sample_texts = []
    for item in styled_content[:100]:
        text = item['text'].strip()
        if len(text) > 3:
            sample_texts.append(text)
    
    if not sample_texts:
        return ['eng'], 'unknown'
    
    combined_text = " ".join(sample_texts)
    
    # Script-based detection
    script_analysis = analyze_script_distribution(combined_text)
    
    if script_analysis is None:
        return ['eng'], 'unknown'
    
    logger.info(f"📊 Script analysis: {script_analysis['scripts']}")
    logger.info(f"📊 ASCII percentage: {script_analysis['ascii']:.1f}%")
    
    detected_languages = set()  # Use set to avoid duplicates
    
    # Map ALL detected scripts (not just primary)
    script_to_lang = {
        'devanagari': 'hin',
        'bengali': 'ben',
        'gurmukhi': 'pan',
        'gujarati': 'guj',
        'tamil': 'tam',
        'telugu': 'tel',
        'kannada': 'kan',
        'malayalam': 'mal',
        'arabic': 'ara',
        'cyrillic': 'rus',
        'cjk': 'chi_sim',
        'hangul': 'kor',
    }
    
    # Add ALL scripts that meet threshold (default 5%)
    for script, percentage in script_analysis['scripts'].items():
        if percentage >= threshold:  # 5% threshold
            if script in script_to_lang:
                lang_code = script_to_lang[script]
                detected_languages.add(lang_code)
                logger.info(f"✅ Added {lang_code} ({script}: {percentage:.1f}%)")
    
    # langdetect for additional languages
    try:
        lang_probs = detect_langs(combined_text)
        logger.info(f"🔍 Language probabilities: {lang_probs}")
        
        for lang_prob in lang_probs:
            lang_code = str(lang_prob).split(':')[0]
            probability = float(str(lang_prob).split(':')[1])
            
            # Add if probability > 5%
            if probability > 0.05 and lang_code in TESSERACT_LANG_MAP:
                tess_lang = TESSERACT_LANG_MAP[lang_code]
                detected_languages.add(tess_lang)
                logger.info(f"✅ Added {tess_lang} from langdetect ({probability:.1%})")
    except Exception as e:
        logger.warning(f"langdetect failed: {e}")
    
    # Always include English if ANY ASCII content
    if script_analysis['ascii'] > 5:  # Even 5% ASCII warrants English
        detected_languages.add('eng')
        logger.info(f"✅ Added eng (ASCII: {script_analysis['ascii']:.1f}%)")
    
    # Default to eng+hin if nothing detected
    if not detected_languages:
        detected_languages = {'eng', 'hin'}
        logger.warning("⚠️ No languages detected, defaulting to eng+hin")
    
    # Convert to sorted list for consistency
    lang_list = sorted(list(detected_languages))
    
    # Determine approach
    use_extraction = script_analysis['ascii'] > 70
    approach = 'extraction' if use_extraction else 'ocr'
    
    logger.info(f"✅ Final language list: {'+'.join(lang_list)}")
    logger.info(f"📋 Approach: {approach.upper()}")
    
    return lang_list, approach

def prioritize_languages(lang_codes, script_analysis):
    """Prioritize languages based on content distribution"""
    # Put dominant language first for better OCR accuracy
    if not script_analysis or not script_analysis['scripts']:
        return lang_codes
    
    priorities = []
    
    # Map back to priorities
    lang_to_script = {
        'hin': 'devanagari',
        'ben': 'bengali',
        'pan': 'gurmukhi',
        'guj': 'gujarati',
        'tam': 'tamil',
        'tel': 'telugu',
        'kan': 'kannada',
        'mal': 'malayalam',
        'ara': 'arabic',
        'rus': 'cyrillic',
        'chi_sim': 'cjk',
        'kor': 'hangul',
    }
    
    # Sort by percentage (highest first)
    for lang in lang_codes:
        if lang in lang_to_script:
            script = lang_to_script[lang]
            percentage = script_analysis['scripts'].get(script, 0)
            priorities.append((lang, percentage))
        elif lang == 'eng':
            priorities.append((lang, script_analysis['ascii']))
        else:
            priorities.append((lang, 0))
    
    # Sort by percentage (descending)
    priorities.sort(key=lambda x: x[1], reverse=True)
    
    sorted_langs = [lang for lang, _ in priorities]
    logger.info(f"📊 Prioritized languages: {'+'.join(sorted_langs)}")
    
    return sorted_langs

# def ocr_with_languages(page_image, page_num, images, lang_codes):
#     """Perform OCR with multiple language models"""
#     try:
#         # Combine ALL language codes
#         lang_string = '+'.join(lang_codes)
        
#         # Enhanced Tesseract configuration
#         custom_config = r'--oem 3 --psm 6'
        
#         logger.info(f"🔍 OCR on page {page_num} with: {lang_string}")
#         logger.info(f"📚 Total languages: {len(lang_codes)}")
        
#         # Perform OCR with all languages
#         text = pytesseract.image_to_string(
#             page_image,
#             lang=lang_string,  # e.g., 'hin+eng+ben+tam'
#             config=custom_config
#         )
        
#         if not text.strip():
#             logger.warning(f"⚠️ OCR returned empty text for page {page_num}")
#         else:
#             logger.info(f"✅ OCR extracted {len(text.strip())} characters")
        
#         html_content = format_ocr_text(text, images)
        
#         return {
#             'page_num': page_num,
#             'html': html_content,
#             'images': images,
#             'success': True,
#             'method': f'ocr({lang_string})',
#             'languages': lang_codes
#         }
#     except Exception as e:
#         logger.error(f"❌ OCR failed for page {page_num}: {e}")
#         return {
#             'page_num': page_num,
#             'html': format_error_page(page_num, str(e)),
#             'images': [],
#             'success': False,
#             'method': 'error'
#         }


import re
from PIL import ImageEnhance, ImageFilter

# Mathematical symbol Unicode ranges
MATH_UNICODE_RANGES = {
    'math_operators': (0x2200, 0x22FF),      # ∀∃∈∉⊂⊃∩∪∫∑∏√∞
    'math_alphanumeric': (0x1D400, 0x1D7FF), # 𝐴𝐵𝐶 (bold, italic variants)
    'math_misc': (0x2100, 0x214F),           # ℂℕℝℤ etc.
    'arrows': (0x2190, 0x21FF),              # ←→↑↓⇒⇔
    'greek': (0x0370, 0x03FF),               # αβγδεθλμπσω
    'subscript': (0x2080, 0x209F),           # ₀₁₂₃
    'superscript': (0x2070, 0x207F),         # ⁰¹²³
}

# Common mathematical patterns
MATH_PATTERNS = [
    r'\d+[+\-×÷*/]\d+',                     # Simple arithmetic: 2+3, 5×7
    r'[a-zA-Z]\s*[=<>≤≥≠]\s*[a-zA-Z0-9]',  # Variables: x=5, a≥b
    r'\([^)]+\)',                            # Parentheses: (x+y)
    r'\[[^\]]+\]',                           # Brackets: [a,b]
    r'\{[^}]+\}',                            # Braces: {1,2,3}
    r'∫|∑|∏|√|∞|±|≈|≡|∝',                   # Math symbols
    r'[a-zA-Z][\^_][0-9a-zA-Z]+',           # Powers/subscripts: x^2, a_i
    r'\d+/\d+',                              # Fractions: 3/4
    r'sin|cos|tan|log|ln|exp|lim',          # Functions
]

def detect_mathematical_content(text, bbox_info=None):
    """Detect if text contains mathematical expressions"""
    if not text:
        return False, 0
    
    math_indicators = 0
    
    # Check Unicode ranges
    for char in text:
        code_point = ord(char)
        for range_name, (start, end) in MATH_UNICODE_RANGES.items():
            if start <= code_point <= end:
                math_indicators += 1
                break
    
    # Check patterns
    for pattern in MATH_PATTERNS:
        if re.search(pattern, text):
            math_indicators += 2  # Patterns weighted more
    
    # Calculate math density
    math_density = (math_indicators / len(text)) * 100 if len(text) > 0 else 0
    
    is_math = math_density > 15 or math_indicators > 3
    
    return is_math, math_density

def analyze_page_for_math(styled_content):
    """Analyze entire page for mathematical content"""
    total_items = len(styled_content)
    math_items = 0
    math_density_sum = 0
    
    for item in styled_content:
        is_math, density = detect_mathematical_content(item['text'])
        if is_math:
            math_items += 1
            math_density_sum += density
    
    if total_items == 0:
        return False, 0
    
    math_percentage = (math_items / total_items) * 100
    avg_math_density = math_density_sum / total_items if total_items > 0 else 0
    
    logger.info(f"📐 Math analysis: {math_items}/{total_items} items ({math_percentage:.1f}%)")
    logger.info(f"📐 Average math density: {avg_math_density:.1f}%")
    
    # Page is mathematical if >20% items contain math or high density
    is_math_heavy = math_percentage > 20 or avg_math_density > 10
    
    return is_math_heavy, math_percentage

def preprocess_image_for_math(page_image):
    """Enhanced preprocessing for mathematical equations"""
    try:
        # Convert to grayscale if needed
        if page_image.mode != 'L':
            page_image = page_image.convert('L')
        
        # Increase contrast for better symbol recognition
        enhancer = ImageEnhance.Contrast(page_image)
        page_image = enhancer.enhance(2.0)
        
        # Sharpen image
        page_image = page_image.filter(ImageFilter.SHARPEN)
        
        # Increase brightness slightly
        enhancer = ImageEnhance.Brightness(page_image)
        page_image = enhancer.enhance(1.1)
        
        return page_image
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}")
        return page_image

def ocr_mathematical_content(page_image, page_num, images, lang_codes):
    """Specialized OCR for mathematical content"""
    try:
        # Preprocess image
        processed_image = preprocess_image_for_math(page_image)
        
        # Add 'equ' (equation detection) to Tesseract if available
        math_langs = lang_codes.copy()
        
        # Tesseract config for mathematical content
        # PSM 6: Uniform block of text (good for equations)
        # PSM 11: Sparse text (alternative for scattered equations)
        custom_configs = [
            r'--oem 3 --psm 6',   # Standard
            r'--oem 3 --psm 11',  # Sparse text
            r'--oem 3 --psm 3',   # Fully automatic
        ]
        
        best_text = ""
        best_length = 0
        
        # Try multiple PSM modes for better equation detection
        for config in custom_configs:
            try:
                lang_string = '+'.join(math_langs)
                text = pytesseract.image_to_string(
                    processed_image,
                    lang=lang_string,
                    config=config
                )
                
                # Keep the result with most content
                if len(text.strip()) > best_length:
                    best_text = text
                    best_length = len(text.strip())
                    
            except Exception as e:
                logger.warning(f"OCR with config '{config}' failed: {e}")
                continue
        
        if not best_text.strip():
            logger.warning(f"⚠️ All OCR attempts returned empty for page {page_num}")
            best_text = "[Mathematical content - OCR unable to extract]"
        
        logger.info(f"✅ Math OCR extracted {len(best_text.strip())} characters")
        
        # Format with special math styling
        html_content = format_mathematical_content(best_text, images)
        
        return {
            'page_num': page_num,
            'html': html_content,
            'images': images,
            'success': True,
            'method': f'math_ocr({"+".join(math_langs)})',
            'languages': math_langs
        }
        
    except Exception as e:
        logger.error(f"❌ Mathematical OCR failed for page {page_num}: {e}")
        return {
            'page_num': page_num,
            'html': format_error_page(page_num, str(e)),
            'images': [],
            'success': False,
            'method': 'error'
        }

# def format_mathematical_content(text, images):
#     """Format mathematical content with special styling"""
#     # Clean text
#     text = text.strip()
#     text = re.sub(r'\n{3,}', '\n\n', text)
    
#     paragraphs = text.split('\n\n')
#     html_parts = []
    
#     for para in paragraphs:
#         para = para.strip()
#         if not para:
#             continue
        
#         # Detect if paragraph is equation
#         is_math, density = detect_mathematical_content(para)
        
#         if is_math or density > 30:
#             # Mathematical equation styling
#             # Preserve spacing and use monospace font
#             para_escaped = html.escape(para)
#             para_escaped = para_escaped.replace(' ', '&nbsp;')
#             para_escaped = para_escaped.replace('\n', '<br/>')
#             html_parts.append(f'<div class="math-equation">{para_escaped}</div>')
#         else:
#             # Regular text
#             if len(para.split()) <= 6 and not para.endswith(('.', ',', ';')):
#                 html_parts.append(f'<h3 class="section-heading">{html.escape(para)}</h3>')
#             else:
#                 html_parts.append(f'<p class="paragraph">{html.escape(para)}</p>')
    
#     if not html_parts:
#         html_parts.append('<p class="empty">[No content detected]</p>')
    
#     # Add images
#     for img in images:
#         html_parts.append(f'<div class="image-container math-image"><img src="Images/{img["filename"]}" alt="Mathematical diagram"/></div>')
    
#     return "\n".join(html_parts)

def extract_equation_images(page, page_num):
    """Extract regions that likely contain equations as images"""
    try:
        # Get page as high-res image
        mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # This is a placeholder - in production, you'd use:
        # - Layout analysis to find equation regions
        # - Crop those regions
        # - Save as separate images
        
        return []  # Return list of equation image objects
    except Exception as e:
        logger.warning(f"Failed to extract equation images from page {page_num}: {e}")
        return []

# def process_page_hybrid(page, page_image, page_num, extract_images=True):
#     """Enhanced page processing with mathematical content handling"""
#     try:
#         # Extract styled content
#         styled_content = extract_text_with_style(page, page_num)
        
#         # Extract images
#         images = []
#         if extract_images:
#             images = extract_images_from_page(page, page_num)
        
#         # Check for mathematical content
#         is_math_heavy, math_percentage = analyze_page_for_math(styled_content)
        
#         if is_math_heavy:
#             logger.info(f"📐 Page {page_num} contains significant mathematical content ({math_percentage:.1f}%)")
#             logger.info(f"🔬 Using specialized math OCR processing")
            
#             # Detect languages (including math symbols)
#             detected_langs, _ = detect_all_languages_in_content(styled_content, threshold=5.0)
#             verified_langs = verify_tesseract_languages(detected_langs)
            
#             # Use specialized math OCR
#             return ocr_mathematical_content(page_image, page_num, images, verified_langs)
        
#         # Regular processing for non-mathematical pages
#         if not styled_content or len(styled_content) == 0:
#             logger.info(f"🔍 No extractable text on page {page_num} - Using OCR")
#             detected_langs = ['eng', 'hin']
#             return ocr_with_languages(page_image, page_num, images, detected_langs)
        
#         # Detect ALL languages
#         detected_langs, approach = detect_all_languages_in_content(styled_content, threshold=5.0)
        
#         # Get script analysis for prioritization
#         sample_texts = [item['text'] for item in styled_content[:100] if item['text'].strip()]
#         combined_text = " ".join(sample_texts)
#         script_analysis = analyze_script_distribution(combined_text)
        
#         # Prioritize languages
#         prioritized_langs = prioritize_languages(detected_langs, script_analysis)
#         verified_langs = verify_tesseract_languages(prioritized_langs)
        
#         if approach == 'extraction':
#             total_text = "".join([item['text'] for item in styled_content])
#             words = [w for w in total_text.split() if len(w) > 1]
#             meaningful_words = [w for w in words if any(c.isalnum() for c in w)]
            
#             if len(meaningful_words) > 10:
#                 html_content = format_styled_text(styled_content, images)
#                 logger.info(f"✅ Using text extraction for page {page_num}")
                
#                 return {
#                     'page_num': page_num,
#                     'html': html_content,
#                     'images': images,
#                     'success': True,
#                     'method': 'extraction',
#                     'languages': verified_langs
#                 }
        
#         # Standard OCR
#         logger.info(f"🔍 Using standard OCR: {'+'.join(verified_langs)}")
#         return ocr_with_languages(page_image, page_num, images, verified_langs)
        
#     except Exception as e:
#         logger.error(f"❌ Failed to process page {page_num}: {e}")
#         return {
#             'page_num': page_num,
#             'html': format_error_page(page_num, str(e)),
#             'images': [],
#             'success': False,
#             'method': 'error'
#         }


######################################################################
################################################################

def format_styled_text(styled_content, images_on_page):
    """Format styled text into HTML with proper tags and images"""
    html_parts = []
    current_paragraph = []
    last_y = None
    
    for item in styled_content:
        text = html.escape(item['text'])
        font_size = max(8, min(item['size'], 72))  # Clamp size
        r, g, b = rgb_from_int(item['color'])
        
        # Determine if it's a heading based on size
        is_heading = font_size > 16
        is_bold = item['flags'] & 2 ** 4  # Bold flag
        is_italic = item['flags'] & 2 ** 1  # Italic flag
        
        # Build style string
        style_parts = [f"font-size: {font_size}pt"]
        if r != 0 or g != 0 or b != 0:
            style_parts.append(f"color: rgb({r}, {g}, {b})")
        
        style_str = "; ".join(style_parts)
        
        # Apply formatting
        if is_bold:
            text = f"<strong>{text}</strong>"
        if is_italic:
            text = f"<em>{text}</em>"
        
        # Check for line breaks
        curr_y = item['bbox'][1]
        if last_y is not None and abs(curr_y - last_y) > font_size * 1.5:
            if current_paragraph:
                para_text = " ".join(current_paragraph)
                if is_heading:
                    html_parts.append(f'<h3 style="{style_str}">{para_text}</h3>')
                else:
                    html_parts.append(f'<p style="{style_str}">{para_text}</p>')
                current_paragraph = []
        
        current_paragraph.append(text)
        last_y = curr_y
    
    # Add remaining paragraph
    if current_paragraph:
        para_text = " ".join(current_paragraph)
        html_parts.append(f'<p>{para_text}</p>')
    
    # Insert images at the end (FIXED: Correct path)
    for img in images_on_page:
        html_parts.append(f'''<div class="image-container">
                <img src="../Images/{img["filename"]}" alt="Page image"/>
            </div>''')
    
    return "\n".join(html_parts)

def format_ocr_text(text, images):
    """Format OCR text into HTML with images"""
    text = text.strip()
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    paragraphs = text.split('\n\n')
    html_parts = []
    
    for para in paragraphs:
        para = para.strip()
        if para:
            if len(para.split()) <= 6 and not para.endswith(('.', ',', ';')):
                html_parts.append(f'<h3 class="section-heading">{html.escape(para)}</h3>')
            else:
                html_parts.append(f'<p class="paragraph">{html.escape(para)}</p>')
    
    if not any(para.strip() for para in paragraphs):
        html_parts.append('<p class="empty">[No text detected on this page]</p>')
    
    # Add images with CORRECT relative path
    for img in images:
        html_parts.append(f'''<div class="image-container">
                <img src="../Images/{img["filename"]}" alt="Page image"/>
            </div>''')
    
    return "\n".join(html_parts)

def format_mathematical_content(text, images):
    """Format mathematical content with special styling and images"""
    text = text.strip()
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    paragraphs = text.split('\n\n')
    html_parts = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Detect if paragraph is equation
        is_math, density = detect_mathematical_content(para)
        
        if is_math or density > 30:
            # Mathematical equation styling
            para_escaped = html.escape(para)
            para_escaped = para_escaped.replace(' ', '&nbsp;')
            para_escaped = para_escaped.replace('\n', '<br/>')
            html_parts.append(f'<div class="math-equation">{para_escaped}</div>')
        else:
            # Regular text
            if len(para.split()) <= 6 and not para.endswith(('.', ',', ';')):
                html_parts.append(f'<h3 class="section-heading">{html.escape(para)}</h3>')
            else:
                html_parts.append(f'<p class="paragraph">{html.escape(para)}</p>')
    
    if not html_parts:
        html_parts.append('<p class="empty">[No content detected]</p>')
    
    # Add images with CORRECT path
    for img in images:
        html_parts.append(f'''<div class="image-container math-image">
                <img src="../Images/{img["filename"]}" alt="Mathematical diagram"/>
            </div>''')
    
    return "\n".join(html_parts)

def create_epub_enhanced(metadata, page_data, output_path):
    """Create EPUB with proper image references"""
    temp_dir = "temp_epub"
    
    try:
        # Setup directory structure
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "META-INF"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "OEBPS"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "OEBPS", "Styles"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "OEBPS", "Images"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "OEBPS", "Text"), exist_ok=True)
        
        # 1. Create mimetype
        with open(os.path.join(temp_dir, "mimetype"), "w", encoding="utf-8") as f:
            f.write("application/epub+zip")
        
        # 2. Create container.xml
        container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
                <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
                    <rootfiles>
                        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
                    </rootfiles>
                </container>'''
        
        with open(os.path.join(temp_dir, "META-INF", "container.xml"), "w", encoding="utf-8") as f:
            f.write(container_xml)
        
        # 3. Enhanced CSS with better image styling
        css_content = '''@namespace epub "http://www.idpf.org/2007/ops";

                        body {
                            font-family: "Noto Sans Devanagari", "Mangal", "Arial Unicode MS", "Nirmala UI", sans-serif;
                            line-height: 1.8;
                            font-size: 1em;
                            margin: 0;
                            padding: 2em;
                            color: #333;
                            background-color: #fff;
                        }

                        .container {
                            max-width: 800px;
                            margin: 0 auto;
                        }

                        .page {
                            margin-bottom: 3em;
                            page-break-after: always;
                        }

                        .page-header {
                            color: #2c3e50;
                            border-bottom: 2px solid #3498db;
                            padding-bottom: 0.5em;
                            margin-top: 2em;
                            margin-bottom: 1.5em;
                            font-size: 1.4em;
                            font-weight: 600;
                            text-align: center;
                        }

                        h1, h2, h3 {
                            color: #34495e;
                            margin-top: 1.5em;
                            margin-bottom: 1em;
                            font-weight: 500;
                        }

                        h1 { font-size: 2em; }
                        h2 { font-size: 1.5em; }
                        h3 { font-size: 1.2em; }

                        .section-heading {
                            color: #34495e;
                            margin-top: 1.5em;
                            margin-bottom: 1em;
                            font-size: 1.2em;
                            font-weight: 500;
                            border-left: 4px solid #3498db;
                            padding-left: 1em;
                        }

                        p {
                            margin: 1em 0;
                            text-align: justify;
                        }

                        .paragraph {
                            text-indent: 1.5em;
                        }

                        /* Image container - CRITICAL for display */
                        .image-container {
                            text-align: center;
                            margin: 2em auto;
                            padding: 1em;
                            page-break-inside: avoid;
                            clear: both;
                            display: block;
                            width: 100%;
                        }

                        .image-container img {
                            max-width: 100%;
                            max-height: 90vh;
                            height: auto;
                            width: auto;
                            display: block;
                            margin: 0 auto;
                            border: 1px solid #ddd;
                            border-radius: 4px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            background-color: #fff;
                        }

                        /* Mathematical content */
                        .math-equation {
                            font-family: "Courier New", "Consolas", "DejaVu Sans Mono", monospace;
                            background-color: #f8f9fa;
                            border-left: 4px solid #007bff;
                            padding: 1em 1.5em;
                            margin: 1.5em 0;
                            overflow-x: auto;
                            font-size: 1.1em;
                            line-height: 1.6;
                            white-space: pre-wrap;
                            word-wrap: break-word;
                        }

                        .math-image {
                            background-color: #f8f9fa;
                            padding: 1.5em;
                            border-radius: 8px;
                        }

                        .error-container {
                            background-color: #fdf2f2;
                            padding: 1.5em;
                            border-radius: 4px;
                            border-left: 4px solid #e74c3c;
                            margin: 1em 0;
                        }

                        .error {
                            color: #e74c3c;
                            font-style: italic;
                        }

                        .empty {
                            color: #999;
                            font-style: italic;
                            text-align: center;
                            margin: 2em 0;
                        }

                        /* TOC Styling */
                        nav[epub|type~="toc"] {
                            page-break-before: always;
                        }

                        nav[epub|type~="toc"] > ol {
                            list-style-type: none;
                            padding-left: 0;
                        }

                        nav[epub|type~="toc"] > ol > li {
                            margin: 0.5em 0;
                            padding: 0.5em;
                            border-bottom: 1px solid #eee;
                        }

                        nav[epub|type~="toc"] a {
                            text-decoration: none;
                            color: #3498db;
                            display: block;
                        }

                        nav[epub|type~="toc"] a:hover {
                            color: #2980b9;
                            text-decoration: underline;
                        }

                        nav[epub|type~="toc"] ol ol {
                            list-style-type: none;
                            padding-left: 2em;
                        }'''
        
        with open(os.path.join(temp_dir, "OEBPS", "Styles", "style.css"), "w", encoding="utf-8") as f:
            f.write(css_content)
        
        # 4. Save all images and track them
        all_images = {}
        images_saved = 0
        
        for data in page_data:
            for img in data['images']:
                try:
                    img_path = os.path.join(temp_dir, "OEBPS", "Images", img['filename'])
                    with open(img_path, "wb") as f:
                        f.write(img['data'])
                    all_images[img['filename']] = img['ext']
                    images_saved += 1
                    logger.info(f"💾 Saved image: {img['filename']}")
                except Exception as e:
                    logger.error(f"Failed to save image {img['filename']}: {e}")
        
        logger.info(f"✅ Total images saved: {images_saved}")
        
        # 5. Create XHTML files for each page
        manifest_items = ['    <item id="style" href="Styles/style.css" media-type="text/css"/>']
        spine_items = []
        
        for data in page_data:
            page_num = data['page_num']
            filename = f"page_{page_num}.xhtml"
            
            # Count images on this page
            img_count = len(data.get('images', []))
            logger.info(f"📄 Page {page_num}: {img_count} images")
            
            xhtml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
                        <!DOCTYPE html>
                        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="hi">
                        <head>
                            <title>Page {page_num}</title>
                            <link rel="stylesheet" type="text/css" href="../Styles/style.css"/>
                            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                        </head>
                        <body>
                            <div class="container">
                                <div class="page" id="page-{page_num}">
                                    <h2 class="page-header">पृष्ठ {page_num} / Page {page_num}</h2>
                                    {data['html']}
                                </div>
                            </div>
                        </body>
                        </html>'''
            
            with open(os.path.join(temp_dir, "OEBPS", "Text", filename), "w", encoding="utf-8") as f:
                f.write(xhtml_content)
            
            manifest_items.append(f'    <item id="page_{page_num}" href="Text/{filename}" media-type="application/xhtml+xml"/>')
            spine_items.append(f'    <itemref idref="page_{page_num}"/>')
        
        # 6. Add ALL images to manifest with correct media types
        for img_filename, img_ext in all_images.items():
            # Determine correct media type
            media_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'bmp': 'image/bmp',
                'webp': 'image/webp',
                'svg': 'image/svg+xml',
            }
            
            media_type = media_type_map.get(img_ext.lower(), 'image/jpeg')
            img_id = img_filename.replace(".", "_").replace("-", "_")
            
            manifest_items.append(f'    <item id="{img_id}" href="Images/{img_filename}" media-type="{media_type}"/>')
            logger.info(f"📋 Added to manifest: {img_filename} ({media_type})")
        
        # 7. Create navigation document
        nav_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE html>
                <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="hi">
                <head>
                    <title>Table of Contents</title>
                    <link rel="stylesheet" type="text/css" href="Styles/style.css"/>
                </head>
                <body>
                    <nav epub:type="toc" id="toc">
                        <h1>विषय सूची / Table of Contents</h1>
                        <ol>
                '''
        
        # Build hierarchical TOC
        for item in metadata['toc']:
            indent = "    " * item['level']
            page_num = item['page']
            title = html.escape(item['title'])
            nav_xhtml += f'{indent}<li><a href="Text/page_{page_num}.xhtml">{title}</a></li>\n'
        
        nav_xhtml += '''        </ol>
                            </nav>
                            
                            <nav epub:type="page-list">
                                <h2>पृष्ठ सूची / Page List</h2>
                                <ol>
                        '''
                                
        for data in page_data:
            page_num = data['page_num']
            nav_xhtml += f'            <li><a href="Text/page_{page_num}.xhtml">Page {page_num}</a></li>\n'
        
        nav_xhtml += '''        </ol>
                    </nav>
                </body>
                </html>'''
        
        with open(os.path.join(temp_dir, "OEBPS", "nav.xhtml"), "w", encoding="utf-8") as f:
            f.write(nav_xhtml)
        
        manifest_items.insert(0, '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
        
        # 8. Create content.opf
        current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        content_opf = f'''<?xml version="1.0" encoding="UTF-8"?>
                    <package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid">
                        <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                            <dc:identifier id="uid">urn:uuid:{hashlib.md5(metadata['title'].encode()).hexdigest()}</dc:identifier>
                            <dc:title>{html.escape(metadata['title'])}</dc:title>
                            <dc:creator>{html.escape(metadata['author'])}</dc:creator>
                            <dc:language>hi</dc:language>
                            <dc:language>en</dc:language>
                            <dc:date>{current_time}</dc:date>
                            <dc:subject>{html.escape(metadata.get('subject', ''))}</dc:subject>
                            <dc:description>Enhanced EPUB with images, preserved styling, and navigation</dc:description>
                            <meta property="dcterms:modified">{current_time}</meta>
                        </metadata>
                        <manifest>
                    {chr(10).join(manifest_items)}
                        </manifest>
                        <spine>
                    {chr(10).join(spine_items)}
                        </spine>
                    </package>'''
                            
        with open(os.path.join(temp_dir, "OEBPS", "content.opf"), "w", encoding="utf-8") as f:
            f.write(content_opf)
        
        # 9. Create EPUB zip file with proper compression
        logger.info("📦 Creating EPUB archive...")
        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as epub_zip:
            # Add mimetype first without compression (EPUB requirement)
            epub_zip.write(
                os.path.join(temp_dir, "mimetype"), 
                "mimetype", 
                compress_type=zipfile.ZIP_STORED
            )
            
            # Add all other files with compression
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == "mimetype":
                        continue
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    epub_zip.write(file_path, arcname, compress_type=zipfile.ZIP_DEFLATED)
        
        logger.info(f"✅ EPUB created successfully: {output_path}")
        logger.info(f"📊 Total images embedded: {len(all_images)}")
        
    except Exception as e:
        logger.error(f"Failed to create EPUB: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Cleanup
        import shutil
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info("🧹 Cleaned up temporary files")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")


####################################################################
###################################################################
# avoid text extraction from image in page 
def get_image_regions(page):
    """Get bounding boxes of all images on the page"""
    image_regions = []
    try:
        image_list = page.get_images(full=True)
        
        for img in image_list:
            try:
                xref = img[0]
                # Get image bounding box
                img_rect = page.get_image_bbox(img)
                if img_rect:
                    image_regions.append(img_rect)
            except Exception as e:
                logger.warning(f"Could not get bbox for image: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Failed to get image regions: {e}")
    
    return image_regions

def is_text_in_image_region(text_bbox, image_regions, overlap_threshold=0.5):
    """Check if text bbox overlaps significantly with any image region"""
    if not image_regions:
        return False
    
    text_x0, text_y0, text_x1, text_y1 = text_bbox
    text_area = (text_x1 - text_x0) * (text_y1 - text_y0)
    
    if text_area <= 0:
        return False
    
    for img_rect in image_regions:
        img_x0, img_y0, img_x1, img_y1 = img_rect
        
        # Calculate intersection
        intersect_x0 = max(text_x0, img_x0)
        intersect_y0 = max(text_y0, img_y0)
        intersect_x1 = min(text_x1, img_x1)
        intersect_y1 = min(text_y1, img_y1)
        
        # Check if there's actual overlap
        if intersect_x1 > intersect_x0 and intersect_y1 > intersect_y0:
            intersect_area = (intersect_x1 - intersect_x0) * (intersect_y1 - intersect_y0)
            overlap_ratio = intersect_area / text_area
            
            # If overlap is significant, text is likely from image OCR
            if overlap_ratio > overlap_threshold:
                return True
    
    return False

def extract_text_with_style(page, page_num):
    """Extract text with styling information, excluding image regions"""
    try:
        # Get image regions first
        image_regions = get_image_regions(page)
        logger.info(f"📍 Found {len(image_regions)} image regions on page {page_num}")
        
        blocks = page.get_text("dict")["blocks"]
        styled_content = []
        excluded_count = 0
        
        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        bbox = span.get("bbox", (0, 0, 0, 0))
                        
                        if not text:
                            continue
                        
                        # Check if this text is inside an image region
                        if is_text_in_image_region(bbox, image_regions):
                            excluded_count += 1
                            logger.debug(f"Excluded text from image region: '{text[:30]}...'")
                            continue
                        
                        # Keep only genuine text outside images
                        styled_content.append({
                            'text': text,
                            'font': span.get("font", ""),
                            'size': span.get("size", 12),
                            'color': span.get("color", 0),
                            'flags': span.get("flags", 0),
                            'bbox': bbox
                        })
        
        if excluded_count > 0:
            logger.info(f"🚫 Excluded {excluded_count} text items from image regions")
        
        return styled_content
        
    except Exception as e:
        logger.error(f"Failed to extract styled text from page {page_num}: {e}")
        return []

def filter_image_text_from_ocr(ocr_text, image_regions, page_height):
    """Filter out text that likely came from images in OCR result"""
    if not image_regions or not ocr_text:
        return ocr_text
    
    # This is a simple heuristic - in production you'd need more sophisticated filtering
    # For now, we'll just return the text as-is since OCR processes the whole page image
    # The key is to use extract_text_with_style when possible to avoid this issue
    
    return ocr_text

def extract_images_from_page(page, page_num):
    """Extract all images from a PDF page with position info"""
    images = []
    try:
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Generate unique image ID
                img_hash = hashlib.md5(image_bytes).hexdigest()
                img_filename = f"img_p{page_num}_{img_index}_{img_hash[:8]}.{image_ext}"
                
                # Get image position and size
                img_rect = page.get_image_bbox(img)
                
                # Calculate image size on page
                if img_rect:
                    img_width = img_rect[2] - img_rect[0]
                    img_height = img_rect[3] - img_rect[1]
                else:
                    img_width, img_height = 0, 0
                
                # Only include images that are substantial (not tiny decorative elements)
                min_size = 20  # Minimum 20x20 points
                if img_width < min_size or img_height < min_size:
                    logger.debug(f"Skipping small image: {img_width}x{img_height}")
                    continue
                
                images.append({
                    'filename': img_filename,
                    'data': image_bytes,
                    'ext': image_ext,
                    'rect': img_rect,
                    'page': page_num,
                    'width': img_width,
                    'height': img_height,
                    'size': len(image_bytes)
                })
                
                logger.info(f"📷 Extracted image {img_index}: {img_width:.0f}x{img_height:.0f}pt, {len(image_bytes)/1024:.1f}KB")
                
            except Exception as e:
                logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Failed to extract images from page {page_num}: {e}")
    
    return images

def sort_content_by_position(styled_content, images):
    """Sort text and images by their vertical position on page"""
    # Combine text and image items with position info
    all_items = []
    
    # Add text items
    for item in styled_content:
        y_pos = item['bbox'][1]  # Top Y coordinate
        all_items.append({
            'type': 'text',
            'data': item,
            'y_pos': y_pos
        })
    
    # Add image items
    for img in images:
        if img['rect']:
            y_pos = img['rect'][1]  # Top Y coordinate
            all_items.append({
                'type': 'image',
                'data': img,
                'y_pos': y_pos
            })
    
    # Sort by vertical position (top to bottom)
    all_items.sort(key=lambda x: x['y_pos'])
    
    return all_items

def format_styled_text_with_images(styled_content, images):
    """Format styled text and images in correct reading order"""
    # Sort all content by position
    sorted_items = sort_content_by_position(styled_content, images)
    
    html_parts = []
    current_paragraph = []
    last_y = None
    last_type = None
    
    for item in sorted_items:
        if item['type'] == 'image':
            # Flush current paragraph before image
            if current_paragraph:
                para_text = " ".join(current_paragraph)
                html_parts.append(f'<p>{para_text}</p>')
                current_paragraph = []
                last_y = None
            
            # Add image
            img_data = item['data']
            html_parts.append(f'''<div class="image-container">
                        <img src="../Images/{img_data['filename']}" alt="Page image" style="max-width:100%; height:auto;"/>
                        <p class="image-caption">Image {img_data['page']}-{len([i for i in html_parts if 'image-container' in i]) + 1} ({img_data['width']:.0f}×{img_data['height']:.0f}pt)</p>
                    </div>''')
            last_type = 'image'
            
        elif item['type'] == 'text':
            text_item = item['data']
            text = html.escape(text_item['text'])
            font_size = max(8, min(text_item['size'], 72))
            r, g, b = rgb_from_int(text_item['color'])
            
            # Determine formatting
            is_heading = font_size > 16
            is_bold = text_item['flags'] & 2 ** 4
            is_italic = text_item['flags'] & 2 ** 1
            
            # Build style
            style_parts = [f"font-size: {font_size}pt"]
            if r != 0 or g != 0 or b != 0:
                style_parts.append(f"color: rgb({r}, {g}, {b})")
            style_str = "; ".join(style_parts)
            
            # Apply formatting
            if is_bold:
                text = f"<strong>{text}</strong>"
            if is_italic:
                text = f"<em>{text}</em>"
            
            # Check for paragraph breaks
            curr_y = text_item['bbox'][1]
            
            # New paragraph if: large vertical gap OR after image OR heading
            if (last_y is not None and abs(curr_y - last_y) > font_size * 1.5) or \
               last_type == 'image' or is_heading:
                
                if current_paragraph:
                    para_text = " ".join(current_paragraph)
                    if is_heading and len(current_paragraph) == 1:
                        html_parts.append(f'<h3 style="{style_str}">{para_text}</h3>')
                    else:
                        html_parts.append(f'<p style="{style_str}">{para_text}</p>')
                    current_paragraph = []
                
                if is_heading:
                    html_parts.append(f'<h3 style="{style_str}">{text}</h3>')
                    last_y = curr_y
                    last_type = 'heading'
                    continue
            
            current_paragraph.append(text)
            last_y = curr_y
            last_type = 'text'
    
    # Add remaining paragraph
    if current_paragraph:
        para_text = " ".join(current_paragraph)
        html_parts.append(f'<p>{para_text}</p>')
    
    return "\n".join(html_parts)

# def process_page_hybrid(page, page_image, page_num, extract_images=True):
#     """Enhanced page processing that separates images from text"""
#     try:
#         # Extract images FIRST to know their positions
#         images = []
#         if extract_images:
#             images = extract_images_from_page(page, page_num)
#             logger.info(f"📷 Extracted {len(images)} images from page {page_num}")
        
#         # Extract styled text (excluding image regions)
#         styled_content = extract_text_with_style(page, page_num)
#         logger.info(f"📝 Extracted {len(styled_content)} text items from page {page_num}")
        
#         # Check for mathematical content
#         is_math_heavy, math_percentage = analyze_page_for_math(styled_content)
        
#         if is_math_heavy:
#             logger.info(f"📐 Page {page_num} contains significant mathematical content ({math_percentage:.1f}%)")
#             detected_langs, _ = detect_all_languages_in_content(styled_content, threshold=5.0)
#             verified_langs = verify_tesseract_languages(detected_langs)
#             return ocr_mathematical_content(page_image, page_num, images, verified_langs)
        
#         # Check if we have meaningful text
#         if not styled_content or len(styled_content) == 0:
#             logger.info(f"🔍 No extractable text on page {page_num} - Using OCR")
#             detected_langs = ['eng', 'hin']
#             return ocr_with_languages(page_image, page_num, images, detected_langs)
        
#         # Detect languages
#         detected_langs, approach = detect_all_languages_in_content(styled_content, threshold=5.0)
        
#         # Get script analysis
#         sample_texts = [item['text'] for item in styled_content[:100] if item['text'].strip()]
#         combined_text = " ".join(sample_texts)
#         script_analysis = analyze_script_distribution(combined_text)
        
#         # Prioritize languages
#         prioritized_langs = prioritize_languages(detected_langs, script_analysis)
#         verified_langs = verify_tesseract_languages(prioritized_langs)
        
#         if approach == 'extraction':
#             total_text = "".join([item['text'] for item in styled_content])
#             words = [w for w in total_text.split() if len(w) > 1]
#             meaningful_words = [w for w in words if any(c.isalnum() for c in w)]
            
#             logger.info(f"📊 Found {len(meaningful_words)} meaningful words")
            
#             if len(meaningful_words) > 10:
#                 # Use styled text extraction with images in correct order
#                 html_content = format_styled_text_with_images(styled_content, images)
#                 logger.info(f"✅ Using text extraction for page {page_num}")
                
#                 return {
#                     'page_num': page_num,
#                     'html': html_content,
#                     'images': images,
#                     'success': True,
#                     'method': 'extraction',
#                     'languages': verified_langs
#                 }
        
#         # Fall back to OCR
#         logger.info(f"🔍 Using OCR: {'+'.join(verified_langs)}")
#         return ocr_with_languages(page_image, page_num, images, verified_langs)
        
#     except Exception as e:
#         logger.error(f"❌ Failed to process page {page_num}: {e}")
#         import traceback
#         traceback.print_exc()
#         return {
#             'page_num': page_num,
#             'html': format_error_page(page_num, str(e)),
#             'images': [],
#             'success': False,
#             'method': 'error'
#         }


######################same problem

# def extract_non_image_regions(page, page_image, image_regions):
#     """Extract only non-image regions from page image for OCR"""
#     try:
#         from PIL import ImageDraw
        
#         if not image_regions:
#             return page_image
        
#         # Create a copy of the image
#         masked_image = page_image.copy()
#         draw = ImageDraw.Draw(masked_image)
        
#         # Get page dimensions
#         page_rect = page.rect
#         page_width = page_rect.width
#         page_height = page_rect.height
        
#         # Calculate scale factor (page points to image pixels)
#         img_width, img_height = page_image.size
#         scale_x = img_width / page_width
#         scale_y = img_height / page_height
        
#         # Mask out image regions with white
#         for img_rect in image_regions:
#             x0, y0, x1, y1 = img_rect
            
#             # Convert PDF coordinates to image coordinates
#             px0 = int(x0 * scale_x)
#             py0 = int(y0 * scale_y)
#             px1 = int(x1 * scale_x)
#             py1 = int(y1 * scale_y)
            
#             # Add some padding to ensure complete coverage
#             padding = 5
#             px0 = max(0, px0 - padding)
#             py0 = max(0, py0 - padding)
#             px1 = min(img_width, px1 + padding)
#             py1 = min(img_height, py1 + padding)
            
#             # Fill image region with white (255, 255, 255)
#             draw.rectangle([px0, py0, px1, py1], fill='white')
#             logger.debug(f"🎭 Masked image region: ({px0}, {py0}) to ({px1}, {py1})")
        
#         logger.info(f"✅ Masked {len(image_regions)} image regions for OCR")
#         return masked_image
        
#     except Exception as e:
#         logger.warning(f"Failed to mask image regions: {e}")
#         return page_image

def ocr_with_languages(page_image, page_num, images, lang_codes, page=None):
    """Perform OCR with multiple language models, excluding image regions"""
    try:
        # If page object is available, mask image regions
        if page is not None:
            image_regions = get_image_regions(page)
            if image_regions:
                logger.info(f"🎭 Masking {len(image_regions)} image regions before OCR")
                page_image = extract_non_image_regions(page, page_image, image_regions)
        
        # Combine ALL language codes
        lang_string = '+'.join(lang_codes)
        
        # Enhanced Tesseract configuration
        custom_config = r'--oem 3 --psm 6'
        
        logger.info(f"🔍 OCR on page {page_num} with: {lang_string}")
        logger.info(f"📚 Total languages: {len(lang_codes)}")
        
        # Perform OCR with all languages
        text = pytesseract.image_to_string(
            page_image,
            lang=lang_string,
            config=custom_config
        )
        
        if not text.strip():
            logger.warning(f"⚠️ OCR returned empty text for page {page_num}")
        else:
            logger.info(f"✅ OCR extracted {len(text.strip())} characters")
        
        html_content = format_ocr_text(text, images)
        
        return {
            'page_num': page_num,
            'html': html_content,
            'images': images,
            'success': True,
            'method': f'ocr({lang_string})',
            'languages': lang_codes
        }
    except Exception as e:
        logger.error(f"❌ OCR failed for page {page_num}: {e}")
        return {
            'page_num': page_num,
            'html': format_error_page(page_num, str(e)),
            'images': [],
            'success': False,
            'method': 'error'
        }

def ocr_mathematical_content(page_image, page_num, images, lang_codes, page=None):
    """Specialized OCR for mathematical content, excluding image regions"""
    try:
        # Mask image regions if page object available
        if page is not None:
            image_regions = get_image_regions(page)
            if image_regions:
                logger.info(f"🎭 Masking {len(image_regions)} image regions before math OCR")
                page_image = extract_non_image_regions(page, page_image, image_regions)
        
        # Preprocess image
        processed_image = preprocess_image_for_math(page_image)
        
        # Add 'equ' (equation detection) to Tesseract if available
        math_langs = lang_codes.copy()
        
        # Tesseract config for mathematical content
        custom_configs = [
            r'--oem 3 --psm 6',   # Standard
            r'--oem 3 --psm 11',  # Sparse text
            r'--oem 3 --psm 3',   # Fully automatic
        ]
        
        best_text = ""
        best_length = 0
        
        # Try multiple PSM modes
        for config in custom_configs:
            try:
                lang_string = '+'.join(math_langs)
                text = pytesseract.image_to_string(
                    processed_image,
                    lang=lang_string,
                    config=config
                )
                
                if len(text.strip()) > best_length:
                    best_text = text
                    best_length = len(text.strip())
                    
            except Exception as e:
                logger.warning(f"OCR with config '{config}' failed: {e}")
                continue
        
        if not best_text.strip():
            logger.warning(f"⚠️ All OCR attempts returned empty for page {page_num}")
            best_text = "[Mathematical content - OCR unable to extract]"
        
        logger.info(f"✅ Math OCR extracted {len(best_text.strip())} characters")
        
        html_content = format_mathematical_content(best_text, images)
        
        return {
            'page_num': page_num,
            'html': html_content,
            'images': images,
            'success': True,
            'method': f'math_ocr({"+".join(math_langs)})',
            'languages': math_langs
        }
        
    except Exception as e:
        logger.error(f"❌ Mathematical OCR failed for page {page_num}: {e}")
        return {
            'page_num': page_num,
            'html': format_error_page(page_num, str(e)),
            'images': [],
            'success': False,
            'method': 'error'
        }

# def process_page_hybrid(page, page_image, page_num, extract_images=True):
#     """Enhanced page processing that completely separates images from text"""
#     try:
#         # Extract images FIRST to know their positions
#         images = []
#         if extract_images:
#             images = extract_images_from_page(page, page_num)
#             logger.info(f"📷 Extracted {len(images)} images from page {page_num}")
        
#         # Extract styled text (excluding image regions)
#         styled_content = extract_text_with_style(page, page_num)
#         logger.info(f"📝 Extracted {len(styled_content)} text items from page {page_num}")
        
#         # Check for mathematical content
#         is_math_heavy, math_percentage = analyze_page_for_math(styled_content)
        
#         if is_math_heavy:
#             logger.info(f"📐 Page {page_num} contains significant mathematical content ({math_percentage:.1f}%)")
#             detected_langs, _ = detect_all_languages_in_content(styled_content, threshold=5.0)
#             verified_langs = verify_tesseract_languages(detected_langs)
#             # Pass page object for image masking
#             return ocr_mathematical_content(page_image, page_num, images, verified_langs, page)
        
#         # Check if we have meaningful text
#         if not styled_content or len(styled_content) == 0:
#             logger.info(f"🔍 No extractable text on page {page_num} - Using OCR")
#             detected_langs = ['eng', 'hin']
#             # Pass page object for image masking
#             return ocr_with_languages(page_image, page_num, images, detected_langs, page)
        
#         # Detect languages
#         detected_langs, approach = detect_all_languages_in_content(styled_content, threshold=5.0)
        
#         # Get script analysis
#         sample_texts = [item['text'] for item in styled_content[:100] if item['text'].strip()]
#         combined_text = " ".join(sample_texts)
#         script_analysis = analyze_script_distribution(combined_text)
        
#         # Prioritize languages
#         prioritized_langs = prioritize_languages(detected_langs, script_analysis)
#         verified_langs = verify_tesseract_languages(prioritized_langs)
        
#         if approach == 'extraction':
#             total_text = "".join([item['text'] for item in styled_content])
#             words = [w for w in total_text.split() if len(w) > 1]
#             meaningful_words = [w for w in words if any(c.isalnum() for c in w)]
            
#             logger.info(f"📊 Found {len(meaningful_words)} meaningful words")
            
#             if len(meaningful_words) > 10:
#                 # Use styled text extraction with images in correct order
#                 html_content = format_styled_text_with_images(styled_content, images)
#                 logger.info(f"✅ Using text extraction for page {page_num}")
                
#                 return {
#                     'page_num': page_num,
#                     'html': html_content,
#                     'images': images,
#                     'success': True,
#                     'method': 'extraction',
#                     'languages': verified_langs
#                 }
        
#         # Fall back to OCR with image masking
#         logger.info(f"🔍 Using OCR: {'+'.join(verified_langs)}")
#         return ocr_with_languages(page_image, page_num, images, verified_langs, page)
        
#     except Exception as e:
#         logger.error(f"❌ Failed to process page {page_num}: {e}")
#         import traceback
#         traceback.print_exc()
#         return {
#             'page_num': page_num,
#             'html': format_error_page(page_num, str(e)),
#             'images': [],
#             'success': False,
#             'method': 'error'
#         }

def save_debug_image(image, filename):
    """Save debug image to check masking"""
    try:
        debug_dir = "debug_images"
        os.makedirs(debug_dir, exist_ok=True)
        image.save(os.path.join(debug_dir, filename))
        logger.info(f"💾 Saved debug image: {filename}")
    except Exception as e:
        logger.warning(f"Failed to save debug image: {e}")

# Optional: Add debug mode
DEBUG_MODE = False  # Set to True to save masked images

def extract_non_image_regions(page, page_image, image_regions):
    """Extract only non-image regions from page image for OCR"""
    try:
        from PIL import ImageDraw
        
        if not image_regions:
            return page_image
        
        # Save original for debugging
        if DEBUG_MODE:
            save_debug_image(page_image, f"original_page_{id(page_image)}.png")
        
        # Create a copy of the image
        masked_image = page_image.copy()
        draw = ImageDraw.Draw(masked_image)
        
        # Get page dimensions
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height
        
        # Calculate scale factor (page points to image pixels)
        img_width, img_height = page_image.size
        scale_x = img_width / page_width
        scale_y = img_height / page_height
        
        logger.info(f"📏 Page: {page_width}x{page_height}pt, Image: {img_width}x{img_height}px")
        logger.info(f"📏 Scale factors: X={scale_x:.2f}, Y={scale_y:.2f}")
        
        # Mask out image regions with white
        masked_count = 0
        for img_rect in image_regions:
            x0, y0, x1, y1 = img_rect
            
            # Convert PDF coordinates to image coordinates
            px0 = int(x0 * scale_x)
            py0 = int(y0 * scale_y)
            px1 = int(x1 * scale_x)
            py1 = int(y1 * scale_y)
            
            # Add padding to ensure complete coverage
            padding = 10  # Increased padding
            px0 = max(0, px0 - padding)
            py0 = max(0, py0 - padding)
            px1 = min(img_width, px1 + padding)
            py1 = min(img_height, py1 + padding)
            
            # Validate coordinates
            if px1 > px0 and py1 > py0:
                # Fill image region with white (255, 255, 255)
                draw.rectangle([px0, py0, px1, py1], fill='white', outline='red', width=2)
                masked_count += 1
                logger.info(f"🎭 Masked region {masked_count}: PDF({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}) → IMG({px0},{py0},{px1},{py1})")
            else:
                logger.warning(f"⚠️ Invalid coordinates: ({px0},{py0},{px1},{py1})")
        
        # Save masked image for debugging
        if DEBUG_MODE:
            save_debug_image(masked_image, f"masked_page_{id(page_image)}.png")
        
        logger.info(f"✅ Successfully masked {masked_count}/{len(image_regions)} image regions")
        return masked_image
        
    except Exception as e:
        logger.error(f"Failed to mask image regions: {e}")
        import traceback
        traceback.print_exc()
        return page_image


###################################################################
# scientific signs ke liye 

# Extended Unicode ranges for scientific symbols
SCIENCE_UNICODE_RANGES = {
    'math_operators': (0x2200, 0x22FF),      # ∀∃∈∉⊂⊃∩∪∫∑∏√∞
    'math_alphanumeric': (0x1D400, 0x1D7FF), # 𝐴𝐵𝐶 (bold, italic variants)
    'math_misc': (0x2100, 0x214F),           # ℂℕℝℤ℃℉
    'arrows': (0x2190, 0x21FF),              # ←→↑↓⇒⇔
    'greek': (0x0370, 0x03FF),               # αβγδεθλμπσωΩ
    'subscript': (0x2080, 0x209F),           # ₀₁₂₃
    'superscript': (0x2070, 0x207F),         # ⁰¹²³
    'letterlike': (0x2100, 0x214F),          # ℓ℮℘ℜℑ
    'technical': (0x2300, 0x23FF),           # ⌀⌂⌘
    'geometric': (0x25A0, 0x25FF),           # ■□▲△
    'misc_symbols': (0x2600, 0x26FF),        # ☀☁☂☃
    'dingbats': (0x2700, 0x27BF),            # ✁✂✃✄
}

# Common physics and math symbols mapping
PHYSICS_SYMBOLS = {
    'V': '⚡ V',      # Voltage
    'A': '⚡ A',      # Ampere
    'Ω': 'Ω',         # Ohm
    'Φ': 'Φ',         # Phi (magnetic flux)
    'θ': 'θ',         # Theta (angle)
    'λ': 'λ',         # Lambda (wavelength)
    'μ': 'μ',         # Micro
    'π': 'π',         # Pi
    'Δ': 'Δ',         # Delta (change)
    '∫': '∫',         # Integral
    '∑': '∑',         # Summation
    '∏': '∏',         # Product
    '√': '√',         # Square root
    '∞': '∞',         # Infinity
    '≈': '≈',         # Approximately
    '≠': '≠',         # Not equal
    '≤': '≤',         # Less than or equal
    '≥': '≥',         # Greater than or equal
    '±': '±',         # Plus minus
    '°': '°',         # Degree
    '℃': '℃',         # Celsius
    '℉': '℉',         # Fahrenheit
}

def enhance_image_for_symbols(page_image):
    """Enhanced preprocessing specifically for scientific symbols"""
    try:
        from PIL import ImageEnhance, ImageFilter, ImageOps
        
        # Convert to grayscale
        if page_image.mode != 'L':
            page_image = page_image.convert('L')
        
        # Increase DPI if too low (helps with small symbols)
        width, height = page_image.size
        if width < 2000:  # Upscale if needed
            scale_factor = 2000 / width
            new_size = (int(width * scale_factor), int(height * scale_factor))
            page_image = page_image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"🔍 Upscaled image to {new_size} for better symbol recognition")
        
        # Apply adaptive thresholding for better contrast
        # This helps separate symbols from background
        page_image = ImageOps.autocontrast(page_image, cutoff=2)
        
        # Increase sharpness significantly
        enhancer = ImageEnhance.Sharpness(page_image)
        page_image = enhancer.enhance(3.0)  # Very sharp
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(page_image)
        page_image = enhancer.enhance(2.5)  # High contrast
        
        # Apply unsharp mask for clarity
        page_image = page_image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        return page_image
        
    except Exception as e:
        logger.warning(f"Symbol enhancement failed: {e}")
        return page_image

def detect_scientific_symbols(text):
    """Detect if text contains scientific/mathematical symbols"""
    if not text:
        return False, []
    
    found_symbols = []
    
    # Check for Unicode scientific symbols
    for char in text:
        code_point = ord(char)
        for range_name, (start, end) in SCIENCE_UNICODE_RANGES.items():
            if start <= code_point <= end:
                found_symbols.append((char, range_name))
                break
    
    # Check for common physics notations
    physics_patterns = [
        r'[VIR]\s*=',           # V=IR (Ohm's law)
        r'\d+\s*[VAΩ]',         # 5V, 10A, 100Ω
        r'[a-zA-Z]\s*[²³⁴]',    # x², y³
        r'[a-zA-Z]₀',           # V₀, I₀
        r'[°℃℉]',               # Temperature
        r'[Δδ][a-zA-Z]',        # ΔV, δx
        r'[∫∑∏]',               # Calculus
        r'[αβγδεθλμπσωΩΦ]',     # Greek letters
    ]
    
    for pattern in physics_patterns:
        if re.search(pattern, text):
            found_symbols.append((pattern, 'physics_notation'))
    
    has_symbols = len(found_symbols) > 0
    return has_symbols, found_symbols

def configure_tesseract_for_symbols(lang_codes):
    """Configure Tesseract for better symbol recognition"""
    # Tesseract configurations optimized for symbols
    configs = []
    
    # Config 1: Standard with symbol preservation
    configs.append({
        'config': r'--oem 3 --psm 6 -c preserve_interword_spaces=1',
        'description': 'Standard with space preservation'
    })
    
    # Config 2: For equations and formulas
    configs.append({
        'config': r'--oem 3 --psm 11 -c preserve_interword_spaces=1',
        'description': 'Sparse text (good for equations)'
    })
    
    # Config 3: Single block
    configs.append({
        'config': r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-=×÷∫∑∏√∞±≈≠≤≥°ΩμπθλΔΦαβγδεωΨ ',
        'description': 'With symbol whitelist'
    })
    
    return configs

def ocr_with_symbol_support(page_image, page_num, images, lang_codes, page=None):
    """Enhanced OCR with better symbol recognition"""
    try:
        # Mask image regions if page available
        if page is not None:
            image_regions = get_image_regions(page)
            if image_regions:
                logger.info(f"🎭 Masking {len(image_regions)} image regions")
                page_image = extract_non_image_regions(page, page_image, image_regions)
        
        # Enhanced preprocessing for symbols
        logger.info("🔬 Applying symbol-enhanced preprocessing")
        processed_image = enhance_image_for_symbols(page_image)
        
        # Get Tesseract configurations
        lang_string = '+'.join(lang_codes)
        configs = configure_tesseract_for_symbols(lang_codes)
        
        best_text = ""
        best_length = 0
        best_config = ""
        
        # Try multiple configurations
        for config_info in configs:
            try:
                config_str = config_info['config']
                description = config_info['description']
                
                logger.info(f"🔍 Trying: {description}")
                
                text = pytesseract.image_to_string(
                    processed_image,
                    lang=lang_string,
                    config=config_str
                )
                
                # Check for scientific symbols
                has_symbols, found_symbols = detect_scientific_symbols(text)
                
                if has_symbols:
                    logger.info(f"✨ Found {len(found_symbols)} scientific symbols")
                
                # Prefer text with more content
                text_length = len(text.strip())
                if text_length > best_length:
                    best_text = text
                    best_length = text_length
                    best_config = description
                
            except Exception as e:
                logger.warning(f"Config '{description}' failed: {e}")
                continue
        
        if not best_text.strip():
            logger.warning(f"⚠️ All OCR attempts returned empty for page {page_num}")
            best_text = "[Content could not be extracted]"
        else:
            logger.info(f"✅ Best result from: {best_config}")
            logger.info(f"✅ Extracted {len(best_text.strip())} characters")
        
        # Post-process to preserve symbols
        best_text = post_process_scientific_text(best_text)
        
        html_content = format_scientific_text(best_text, images)
        
        return {
            'page_num': page_num,
            'html': html_content,
            'images': images,
            'success': True,
            'method': f'symbol_ocr({lang_string})',
            'languages': lang_codes
        }
        
    except Exception as e:
        logger.error(f"❌ Symbol OCR failed for page {page_num}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'page_num': page_num,
            'html': format_error_page(page_num, str(e)),
            'images': [],
            'success': False,
            'method': 'error'
        }

def post_process_scientific_text(text):
    """Post-process OCR text to fix common symbol misrecognitions"""
    
    # Common OCR mistakes for scientific symbols
    replacements = {
        # Greek letters often misread
        r'\bph1\b': 'Φ',
        r'\balpha\b': 'α',
        r'\bbeta\b': 'β',
        r'\bgamma\b': 'γ',
        r'\bdelta\b': 'δ',
        r'\btheta\b': 'θ',
        r'\blambda\b': 'λ',
        r'\bmu\b': 'μ',
        r'\bpi\b': 'π',
        r'\bsigma\b': 'σ',
        r'\bomega\b': 'ω',
        r'\bOmega\b': 'Ω',
        
        # Common symbol mistakes
        r'ohm': 'Ω',
        r'ohms': 'Ω',
        r'\binfinity\b': '∞',
        r'\bdelta\b': 'Δ',
        
        # Units
        r'(\d+)\s*volt': r'\1V',
        r'(\d+)\s*ampere': r'\1A',
        r'(\d+)\s*ohm': r'\1Ω',
        r'(\d+)\s*degree': r'\1°',
        
        # Math operators
        r'<=': '≤',
        r'>=': '≥',
        r'!=': '≠',
        r'~=': '≈',
        r'\+/-': '±',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_scientific_text(text, images):
    """Format scientific text with proper symbol rendering"""
    text = text.strip()
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    paragraphs = text.split('\n\n')
    html_parts = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Detect if paragraph contains scientific content
        has_symbols, found_symbols = detect_scientific_symbols(para)
        
        # Check if it's an equation/formula (high symbol density)
        is_equation = False
        if has_symbols:
            symbol_density = len(found_symbols) / len(para) if len(para) > 0 else 0
            is_equation = symbol_density > 0.15  # 15% symbols = likely equation
        
        para_escaped = html.escape(para)
        
        if is_equation:
            # Format as equation
            para_escaped = para_escaped.replace(' ', '&nbsp;')
            html_parts.append(f'<div class="scientific-equation">{para_escaped}</div>')
        elif has_symbols:
            # Text with symbols - preserve spacing
            html_parts.append(f'<p class="scientific-text">{para_escaped}</p>')
        else:
            # Regular text
            if len(para.split()) <= 6 and not para.endswith(('.', ',', ';')):
                html_parts.append(f'<h3 class="section-heading">{para_escaped}</h3>')
            else:
                html_parts.append(f'<p class="paragraph">{para_escaped}</p>')
    
    if not html_parts:
        html_parts.append('<p class="empty">[No content detected]</p>')
    
    # Add images
    for img in images:
        html_parts.append(f'''<div class="image-container scientific-image">
            <img src="../Images/{img["filename"]}" alt="Scientific diagram"/>
        </div>''')
    
    return "\n".join(html_parts)

# Update process_page_hybrid to use symbol-aware OCR
def process_page_hybrid(page, page_image, page_num, extract_images=True):
    """Enhanced page processing with scientific symbol support"""
    try:
        # Extract images FIRST
        images = []
        if extract_images:
            images = extract_images_from_page(page, page_num)
            logger.info(f"📷 Extracted {len(images)} images from page {page_num}")
        
        # Extract styled text (excluding image regions)
        styled_content = extract_text_with_style(page, page_num)
        logger.info(f"📝 Extracted {len(styled_content)} text items from page {page_num}")
        
        # Check for scientific symbols in extracted text
        all_text = " ".join([item['text'] for item in styled_content])
        has_symbols, found_symbols = detect_scientific_symbols(all_text)
        
        if has_symbols:
            logger.info(f"🔬 Detected {len(found_symbols)} scientific symbols on page {page_num}")
        
        # Check for mathematical content
        is_math_heavy, math_percentage = analyze_page_for_math(styled_content)
        
        # If heavy math or symbols, use enhanced OCR
        if is_math_heavy or (has_symbols and len(found_symbols) > 10):
            logger.info(f"📐 Page {page_num} contains significant scientific content")
            detected_langs, _ = detect_all_languages_in_content(styled_content, threshold=5.0)
            verified_langs = verify_tesseract_languages(detected_langs)
            return ocr_with_symbol_support(page_image, page_num, images, verified_langs, page)
        
        # Check if we have meaningful text
        if not styled_content or len(styled_content) == 0:
            logger.info(f"🔍 No extractable text on page {page_num} - Using enhanced OCR")
            detected_langs = ['eng', 'hin']
            return ocr_with_symbol_support(page_image, page_num, images, detected_langs, page)
        
        # Detect languages
        detected_langs, approach = detect_all_languages_in_content(styled_content, threshold=5.0)
        
        # Get script analysis
        sample_texts = [item['text'] for item in styled_content[:100] if item['text'].strip()]
        combined_text = " ".join(sample_texts)
        script_analysis = analyze_script_distribution(combined_text)
        
        # Prioritize languages
        prioritized_langs = prioritize_languages(detected_langs, script_analysis)
        verified_langs = verify_tesseract_languages(prioritized_langs)
        
        if approach == 'extraction':
            total_text = "".join([item['text'] for item in styled_content])
            words = [w for w in total_text.split() if len(w) > 1]
            meaningful_words = [w for w in words if any(c.isalnum() for c in w)]
            
            logger.info(f"📊 Found {len(meaningful_words)} meaningful words")
            
            if len(meaningful_words) > 10:
                html_content = format_styled_text_with_images(styled_content, images)
                logger.info(f"✅ Using text extraction for page {page_num}")
                
                return {
                    'page_num': page_num,
                    'html': html_content,
                    'images': images,
                    'success': True,
                    'method': 'extraction',
                    'languages': verified_langs
                }
        
        # Fall back to symbol-aware OCR
        logger.info(f"🔍 Using symbol-aware OCR: {'+'.join(verified_langs)}")
        return ocr_with_symbol_support(page_image, page_num, images, verified_langs, page)
        
    except Exception as e:
        logger.error(f"❌ Failed to process page {page_num}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'page_num': page_num,
            'html': format_error_page(page_num, str(e)),
            'images': [],
            'success': False,
            'method': 'error'
        }


####################################################################



# def format_ocr_text(text, images):
#     """Format OCR text into HTML"""
#     text = text.strip()
#     text = re.sub(r'\n{3,}', '\n\n', text)
    
#     paragraphs = text.split('\n\n')
#     html_parts = []
    
#     for para in paragraphs:
#         para = para.strip()
#         if para:
#             if len(para.split()) <= 6 and not para.endswith(('.', ',', ';')):
#                 html_parts.append(f'<h3 class="section-heading">{html.escape(para)}</h3>')
#             else:
#                 html_parts.append(f'<p class="paragraph">{html.escape(para)}</p>')
    
#     if not any(para.strip() for para in paragraphs):
#         html_parts.append('<p class="empty">[No text detected on this page]</p>')
    
#     # Add images
#     for img in images:
#         html_parts.append(f'<div class="image-container"><img src="Images/{img["filename"]}" alt="Page image"/></div>')
    
#     return "\n".join(html_parts)

def format_error_page(page_num, error_msg):
    """Create error page HTML"""
    return f'''<div class="error-container">
                <h2>Page {page_num}</h2>
                <p class="error">Error processing page: {html.escape(error_msg)}</p>
            </div>'''

# ---------------------------
# STEP 5: ENHANCED EPUB CREATION
# ---------------------------
# def create_epub_enhanced(metadata, page_data, output_path):
#     """Create EPUB with images, styles, and proper navigation"""
#     temp_dir = "temp_epub"
    
#     try:
#         # Setup directory structure
#         os.makedirs(temp_dir, exist_ok=True)
#         os.makedirs(os.path.join(temp_dir, "META-INF"), exist_ok=True)
#         os.makedirs(os.path.join(temp_dir, "OEBPS"), exist_ok=True)
#         os.makedirs(os.path.join(temp_dir, "OEBPS", "Styles"), exist_ok=True)
#         os.makedirs(os.path.join(temp_dir, "OEBPS", "Images"), exist_ok=True)
#         os.makedirs(os.path.join(temp_dir, "OEBPS", "Text"), exist_ok=True)
        
#         # 1. Create mimetype
#         with open(os.path.join(temp_dir, "mimetype"), "w", encoding="utf-8") as f:
#             f.write("application/epub+zip")
        
#         # 2. Create container.xml
#         container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
#                     <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
#                         <rootfiles>
#                             <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
#                         </rootfiles>
#                     </container>'''
        
#         with open(os.path.join(temp_dir, "META-INF", "container.xml"), "w", encoding="utf-8") as f:
#             f.write(container_xml)
        
#         # 3. Create enhanced CSS
#         css_content = '''@namespace epub "http://www.idpf.org/2007/ops";

#                         body {
#                             font-family: "Noto Sans Devanagari", "Mangal", "Arial Unicode MS", "Nirmala UI", sans-serif;
#                             line-height: 1.8;
#                             font-size: 1em;
#                             margin: 0;
#                             padding: 2em;
#                             color: #333;
#                             background-color: #fff;
#                         }

#                         .container {
#                             max-width: 800px;
#                             margin: 0 auto;
#                         }

#                         .page {
#                             margin-bottom: 3em;
#                             page-break-after: always;
#                         }

#                         .page-header {
#                             color: #2c3e50;
#                             border-bottom: 2px solid #3498db;
#                             padding-bottom: 0.5em;
#                             margin-top: 2em;
#                             margin-bottom: 1.5em;
#                             font-size: 1.4em;
#                             font-weight: 600;
#                             text-align: center;
#                         }

#                         h1, h2, h3 {
#                             color: #34495e;
#                             margin-top: 1.5em;
#                             margin-bottom: 1em;
#                             font-weight: 500;
#                         }

#                         h1 { font-size: 2em; }
#                         h2 { font-size: 1.5em; }
#                         h3 { font-size: 1.2em; }

#                         .section-heading {
#                             color: #34495e;
#                             margin-top: 1.5em;
#                             margin-bottom: 1em;
#                             font-size: 1.2em;
#                             font-weight: 500;
#                             border-left: 4px solid #3498db;
#                             padding-left: 1em;
#                         }

#                         p {
#                             margin: 1em 0;
#                             text-align: justify;
#                         }

#                         .paragraph {
#                             text-indent: 1.5em;
#                         }

#                         .image-container {
#                             text-align: center;
#                             margin: 2em 0;
#                             page-break-inside: avoid;
#                         }

#                         .image-container img {
#                             max-width: 100%;
#                             height: auto;
#                             border: 1px solid #ddd;
#                             border-radius: 4px;
#                             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#                         }

#                         .error-container {
#                             background-color: #fdf2f2;
#                             padding: 1.5em;
#                             border-radius: 4px;
#                             border-left: 4px solid #e74c3c;
#                             margin: 1em 0;
#                         }

#                         .error {
#                             color: #e74c3c;
#                             font-style: italic;
#                         }

#                         .empty {
#                             color: #999;
#                             font-style: italic;
#                             text-align: center;
#                             margin: 2em 0;
#                         }

#                         /* TOC Styling */
#                         nav[epub|type~="toc"] {
#                             page-break-before: always;
#                         }

#                         nav[epub|type~="toc"] > ol {
#                             list-style-type: none;
#                             padding-left: 0;
#                         }

#                         nav[epub|type~="toc"] > ol > li {
#                             margin: 0.5em 0;
#                             padding: 0.5em;
#                             border-bottom: 1px solid #eee;
#                         }

#                         nav[epub|type~="toc"] a {
#                             text-decoration: none;
#                             color: #3498db;
#                             display: block;
#                         }

#                         nav[epub|type~="toc"] a:hover {
#                             color: #2980b9;
#                             text-decoration: underline;
#                         }

#                         /* Nested TOC levels */
#                         nav[epub|type~="toc"] ol ol {
#                             list-style-type: none;
#                             padding-left: 2em;
#                         }'''
        
#         with open(os.path.join(temp_dir, "OEBPS", "Styles", "style.css"), "w", encoding="utf-8") as f:
#             f.write(css_content)
        
#         # 4. Save all images
#         all_images = {}
#         for data in page_data:
#             for img in data['images']:
#                 img_path = os.path.join(temp_dir, "OEBPS", "Images", img['filename'])
#                 with open(img_path, "wb") as f:
#                     f.write(img['data'])
#                 all_images[img['filename']] = img['ext']
        
#         logger.info(f"✅ Saved {len(all_images)} images")
        
#         # 5. Create XHTML files for each page
#         manifest_items = ['    <item id="style" href="Styles/style.css" media-type="text/css"/>']
#         spine_items = []
        
#         for data in page_data:
#             page_num = data['page_num']
#             filename = f"page_{page_num}.xhtml"
            
#             xhtml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
#                                 <!DOCTYPE html>
#                                 <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="hi">
#                                 <head>
#                                     <title>Page {page_num}</title>
#                                     <link rel="stylesheet" type="text/css" href="../Styles/style.css"/>
#                                 </head>
#                                 <body>
#                                     <div class="container">
#                                         <div class="page" id="page-{page_num}">
#                                             <h2 class="page-header">पृष्ठ {page_num} / Page {page_num}</h2>
#                                             {data['html']}
#                                         </div>
#                                     </div>
#                                 </body>
#                                 </html>'''
            
#             with open(os.path.join(temp_dir, "OEBPS", "Text", filename), "w", encoding="utf-8") as f:
#                 f.write(xhtml_content)
            
#             manifest_items.append(f'    <item id="page_{page_num}" href="Text/{filename}" media-type="application/xhtml+xml"/>')
#             spine_items.append(f'    <itemref idref="page_{page_num}"/>')
        
#         # Add images to manifest
#         for img_filename, img_ext in all_images.items():
#             media_type = f"image/{img_ext}" if img_ext != "jpg" else "image/jpeg"
#             img_id = img_filename.replace(".", "_")
#             manifest_items.append(f'    <item id="{img_id}" href="Images/{img_filename}" media-type="{media_type}"/>')
            
#             # 6. Create enhanced navigation document
#             nav_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
#                     <!DOCTYPE html>
#                     <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="hi">
#                     <head>
#                         <title>Table of Contents</title>
#                         <link rel="stylesheet" type="text/css" href="Styles/style.css"/>
#                     </head>
#                     <body>
#                         <nav epub:type="toc" id="toc">
#                             <h1>विषय सूची / Table of Contents</h1>
#                             <ol>
#                     '''
                        
#         # Build hierarchical TOC
#         for item in metadata['toc']:
#             indent = "    " * item['level']
#             page_num = item['page']
#             title = html.escape(item['title'])
#             nav_xhtml += f'{indent}<li><a href="Text/page_{page_num}.xhtml">{title}</a></li>\n'
        
#         nav_xhtml += '''        </ol>
#                         </nav>
                        
#                         <nav epub:type="page-list">
#                             <h2>पृष्ठ सूची / Page List</h2>
#                             <ol>
#                     '''
                            
#         for data in page_data:
#                                 page_num = data['page_num']
#                                 nav_xhtml += f'            <li><a href="Text/page_{page_num}.xhtml">Page {page_num}</a></li>\n'
                            
#         nav_xhtml += '''        </ol>
#                         </nav>
#                     </body>
#                     </html>'''
        
#         with open(os.path.join(temp_dir, "OEBPS", "nav.xhtml"), "w", encoding="utf-8") as f:
#             f.write(nav_xhtml)
        
#         manifest_items.insert(0, '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
        
#         # 7. Create content.opf
#         current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
#         content_opf = f'''<?xml version="1.0" encoding="UTF-8"?>
#                     <package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid">
#                         <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
#                             <dc:identifier id="uid">urn:uuid:{hashlib.md5(metadata['title'].encode()).hexdigest()}</dc:identifier>
#                             <dc:title>{html.escape(metadata['title'])}</dc:title>
#                             <dc:creator>{html.escape(metadata['author'])}</dc:creator>
#                             <dc:language>hi</dc:language>
#                             <dc:language>en</dc:language>
#                             <dc:date>{current_time}</dc:date>
#                             <dc:subject>{html.escape(metadata.get('subject', ''))}</dc:subject>
#                             <dc:description>Enhanced EPUB with preserved styling, images, and navigation</dc:description>
#                             <meta property="dcterms:modified">{current_time}</meta>
#                         </metadata>
#                         <manifest>
#                     {chr(10).join(manifest_items)}
#                         </manifest>
#                         <spine>
#                     {chr(10).join(spine_items)}
#                         </spine>
#                     </package>'''
        
#         with open(os.path.join(temp_dir, "OEBPS", "content.opf"), "w", encoding="utf-8") as f:
#             f.write(content_opf)
        
#         # 8. Create EPUB zip file
#         with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as epub_zip:
#             # Add mimetype first without compression
#             epub_zip.write(os.path.join(temp_dir, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
            
#             # Add all other files
#             for root, dirs, files in os.walk(temp_dir):
#                 for file in files:
#                     if file == "mimetype":
#                         continue
#                     file_path = os.path.join(root, file)
#                     arcname = os.path.relpath(file_path, temp_dir)
#                     epub_zip.write(file_path, arcname)
        
#         logger.info(f"✅ EPUB created successfully: {output_path}")
        
#     except Exception as e:
#         logger.error(f"Failed to create EPUB: {e}")
#         raise
#     finally:
#         # Cleanup
#         import shutil
#         if os.path.exists(temp_dir):
#             shutil.rmtree(temp_dir, ignore_errors=True)

# ---------------------------
# STEP 6: MAIN PROCESSING
# ---------------------------
def process_pdf_enhanced(pdf_path, output_epub):
    """Main processing function with enhanced features"""
    logger.info("📖 Starting enhanced PDF to EPUB conversion...")
    
    try:
        # Extract metadata and TOC
        logger.info("🔹 Extracting PDF metadata and TOC...")
        metadata = extract_pdf_metadata(pdf_path)
        total_pages = metadata['total_pages']
        logger.info(f"📄 Total pages: {total_pages}")
        logger.info(f"📑 TOC entries: {len(metadata['toc'])}")
        
        # Open PDF document
        doc = fitz.open(pdf_path)
        
        # Convert pages to images for OCR fallback
        logger.info(f"📄 Converting pages to images (DPI: {DPI})...")
        page_images = convert_from_path(pdf_path, dpi=DPI)
        logger.info(f"✅ Converted {len(page_images)} pages")
        
        # Process all pages with hybrid approach
        logger.info(f"🚀 Processing pages with {MAX_THREADS} threads...")
        
        page_data = []
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {}
            
            for i in range(total_pages):
                page = doc[i]
                page_image = page_images[i]
                future = executor.submit(
                    process_page_hybrid,
                    page,
                    page_image,
                    i + 1,
                    EXTRACT_IMAGES
                )
                futures[future] = i + 1
            
            # Collect results
            for future in as_completed(futures):
                page_num = futures[future]
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per page
                    page_data.append(result)
                    status = "✅" if result['success'] else "⚠️"
                    logger.info(f"{status} Processed page {page_num}/{total_pages}")
                except Exception as e:
                    logger.error(f"❌ Error processing page {page_num}: {e}")
                    page_data.append({
                        'page_num': page_num,
                        'html': format_error_page(page_num, str(e)),
                        'images': [],
                        'success': False
                    })
        
        # Sort by page number
        page_data.sort(key=lambda x: x['page_num'])
        
        # Close PDF
        doc.close()
        
        # Create enhanced EPUB
        logger.info("📚 Building enhanced EPUB...")
        create_epub_enhanced(metadata, page_data, output_epub)
        
        # Summary
        successful_pages = sum(1 for p in page_data if p['success'])
        total_images = sum(len(p['images']) for p in page_data)
        
        logger.info("="*60)
        logger.info("✅ CONVERSION COMPLETE!")
        logger.info(f"📊 Successfully processed: {successful_pages}/{total_pages} pages")
        logger.info(f"🖼️  Extracted images: {total_images}")
        logger.info(f"📑 TOC entries: {len(metadata['toc'])}")
        logger.info(f"📖 Output: {output_epub}")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        raise



# ---------------------------
# MAIN EXECUTION
# ---------------------------
if __name__ == "__main__":
    try:
        # Verify Tesseract
        logger.info("🔧 Verifying Tesseract installation...")
        version = pytesseract.get_tesseract_version()
        logger.info(f"✅ Tesseract version: {version}")
        
        # Verify PDF
        logger.info("🔧 Verifying PDF file...")
        if not os.path.exists(PDF_PATH):
            raise FileNotFoundError(f"PDF file not found: {PDF_PATH}")
        
        with fitz.open(PDF_PATH) as doc:
            logger.info(f"✅ PDF loaded: {len(doc)} pages")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(OUTPUT_EPUB)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Run conversion
        process_pdf_enhanced(PDF_PATH, OUTPUT_EPUB)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1) 
    