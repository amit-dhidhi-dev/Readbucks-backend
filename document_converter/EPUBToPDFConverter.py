
# from ebooklib import epub
# import os
# from pathlib import Path
# from document_converter.PDFFooter import create_pdf_footer
# import subprocess
# import sys
# from utils.cleanup_utils import cleanup_file


# # step 1 get cover image from epub file
# def extract_epub_cover(epub_path: str, output_dir: str = './documents') -> str | None:
#     """
#     Extract cover image from an EPUB file and save it to output_dir.
#     Compatible with all ebooklib versions.
#     """
#     book = epub.read_epub(epub_path)
#     cover_item = None

#     # Try EPUB metadata for cover image ID
#     cover_id = None
#     meta = book.get_metadata('OPF', 'cover')
#     if meta and len(meta) > 0:
#         cover_id = meta[0][0]

#     # Find cover by ID
#     if cover_id:
#         for item in book.get_items():
#             if item.get_id() == cover_id:
#                 cover_item = item
#                 break

#     # Fallback 1: filename contains "cover"
#     if not cover_item:
#         for item in book.get_items():
#             media_type = getattr(item, "media_type", None)
#             name = getattr(item, "get_name", lambda: "")()
#             if media_type and media_type.startswith("image/") and "cover" in name.lower():
#                 cover_item = item
#                 break

#     # Fallback 2: pick first image
#     if not cover_item:
#         for item in book.get_items():
#             media_type = getattr(item, "media_type", None)
#             if media_type and media_type.startswith("image/"):
#                 cover_item = item
#                 break

#     if not cover_item:
#         print("❌ No cover image found in EPUB.")
#         return None

#     # Ensure output directory exists
    
#     os.makedirs(output_dir, exist_ok=True)

#     # Determine extension and output path
#     name = getattr(cover_item, "get_name", lambda: "cover.jpg")()
#     image_ext = os.path.splitext(name)[-1] or ".jpg"
#     cover_filename = f"{os.path.splitext(os.path.basename(epub_path))[0]}_cover{image_ext}"
#     # cover_path = os.path.join(output_dir, cover_filename)
#     cover_path = f"{output_dir}/{cover_filename}"

#     # Save cover image
#     with open(cover_path, "wb") as f:
#         f.write(cover_item.get_content())

#     print(f"✅ Cover image extracted: {cover_path}")
#     return cover_path


# # step 2 convert epub to pdf
# def convert_epub_to_pdf(epub_path, output_path: str =None):
    
#     # Validate inputs
#     if not os.path.exists(epub_path):
#                 raise FileNotFoundError(f"DOCX file not found: {epub_path}")

#     if not output_path:
#         output_path = Path(epub_path).with_suffix('.pdf');
    
#     # get cover image
#     cover_image_path = extract_epub_cover(epub_path)
    
#     # get footer for pdf
#     footer_content = create_pdf_footer()
    
#     pdf_command = [
#                 "ebook-convert", epub_path, output_path,
#                 "--paper-size", "a4",
#                 "--pdf-page-numbers",
#                 "--pdf-footer-template", footer_content,
#                 "--pdf-default-font-size", "11",
#                 "--pdf-page-margin-left", "36",
#                 "--pdf-page-margin-right", "36",
#                 "--pdf-page-margin-top", "36",
#                 "--pdf-page-margin-bottom", "36",
#                 "--pdf-standard-font", "sans",  # Corrected: use 'sans' instead of 'helvetica'
#                 "--cover", cover_image_path,
#             ]
   
#     print("Converting EPUB to PDF...")
#     subprocess.run(
#                 pdf_command,
#                 check=True,
#                 capture_output=True,
#                 text=True,
#                 timeout=300  # 5 minute timeout
#             )
  
#     # remove cover image
#     cleanup_file(cover_image_path)
      
#     return output_path;

#######################################################################
from ebooklib import epub
import os
from pathlib import Path
from document_converter.PDFFooter import create_pdf_footer
import subprocess
import sys
from utils.cleanup_utils import cleanup_file
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

