import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple, List
from docx import Document
from zipfile import ZipFile
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from watermark import add_epub_watermark
except ImportError:
    logger.warning("Watermark module not available, proceeding without watermarking")
    def add_epub_watermark(epub_path: str) -> str:
        return epub_path


class DocxConverter:
    """Handles DOCX to EPUB and PDF conversion using Calibre"""
    
    def __init__(self, website_name: str = "Readbucks"):
        self.website_name = website_name
        self.temp_dir = tempfile.mkdtemp()
        
    def __del__(self):
        """Cleanup temporary directory"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def has_cover_page(self, docx_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if DOCX has a cover page and extract cover image.
        
        Returns:
            Tuple[has_cover, cover_image_path]
        """
        cover_image_path = None
        
        try:
                       
            # Check first few paragraphs and sections
            doc = Document(docx_path)
            first_elements = doc.paragraphs[:5]
            
            for para in first_elements:
                text = para.text.strip().lower()
                # Check for cover text or images
                if any(keyword in text for keyword in ['cover', 'title', 'book name']):
                    cover_image_path = self._extract_first_image(docx_path)
                    return True, cover_image_path
                # Check for images in paragraph
                if len(para._element.xpath(".//w:drawing")) > 0:
                    cover_image_path = self._extract_first_image(docx_path)
                    return True, cover_image_path
            
            
              # If no cover text found but images exist, use first image as cover
            
            
            cover_image_path = self._extract_first_image(docx_path)
            print('cover image path inside has_cover_page is ',cover_image_path)
            if cover_image_path:
                return True, cover_image_path       
        except Exception as e:
            logger.warning(f"Error checking cover page: {e}")
            
        return False, cover_image_path

    def _extract_first_image(self, docx_path: str) -> Optional[str]:
        """Extract the first image from DOCX to use as cover image."""
        try:
            with ZipFile(docx_path, "r") as z:
                # Get all image files sorted to ensure consistent selection
                image_files = [
                    f for f in z.namelist() 
                    if f.startswith("word/media/") 
                    and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.emf', '.wmf'))
                ]
                
                if image_files:
                    # Use the first image found
                    first_image = image_files[0]
                    cover_filename = os.path.basename(first_image)
                    cover_image_path = os.path.join(self.temp_dir, cover_filename)
                    
                    # Extract the image
                    with z.open(first_image) as source, open(cover_image_path, 'wb') as target:
                        target.write(source.read())
                    
                    logger.info(f"Extracted cover image: {cover_image_path}")
                    return cover_image_path
                    
        except Exception as e:
            logger.warning(f"Error extracting cover image: {e}")
            
        return None

    def create_pdf_footer(self) -> str:
        """Create PDF footer template with watermark and page numbers."""
        return f'''<div style="width: 100%; font-size: 10pt; font-family: Arial, sans-serif;">
                    <div style="float: left; width: 50%; text-align: left;">
                        Page <span style="font-weight: bold;">_PAGENUM_</span>
                    </div>
                    <div style="float: right; width: 50%; text-align: right; color: #666666; font-style: italic;">
                        {self.website_name}
                    </div>
                </div>'''

    def _run_calibre_command(self, command: List[str]) -> bool:
        """Run calibre command with error handling."""
        try:
            # Ensure paths with spaces are properly quoted
            formatted_command = []
            for arg in command:
                if ' ' in arg and not arg.startswith('"'):
                    formatted_command.append(f'"{arg}"')
                else:
                    formatted_command.append(arg)
            
            logger.debug(f"Running command: {' '.join(formatted_command)}")
            
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.stdout:
                logger.debug(f"Command output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Calibre command failed: {e}")
            if e.stderr:
                logger.error(f"Error output: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("Calibre command timed out")
            return False

    def convert_docx_with_calibre(self, docx_path: str, output_dir: str) -> Tuple[bool, str, str, str]:
        """
        Convert DOCX → EPUB and PDF using Calibre CLI (ebook-convert)
        
        Returns:
            Tuple[success, epub_path, watermarked_epub_path, pdf_path]
        """
        epub_path = ""
        watermarked_epub = ""
        pdf_path = ""
        
        try:
            # Validate inputs
            if not os.path.exists(docx_path):
                raise FileNotFoundError(f"DOCX file not found: {docx_path}")
                
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            base_name = Path(docx_path).stem
            epub_path = os.path.join(output_dir, f"{base_name}.epub")
            pdf_path = os.path.join(output_dir, f"{base_name}.pdf")

            # Check if cover page exists and extract cover image
            has_cover, cover_image_path = self.has_cover_page(docx_path)
            
            print('cover image path is ',cover_image_path)
            print('has_cover image path is ',has_cover)
            cover_option = []
            
            if has_cover and cover_image_path and os.path.exists(cover_image_path):
                cover_option = ["--cover", cover_image_path]
                logger.info(f"Using cover image: {cover_image_path}")
            else:
                logger.info("No suitable cover image found, proceeding without cover")

            # Common conversion arguments for better structure
            common_args = [
                "--chapter", "//h:h1",
                "--page-breaks-before", "//h:h1",
                "--level1-toc", "//h:h1",
                "--level2-toc", "//h:h2",
                "--enable-heuristics",
            ]

            # DOCX → EPUB
            epub_command = [
                "ebook-convert", 
                docx_path, 
                epub_path,
                *cover_option,
                *common_args,
            ]
            
            logger.info("Converting DOCX to EPUB...")
            if not self._run_calibre_command(epub_command):
                raise RuntimeError("EPUB conversion failed")

            # Apply watermark to EPUB
            logger.info("Applying watermark to EPUB...")
            try:
                watermarked_epub = add_epub_watermark(epub_path)
                logger.info(f"Watermark applied successfully: {watermarked_epub}")
            except Exception as e:
                logger.warning(f"Watermarking failed, using original EPUB: {e}")
                watermarked_epub = epub_path

            # DOCX → PDF with footer
            footer_content = self.create_pdf_footer()
            
            pdf_command = [
                "ebook-convert", 
                docx_path, 
                pdf_path,
                "--paper-size", "a4",
                "--pdf-page-numbers",
                "--pdf-footer-template", footer_content,
                "--pdf-default-font-size", "11",
                "--pdf-page-margin-left", "36",
                "--pdf-page-margin-right", "36",
                "--pdf-page-margin-top", "36",
                "--pdf-page-margin-bottom", "36",
                "--pdf-standard-font", "sans",  # Corrected: use 'sans' instead of 'helvetica'
                *cover_option,
                *common_args,
            ]
            
            logger.info("Converting DOCX to PDF...")
            if not self._run_calibre_command(pdf_command):
                raise RuntimeError("PDF conversion failed")

            logger.info(f"✅ EPUB generated at: {epub_path}")
            logger.info(f"✅ Watermarked EPUB generated at: {watermarked_epub}")
            logger.info(f"✅ PDF generated at: {pdf_path}")

            return True, epub_path, watermarked_epub, pdf_path

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            # Clean up partially created files
            for file_path in [epub_path, pdf_path]:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"Cleaned up failed conversion file: {file_path}")
                    except Exception:
                        pass
            return False, "", "", ""


