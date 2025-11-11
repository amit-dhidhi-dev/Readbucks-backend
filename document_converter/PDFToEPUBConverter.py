# import subprocess
# import os
# import fitz  # PyMuPDF
# from PIL import Image
# import io


# def extract_cover_pymupdf(pdf_path, output_path=None, dpi=150):
#     """
#     PyMuPDF use karke PDF se cover image extract karta hai
#     - High quality
#     - Fast processing
#     - Reliable
#     """
#     try:
#         # PDF file check karo
#         if not os.path.exists(pdf_path):
#             print(f"Error: PDF file not found - {pdf_path}")
#             return None
        
#         # PDF open karo
#         pdf_document = fitz.open(pdf_path)
        
#         if len(pdf_document) == 0:
#             print("Error: PDF is empty")
#             return None
        
#         # First page get karo (cover)
#         first_page = pdf_document[0]
        
#         # Matrix for high resolution
#         zoom = dpi / 72  # 72 is default DPI
#         mat = fitz.Matrix(zoom, zoom)
        
#         # Pixmap generate karo
#         pix = first_page.get_pixmap(matrix=mat)
        
#         # PIL Image mein convert karo
#         img_data = pix.tobytes("ppm")
#         img = Image.open(io.BytesIO(img_data))
        
#         # RGB format ensure karo
#         if img.mode != 'RGB':
#             img = img.convert('RGB')
        
        
#         # if output_path nahin diya hai toh
#         if not output_path:
#             output_path = os.path.splitext(pdf_path)[0] + "_cover.jpg"
        
        
#         # Save karo agar output path diya hai
#         if output_path:
#             # Directory create karo agar nahi hai
#             os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', 
#                        exist_ok=True)
            
#             # Quality based on format
#             if output_path.lower().endswith(('.jpg', '.jpeg')):
#                 img.save(output_path, 'JPEG', quality=95)
#             elif output_path.lower().endswith('.png'):
#                 img.save(output_path, 'PNG')
#             else:
#                 # Default JPEG
#                 output_path = output_path + '.jpg' if '.' not in output_path else output_path
#                 img.save(output_path, 'JPEG', quality=95)
            
#             print(f"✓ Cover image saved: {output_path}")
        
#         pdf_document.close()
#         return output_path
        
#     except Exception as e:
#         print(f"✗ Cover extraction failed: {e}")
#         return None


# def pdf_to_epub_with_cover(pdf_path, epub_path):
#     """
#     Calibre se direct conversion with cover extraction
#     """
#     cover_image_path = extract_cover_pymupdf(pdf_path, dpi=300)
#     if cover_image_path:
#         print(f"Using extracted cover image: {cover_image_path}")
#     try:
#         cmd = [
#             'ebook-convert',
#             pdf_path,
#             epub_path,
#             '--cover', cover_image_path,  # Extracted cover image
#         ]
        
#         subprocess.run(cmd, check=True)
#         print(f"Conversion with cover successful: {epub_path}")
#         return True
        
#     except subprocess.CalledProcessError as e:
#         print(f"Conversion failed: {e}")
#         return False

###################################################

import subprocess
import os
import fitz  # PyMuPDF
from PIL import Image
import io
import shutil
import tempfile


def extract_cover_pymupdf(pdf_path, output_path=None, dpi=150, verbose=False):
    """
    Extract the first page (cover) from a PDF using PyMuPDF as a high-quality image.

    Args:
        pdf_path (str): Path to the input PDF.
        output_path (str, optional): Path to save the extracted cover image.
        dpi (int): Output image resolution (default 150).
        verbose (bool): Print extra details for debugging.

    Returns:
        str | None: Path to saved cover image, or None if extraction fails.
    """
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        pdf_document = fitz.open(pdf_path)
        if len(pdf_document) == 0:
            raise ValueError("PDF is empty or corrupted.")

        # Use first page as cover
        first_page = pdf_document[0]
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = first_page.get_pixmap(matrix=mat, alpha=False)

        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        if img.mode != 'RGB':
            img = img.convert('RGB')

        if not output_path:
            output_path = os.path.splitext(pdf_path)[0] + "_cover.jpg"

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        img.save(output_path, 'JPEG', quality=95)
        pdf_document.close()

        if verbose:
            print(f"✓ Cover extracted at {output_path}")

        return output_path

    except Exception as e:
        if verbose:
            print(f"✗ Cover extraction failed: {e}")
        return None


def is_calibre_installed():
    """Check if Calibre's ebook-convert command is available."""
    return shutil.which("ebook-convert") is not None


def pdf_to_epub_with_cover(pdf_path, epub_path, dpi=300, keep_cover=False, verbose=True, overwrite=False):
    """
    Convert a PDF to EPUB using Calibre with extracted cover.

    Args:
        pdf_path (str): Path to input PDF.
        epub_path (str): Desired output EPUB path.
        dpi (int): DPI for cover extraction.
        keep_cover (bool): Keep temporary cover file.
        verbose (bool): Print progress logs.
        overwrite (bool): Replace existing EPUB file.

    Returns:
        dict: { "success": bool, "epub_path": str | None, "cover_path": str | None, "error": str | None }
    """
    result = {"success": False, "epub_path": None, "cover_path": None, "error": None}

    try:
        # Check Calibre availability
        if not is_calibre_installed():
            raise EnvironmentError("Calibre (ebook-convert) is not installed or not in PATH.")

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if os.path.exists(epub_path) and not overwrite:
            raise FileExistsError(f"EPUB already exists: {epub_path}")

        # Extract cover to a temp directory
        temp_dir = tempfile.mkdtemp()
        cover_image_path = os.path.join(temp_dir, "cover.jpg")
        cover_image_path = extract_cover_pymupdf(pdf_path, cover_image_path, dpi=dpi, verbose=verbose)

        if not cover_image_path:
            raise RuntimeError("Cover extraction failed.")

        result["cover_path"] = cover_image_path

        # Run Calibre conversion
        cmd = [
            "ebook-convert",
            pdf_path,
            epub_path,
            "--cover", cover_image_path,
            "--no-default-epub-cover"  # Prevent Calibre from adding its own cover
        ]

        if verbose:
            print("Running Calibre command:")
            print(" ".join(cmd))

        subprocess.run(cmd, check=True)

        if verbose:
            print(f"✓ Conversion successful: {epub_path}")

        result.update({
            "success": True,
            "epub_path": epub_path
        })

    except subprocess.CalledProcessError as e:
        result["error"] = f"Calibre conversion failed: {e}"
    except Exception as e:
        result["error"] = str(e)
    finally:
        # Cleanup temporary cover
        if not keep_cover and result["cover_path"]:
            try:
                os.remove(result["cover_path"])
                shutil.rmtree(os.path.dirname(result["cover_path"]), ignore_errors=True)
            except Exception:
                pass

    return result


# Example usage
# if __name__ == "__main__":
#     pdf_path = "example.pdf"
#     epub_path = "example.epub"
#     result = pdf_to_epub_with_cover(pdf_path, epub_path, dpi=300, verbose=True)

#     print(result)