# Step 1: Get cover image from EPUB file
def extract_epub_cover(epub_path: str, output_dir: str = './documents') -> Optional[str]:
    """
    Extract cover image from an EPUB file and save it to output_dir.
    Compatible with all ebooklib versions.
    
    Args:
        epub_path: Path to the EPUB file
        output_dir: Directory to save the cover image
        
    Returns:
        Path to the extracted cover image or None if not found
    """
    try:
        book = epub.read_epub(epub_path)
        cover_item = None

        # Try EPUB metadata for cover image ID
        cover_id = None
        meta = book.get_metadata('OPF', 'cover')
        if meta:
            cover_id = meta[0][0] if len(meta) > 0 else None

        # Find cover by ID
        if cover_id:
            for item in book.get_items():
                if item.get_id() == cover_id:
                    cover_item = item
                    break

        # Fallback 1: filename contains "cover"
        if not cover_item:
            for item in book.get_items():
                media_type = getattr(item, "media_type", None)
                name = getattr(item, "get_name", lambda: "")()
                if (media_type and media_type.startswith("image/") 
                    and "cover" in name.lower()):
                    cover_item = item
                    break

        # Fallback 2: pick first image
        if not cover_item:
            for item in book.get_items():
                media_type = getattr(item, "media_type", None)
                if media_type and media_type.startswith("image/"):
                    cover_item = item
                    break

        if not cover_item:
            logger.warning("No cover image found in EPUB: %s", epub_path)
            return None

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Determine extension and output path
        name = getattr(cover_item, "get_name", lambda: "cover.jpg")()
        image_ext = os.path.splitext(name)[-1] or ".jpg"
        base_name = os.path.splitext(os.path.basename(epub_path))[0]
        cover_filename = f"{base_name}_cover{image_ext}"
        cover_path = os.path.join(output_dir, cover_filename)

        # Save cover image
        with open(cover_path, "wb") as f:
            f.write(cover_item.get_content())

        logger.info("Cover image extracted: %s", cover_path)
        return cover_path

    except Exception as e:
        logger.error("Error extracting cover from EPUB %s: %s", epub_path, str(e))
        return None


# Step 2: Convert EPUB to PDF
# def convert_epub_to_pdf(epub_path: str, output_path: Optional[str] = None) -> str:
#     """
#     Convert EPUB file to PDF with cover image and footer.
    
#     Args:
#         epub_path: Path to the EPUB file
#         output_path: Optional output path for PDF (defaults to same name with .pdf extension)
        
#     Returns:
#         Path to the generated PDF file
        
#     Raises:
#         FileNotFoundError: If EPUB file doesn't exist
#         subprocess.CalledProcessError: If conversion fails
#         Exception: For other errors
#     """
#     # Validate inputs
#     if not os.path.exists(epub_path):
#         raise FileNotFoundError(f"EPUB file not found: {epub_path}")

#     if not output_path:
#         output_path = str(Path(epub_path).with_suffix('.pdf'))
    
#     cover_image_path = None
#     try:
#         # Get cover image
#         cover_image_path = extract_epub_cover(epub_path)
        
#         # Get footer for PDF
#         footer_content = create_pdf_footer()
        
#         # Build conversion command
#         pdf_command = [
#             "ebook-convert", epub_path, output_path,
#             "--paper-size", "a4",
#             "--pdf-page-numbers",
#             "--pdf-footer-template", footer_content,
#             "--pdf-default-font-size", "11",
#             "--pdf-page-margin-left", "36",
#             "--pdf-page-margin-right", "36",
#             "--pdf-page-margin-top", "36",
#             "--pdf-page-margin-bottom", "36",
#             "--pdf-standard-font", "sans",
#         ]
        
#         # Add cover if available
#         if cover_image_path and os.path.exists(cover_image_path):
#             pdf_command.extend(["--cover", cover_image_path])
#         else:
#             logger.warning("No cover image available for EPUB: %s", epub_path)