def convert_docx_with_calibre(docx_path: str, output_dir: str, website_name: str = None) -> Tuple[bool, str, str, str]:
    """
    Convenience function for direct usage.
    
    Args:
        docx_path: Path to input DOCX file
        output_dir: Directory where output files should be saved
        website_name: Name for watermark/footer (default: from env or "Readbucks")
    
    Returns:
        Tuple[success, epub_path, watermarked_epub_path, pdf_path]
    """
    website_name = website_name or os.environ.get("WEBSITE_NAME", "Readbucks")
    converter = DocxConverter(website_name)
    return converter.convert_docx_with_calibre(docx_path, output_dir)


# ------------------ USAGE EXAMPLE ------------------

# if __name__ == "__main__":
#     # Example usage
#     input_docx = r"C:\Users\user\Desktop\readbucks.com\backend\documents\ebook_final.docx"
#     output_folder = r"C:\Users\user\Desktop\readbucks.com\backend\documents"
    
#     success, epub_path, watermarked_epub, pdf_path = convert_docx_with_calibre(
#         input_docx, 
#         output_folder,
#         website_name=os.environ.get("WEBSITE_NAME",'Readbucks')
#     )
    
#     if success:
#         print("🎉 Conversion completed successfully!")
#         print(f"EPUB: {epub_path}")
#         print(f"Watermarked EPUB: {watermarked_epub}")
#         print(f"PDF: {pdf_path}")
#     else:
#         print("❌ Conversion failed!")
