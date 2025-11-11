# import os
# import pypandoc
# pypandoc.download_pandoc()
# def convert_book(input_path: str, output_format: str) -> str:
#     """
#     Convert between PDF and EPUB using pypandoc.
#     output_format should be 'pdf' or 'epub'.
#     Returns the path of the converted file.
#     """
#     base, ext = os.path.splitext(input_path)
#     output_path = f"{base}_converted.{output_format}"
    
#     # Convert file
#     pypandoc.convert_file(
#         input_path,
#         to=output_format,
#         outputfile=output_path,
#         extra_args=['--standalone']
#     )
#     return output_path


# def convert_book_auto(input_path, output_format):
#     import os, pypandoc
#     base, ext = os.path.splitext(input_path)
#     output_path = f"{base}_converted.{output_format}"

#     if ext.lower() == ".pdf" and output_format == "epub":
#         from pdf2docx import Converter
#         docx_path = base + ".docx"
#         Converter(input_path).convert(docx_path)
#         pypandoc.download_pandoc()
#         pypandoc.convert_file(docx_path, to="epub", outputfile=output_path)
#         os.remove(docx_path)
#     elif ext.lower() == ".epub" and output_format == "pdf":
#         pypandoc.download_pandoc()
#         pypandoc.convert_file(input_path, to="pdf", outputfile=output_path)
#     else:
#         raise ValueError("Unsupported conversion")
    
#     return output_path

# import pdfplumber
# from ebooklib import epub

# def pdf_to_epub(pdf_path, epub_path):
#     book = epub.EpubBook()
#     book.set_identifier('id123456')
#     book.set_title('Converted PDF Book')
#     book.set_language('en')
#     book.add_author('Unknown')

#     with pdfplumber.open(pdf_path) as pdf:
#         for i, page in enumerate(pdf.pages):
#             text = page.extract_text() or ''
#             if not text.strip():
#                 continue
            
#             safe_text = text.replace("\n", "<br/>")
#             chapter = epub.EpubHtml(
#                 title=f'Page {i+1}',
#                 file_name=f'page_{i+1}.xhtml',
#                 lang='en'
#             )
#             chapter.content = f"<h2>Page {i+1}</h2><p>{safe_text}</p>"
#             book.add_item(chapter)

#             if i == 0:
#                 book.toc = [chapter]
#                 book.spine = ['nav', chapter]
#             else:
#                 book.toc.append(chapter)
#                 book.spine.append(chapter)

#     book.add_item(epub.EpubNcx())
#     book.add_item(epub.EpubNav())

#     epub.write_epub(epub_path, book, {})
#     print(f"✅ EPUB created successfully : {epub_path}")



# from pdf2docx import Converter
# import pypandoc

# def pdf_to_epub_via_docx(pdf_path, epub_path):
#     docx_path = pdf_path.replace(".pdf", ".docx")

#     # Step 1: Convert PDF to DOCX
#     cv = Converter(pdf_path)
#     cv.convert(docx_path, start=0, end=None)
#     cv.close()

#     # Step 2: Convert DOCX to EPUB
#     pypandoc.download_pandoc()
#     pypandoc.convert_file(docx_path, to="epub", outputfile=epub_path)



import pdfplumber
from ebooklib import epub
import html

def pdf_to_epub(pdf_path, epub_path):
    # Create EPUB book
    book = epub.EpubBook()
    book.set_identifier('id123456')
    book.set_title('Converted PDF Book')
    book.set_language('en')
    book.add_author('ReadBucks')

    chapters = []

    # Extract text safely
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            text = html.escape(text)  # escape special chars like <, >
            safe_text = text.replace("\n", "<br/>")

            chapter = epub.EpubHtml(
                title=f'Page {i+1}',
                file_name=f'page_{i+1}.xhtml',
                lang='en'
            )
            chapter.content = f"""
            <!DOCTYPE html>
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head><meta charset="utf-8"/></head>
            <body>
                <h2>Page {i+1}</h2>
                <p>{safe_text}</p>
            </body>
            </html>
            """
            book.add_item(chapter)
            chapters.append(chapter)

    if not chapters:
        raise ValueError("No readable text extracted from PDF!")

    # Add TOC & Spine
    book.toc = tuple(chapters)
    book.spine = ['nav'] + chapters

    # Add navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Add stylesheet
    style = 'body { font-family: Arial; line-height: 1.5; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Write EPUB
    epub.write_epub(epub_path, book)
    print(f"✅ Valid EPUB created: {epub_path}")