#         logger.info("Converting EPUB to PDF: %s -> %s", epub_path, output_path)
        
#         # Execute conversion
#         result = subprocess.run(
#             pdf_command,
#             check=True,
#             capture_output=True,
#             text=True,
#             timeout=300  # 5 minute timeout
#         )
        
#         logger.info("Successfully converted EPUB to PDF: %s", output_path)
#         return output_path

#     except subprocess.CalledProcessError as e:
#         logger.error("PDF conversion failed for %s: %s", epub_path, e.stderr)
#         # Clean up partially created PDF if it exists
#         if os.path.exists(output_path):
#             cleanup_file(output_path)
#         raise
#     except Exception as e:
#         logger.error("Unexpected error during EPUB to PDF conversion: %s", str(e))
#         raise
#     finally:
#         # Always clean up cover image
#         if cover_image_path and os.path.exists(cover_image_path):
#             cleanup_file(cover_image_path)

def convert_epub_to_pdf(epub_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert EPUB file to PDF with dynamic timeout based on file size.
    """
    # Validate inputs
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")

    if not output_path:
        output_path = str(Path(epub_path).with_suffix('.pdf'))
    
    cover_image_path = None
    process = None
    
    try:
        # Get cover image
        cover_image_path = extract_epub_cover(epub_path)
        footer_content = create_pdf_footer()
        
        # Calculate dynamic timeout based on file size
        file_size_mb = os.path.getsize(epub_path) / (1024 * 1024)
        timeout = calculate_timeout(file_size_mb)
        
        logger.info("File size: %.2f MB, Using timeout: %d seconds", file_size_mb, timeout)
        
        pdf_command = [
            "ebook-convert", epub_path, output_path,
            "--paper-size", "a4",
            "--pdf-page-numbers",
            "--pdf-footer-template", footer_content,
            "--pdf-default-font-size", "11",
            "--pdf-page-margin-left", "36",
            "--pdf-page-margin-right", "36",
            "--pdf-page-margin-top", "36",
            "--pdf-page-margin-bottom", "36",
            "--pdf-standard-font", "sans",
        ]
        
        if cover_image_path and os.path.exists(cover_image_path):
            pdf_command.extend(["--cover", cover_image_path])

        logger.info("Converting EPUB to PDF (timeout: %ds): %s", timeout, epub_path)
        
        # Execute with timeout
        process = subprocess.Popen(
            pdf_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode, pdf_command, stdout, stderr
                )
                
            logger.info("Successfully converted: %s", output_path)
            return output_path
            
        except subprocess.TimeoutExpired:
            logger.error("Conversion timeout after %d seconds for: %s", timeout, epub_path)
            # Kill the process
            process.kill()
            stdout, stderr = process.communicate()
            raise TimeoutError(f"PDF conversion timed out after {timeout} seconds")
            
    except subprocess.TimeoutExpired:
        # Handle case where kill also takes time
        if process:
            process.kill()
            process.wait()
        raise TimeoutError(f"PDF conversion timed out after {timeout} seconds")
        
    except subprocess.CalledProcessError as e:
        logger.error("PDF conversion failed: %s", e.stderr)
        if os.path.exists(output_path):
            cleanup_file(output_path)
        raise
            
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        if os.path.exists(output_path):
            cleanup_file(output_path)
        raise
        
    finally:
        # Always clean up
        if cover_image_path and os.path.exists(cover_image_path):
            cleanup_file(cover_image_path)
        if process and process.poll() is None:
            process.kill()


def calculate_timeout(file_size_mb: float) -> int:
    """
    Calculate timeout based on file size.
    - Small files (<10MB): 2 minutes
    - Medium files (10-50MB): 5 minutes  
    - Large files (50-100MB): 10 minutes
    - Very large files (>100MB): 15 minutes
    """
    if file_size_mb < 10:
        return 120    # 2 minutes
    elif file_size_mb < 50:
        return 300    # 5 minutes
    elif file_size_mb < 100:
        return 600    # 10 minutes
    else:
        return 900    # 15 minutes



