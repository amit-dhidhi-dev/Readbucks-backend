# import subprocess
# import os
# import json
# from pathlib import Path
# from typing import Dict, Any, List, Optional

# class CalibreDocumentConverter:
#     """
#     Complete Document Conversion Suite using Calibre
#     Supports: EPUB ↔ PDF ↔ DOCX ↔ MOBI ↔ AZW3
#     """
    
#     def __init__(self):
#         self.supported_formats = {
#             'input': ['epub', 'pdf', 'docx', 'doc', 'mobi', 'azw3', 'txt', 'html'],
#             'output': ['epub', 'pdf', 'docx', 'mobi', 'azw3', 'html']
#         }
#         self.check_calibre_installation()
    
#     def check_calibre_installation(self):
#         """Check if Calibre is installed and accessible"""
#         try:
#             result = subprocess.run(['ebook-convert', '--version'], 
#                                   capture_output=True, text=True, check=True)
#             print(f"✅ Calibre found: {result.stdout.strip()}")
#             return True
#         except (subprocess.CalledProcessError, FileNotFoundError):
#             print("❌ Calibre not found!")
#             print("Please install Calibre from: https://calibre-ebook.com/download")
#             return False

#     def get_supported_conversions(self) -> List[str]:
#         """Get list of all supported conversion types"""
#         conversions = []
#         for inp in self.supported_formats['input']:
#             for out in self.supported_formats['output']:
#                 if inp != out:
#                     conversions.append(f"{inp.upper()} → {out.upper()}")
#         return conversions

#     def convert_document(self, input_path: str, output_path: str = None, 
#                         options: Dict[str, Any] = None) -> bool:
#         """
#         Universal document converter
        
#         Args:
#             input_path: Input file path
#             output_path: Output file path (optional)
#             options: Conversion options dictionary
        
#         Returns:
#             bool: Success status
#         """
#         try:
#             # Validate input
#             if not os.path.exists(input_path):
#                 raise FileNotFoundError(f"Input file not found: {input_path}")
            
#             input_ext = Path(input_path).suffix.lower()[1:]
#             if input_ext not in self.supported_formats['input']:
#                 raise ValueError(f"Unsupported input format: {input_ext}")
            
#             # Set default output path
#             if output_path is None:
#                 if input_ext == 'docx':
#                     output_path = str(Path(input_path).with_suffix('.epub'))
#                 else:
#                     output_path = str(Path(input_path).with_suffix('.pdf'))
            
#             output_ext = Path(output_path).suffix.lower()[1:]
#             if output_ext not in self.supported_formats['output']:
#                 raise ValueError(f"Unsupported output format: {output_ext}")
            
#             # Get format-specific options
#             format_options = self._get_format_options(input_ext, output_ext, options)
            
#             print(f"🔄 Converting: {Path(input_path).name} → {Path(output_path).name}")
            
#             # Execute conversion
#             cmd = ['ebook-convert', input_path, output_path]
#             cmd.extend(format_options)
            
#             result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
#             if result.returncode == 0:
#                 file_size = os.path.getsize(output_path)
#                 print(f"✅ Successfully created: {output_path} ({file_size:,} bytes)")
#                 return True
#             else:
#                 print(f"❌ Conversion failed with error: {result.stderr}")
#                 return False
                
#         except subprocess.TimeoutExpired:
#             print("❌ Conversion timed out after 5 minutes")
#             return False
#         except Exception as e:
#             print(f"❌ Error during conversion: {str(e)}")
#             return False

#     def _get_format_options(self, input_format: str, output_format: str, 
#                            user_options: Dict[str, Any] = None) -> List[str]:
#         """Get format-specific conversion options"""
        
#         # Default options for all conversions
#         default_options = {
#             'epub_to_pdf': {
#                 '--paper-size': 'a4',
#                 '--pdf-page-margin-left': '40',
#                 '--pdf-page-margin-right': '40',
#                 '--pdf-page-margin-top': '40',
#                 '--pdf-page-margin-bottom': '40',
#                 '--pdf-default-font-size': '12',
#             },
#             'docx_to_epub': {
#                 '--epub-flatten': None,
#                 '--epub-version': '3',
#                 '--chapter': '//h:h1',
#                 '--page-breaks-before': '//h:h1',
#             },
#             'docx_to_pdf': {
#                 '--paper-size': 'a4',
#                 '--pdf-page-margin-left': '40',
#                 '--margin-right': '40',
#                 '--margin-top': '40',
#                 '--margin-bottom': '40',
#             },
#             'pdf_to_epub': {
#                 '--epub-flatten': None,
#                 '--enable-heuristics': None,
#                 '--unwrap-lines': None,
#             }
#         }
        
#         # Get the appropriate option set
#         conversion_key = f"{input_format}_to_{output_format}"
#         options = default_options.get(conversion_key, {})
        
#         # Merge with user options
#         if user_options:
#             # Convert user options to command line format
#             for key, value in user_options.items():
#                 if value is None:
#                     options[f"--{key}"] = None
#                 else:
#                     options[f"--{key}"] = str(value)
        
#         # Convert options to command line arguments
#         cmd_options = []
#         for key, value in options.items():
#             if value is None:
#                 cmd_options.append(key)
#             else:
#                 cmd_options.extend([key, value])
        
#         return cmd_options

#     def batch_convert(self, input_folder: str, output_folder: str, 
#                      output_format: str, pattern: str = "*") -> Dict[str, bool]:
#         """
#         Convert multiple files in a folder
        
#         Args:
#             input_folder: Input folder path
#             output_folder: Output folder path
#             output_format: Target format (epub, pdf, etc.)
#             pattern: File pattern to match (e.g., "*.docx")
        
#         Returns:
#             Dict with conversion results
#         """
#         results = {}
#         input_path = Path(input_folder)
#         output_path = Path(output_folder)
        
#         # Create output folder if it doesn't exist
#         output_path.mkdir(parents=True, exist_ok=True)
        
#         for file_path in input_path.glob(pattern):
#             if file_path.suffix[1:].lower() in self.supported_formats['input']:
#                 output_file = output_path / file_path.with_suffix(f'.{output_format}').name
#                 success = self.convert_document(str(file_path), str(output_file))
#                 results[file_path.name] = success
        
#         return results

#     def get_document_info(self, file_path: str) -> Dict[str, Any]:
#         """
#         Extract metadata and information from document
#         """
#         try:
#             cmd = ['ebook-meta', file_path, '--to-json']
#             result = subprocess.run(cmd, capture_output=True, text=True, check=True)
#             return json.loads(result.stdout)
#         except Exception as e:
#             print(f"❌ Error getting document info: {str(e)}")
#             return {}

# # Usage Examples with Specialized Methods
# class CalibreSpecializedConverters:
#     """Specialized converter classes for common use cases"""
    
#     def __init__(self, converter: CalibreDocumentConverter):
#         self.converter = converter
    
#     def docx_to_epub(self, docx_path: str, epub_path: str = None, 
#                      options: Dict[str, Any] = None) -> bool:
#         """Convert DOCX to EPUB (perfect for ebooks)"""
#         default_opts = {
#             'epub-flatten': None,
#             'epub-version': '3',
#             'chapter': '//h:h1',
#             'page-breaks-before': '//h:h1',
#             'insert-blank-line': None,
#             'change-justification': 'left'
#         }
#         if options:
#             default_opts.update(options)
        
#         return self.converter.convert_document(docx_path, epub_path, default_opts)
    
#     def docx_to_pdf(self, docx_path: str, pdf_path: str = None,
#                    options: Dict[str, Any] = None) -> bool:
#         """Convert DOCX to PDF with professional formatting"""
#         default_opts = {
#             'paper-size': 'a4',
#             'margin-left': '40',
#             'margin-right': '40',
#             'margin-top': '40',
#             'margin-bottom': '40',
#             'pdf-default-font-size': '11',
#             'embed-font-family': 'Times New Roman'
#         }
#         if options:
#             default_opts.update(options)
        
#         return self.converter.convert_document(docx_path, pdf_path, default_opts)
    
#     def pdf_to_epub(self, pdf_path: str, epub_path: str = None,
#                    options: Dict[str, Any] = None) -> bool:
#         """Convert PDF to EPUB (useful for e-readers)"""
#         default_opts = {
#             'enable-heuristics': None,
#             'unwrap-lines': None,
#             'base-font-size': '12',
#             'insert-blank-line': None
#         }
#         if options:
#             default_opts.update(options)
        
#         return self.converter.convert_document(pdf_path, epub_path, default_opts)

# ////////////////////////cover-page, page-number, watermark/////////////////////////////////////



# import subprocess
# import os
# import json
# from pathlib import Path
# from typing import Dict, Any, List, Optional
# import sys
# from docx import Document
# import zipfile

# class CalibreDocumentConverter:
#     """
#     Complete Document Conversion Suite using Calibre with Cover Image Detection and Watermark
#     """
    
#     def __init__(self):
#         self.supported_formats = {
#             'input': ['epub', 'pdf', 'docx', 'doc', 'mobi', 'azw3', 'txt', 'html'],
#             'output': ['epub', 'pdf', 'docx', 'mobi', 'azw3', 'html']
#         }
#         self.watermark_text = os.environ.get("WEBSITE_NAME", "Readbucks")
#         self.check_calibre_installation()
    
#     def check_calibre_installation(self):
#         """Check if Calibre is installed and accessible"""
#         try:
#             result = subprocess.run(['ebook-convert', '--version'], 
#                                   capture_output=True, text=True, encoding='utf-8', check=True)
#             print(f"✅ Calibre found: {result.stdout.strip()}")
#             return True
#         except (subprocess.CalledProcessError, FileNotFoundError):
#             print("❌ Calibre not found!")
#             print("Please install Calibre from: https://calibre-ebook.com/download")
#             return False

#     def _extract_cover_from_docx(self, docx_path: str) -> Optional[str]:
#         """
#         Extract cover image from DOCX file if exists
#         """
#         try:
#             # Method 1: Check for images using python-docx
#             doc = Document(docx_path)
            
#             # Check if document has any images
#             has_images = False
#             for rel in doc.part.rels.values():
#                 if "image" in str(rel.target_ref):
#                     has_images = True
#                     break
            
#             if not has_images:
#                 print("📄 No images found in DOCX document")
#                 return None

#             # Method 2: Extract using zipfile
#             with zipfile.ZipFile(docx_path, 'r') as docx_zip:
#                 image_files = [f for f in docx_zip.namelist() if f.startswith('word/media/')]
                
#                 if image_files:
#                     # Get the largest image as cover (usually the first one is cover)
#                     cover_image = image_files[0]
                    
#                     # Extract to temporary file
#                     temp_dir = Path("temp_covers")
#                     temp_dir.mkdir(exist_ok=True)
                    
#                     cover_path = temp_dir / "cover_image.jpg"
#                     with docx_zip.open(cover_image) as source, open(cover_path, 'wb') as target:
#                         target.write(source.read())
                    
#                     print(f"📸 Cover image found and extracted: {cover_path}")
#                     return str(cover_path)
            
#             print("📄 No cover image found in DOCX, using default formatting")
#             return None
            
#         except Exception as e:
#             print(f"⚠️ Error extracting cover image: {e}")
#             return None

#     def _create_pdf_footer(self) -> str:
#         """
#         Create PDF footer template with watermark and page numbers
#         """
#         return f'''<div style="width: 100%; font-size: 10pt; font-family: Arial, sans-serif;">
#     <div style="float: left; width: 50%; text-align: left;">
#         Page <span style="font-weight: bold;">$PAGE</span> of <span style="font-weight: bold;">$PAGES</span>
#     </div>
#     <div style="float: right; width: 50%; text-align: right; color: #666666; font-style: italic;">
#         {self.watermark_text}
#     </div>
# </div>'''

#     def _run_command_safe(self, cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
#         """
#         Safely run command with proper Unicode handling
#         """
#         try:
#             result = subprocess.run(
#                 cmd, 
#                 capture_output=True, 
#                 text=True, 
#                 encoding='utf-8',
#                 errors='ignore',
#                 timeout=timeout,
#                 creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
#             )
            
#             return {
#                 'success': result.returncode == 0,
#                 'stdout': result.stdout,
#                 'stderr': result.stderr,
#                 'returncode': result.returncode
#             }
            
#         except subprocess.TimeoutExpired:
#             return {
#                 'success': False,
#                 'stdout': '',
#                 'stderr': 'Conversion timed out',
#                 'returncode': -1
#             }
#         except Exception as e:
#             return {
#                 'success': False,
#                 'stdout': '',
#                 'stderr': str(e),
#                 'returncode': -1
#             }

#     def convert_document(self, input_path: str, output_path: str = None, 
#                         options: Dict[str, Any] = None) -> bool:
#         """
#         Universal document converter with cover detection and watermark
#         """
#         try:
#             # Validate input
#             if not os.path.exists(input_path):
#                 raise FileNotFoundError(f"Input file not found: {input_path}")
            
#             input_ext = Path(input_path).suffix.lower()[1:]
#             if input_ext not in self.supported_formats['input']:
#                 raise ValueError(f"Unsupported input format: {input_ext}")
            
#             # Set default output path
#             if output_path is None:
#                 if input_ext == 'docx':
#                     output_path = str(Path(input_path).with_suffix('.epub'))
#                 else:
#                     output_path = str(Path(input_path).with_suffix('.pdf'))
            
#             output_ext = Path(output_path).suffix.lower()[1:]
#             if output_ext not in self.supported_formats['output']:
#                 raise ValueError(f"Unsupported output format: {output_ext}")
            
#             # Extract cover image for DOCX to EPUB conversion
#             cover_image_path = None
#             if input_ext == 'docx' and output_ext == 'epub':
#                 cover_image_path = self._extract_cover_from_docx(input_path)
            
#             # Get format-specific options
#             format_options = self._get_format_options(
#                 input_ext, output_ext, options, cover_image_path
#             )
            
#             print(f"🔄 Converting: {Path(input_path).name} → {Path(output_path).name}")
#             if cover_image_path:
#                 print(f"📸 Using cover image: {Path(cover_image_path).name}")
            
#             # Execute conversion
#             cmd = ['ebook-convert', input_path, output_path]
#             cmd.extend(format_options)
            
#             print(f"🔧 Command: {' '.join(cmd[:5])}...")  # Show first 5 parts only
            
#             result = self._run_command_safe(cmd)
            
#             # Clean up temporary cover image
#             if cover_image_path and os.path.exists(cover_image_path):
#                 try:
#                     os.remove(cover_image_path)
#                     # Remove temp directory if empty
#                     temp_dir = Path("temp_covers")
#                     if temp_dir.exists() and not any(temp_dir.iterdir()):
#                         temp_dir.rmdir()
#                 except:
#                     pass
            
#             if result['success']:
#                 if os.path.exists(output_path):
#                     file_size = os.path.getsize(output_path)
#                     print(f"✅ Successfully created: {output_path} ({file_size:,} bytes)")
                    
#                     # Show what features were applied
#                     if output_ext == 'pdf':
#                         print(f"💧 Watermark added: '{self.watermark_text}'")
#                         print("🔢 Page numbers enabled in footer")
#                     elif output_ext == 'epub':
#                         print(f"💧 Watermark will be visible in EPUB reading apps")
#                         if cover_image_path:
#                             print("📸 Cover image embedded in EPUB")
                    
#                     return True
#                 else:
#                     print(f"❌ Output file was not created: {output_path}")
#                     return False
#             else:
#                 print(f"❌ Conversion failed with error: {result['stderr'][:200]}...")
#                 if "no such option" in result['stderr']:
#                     print("💡 Tip: Some options might not be supported for this conversion type")
#                 return False
                
#         except Exception as e:
#             print(f"❌ Error during conversion: {str(e)}")
#             return False

#     def _get_format_options(self, input_format: str, output_format: str, 
#                            user_options: Dict[str, Any] = None, 
#                            cover_image_path: str = None) -> List[str]:
#         """Get format-specific conversion options with CORRECT Calibre options"""
        
#         # Default options for all conversions - USING ONLY VALID CALIBRE OPTIONS
#         default_options = {
#             'epub_to_pdf': {
#                 '--paper-size': 'a4',
#                 '--pdf-page-margin-left': '40',
#                 '--pdf-page-margin-right': '40',
#                 '--pdf-page-margin-top': '40',
#                 '--pdf-page-margin-bottom': '40',
#                 '--pdf-default-font-size': '12',
#                 '--pdf-footer-template': self._create_pdf_footer(),
#             },
#             'docx_to_epub': {
#                 '--epub-flatten': None,
#                 '--epub-version': '3',
#                 '--chapter': '//h:h1',
#                 '--page-breaks-before': '//h:h1',
#                 '--insert-blank-line': None,
#                 '--change-justification': 'left',
#                 # EPUB footer is handled differently - we'll add watermark in content
#             },
#             'docx_to_pdf': {
#                 '--paper-size': 'a4',
#                 '--pdf-page-margin-left': '40',
#                 '--pdf-page-margin-right': '40',
#                 '--pdf-page-margin-top': '40',
#                 '--pdf-page-margin-bottom': '40',
#                 '--pdf-default-font-size': '11',
#                 '--pdf-footer-template': self._create_pdf_footer(),
#             },
#             'pdf_to_epub': {
#                 '--enable-heuristics': None,
#                 '--unwrap-lines': None,
#                 '--base-font-size': '12',
#                 # EPUB footer is handled differently
#             }
#         }
        
#         # Add cover image for DOCX to EPUB conversion
#         if input_format == 'docx' and output_format == 'epub' and cover_image_path:
#             default_options['docx_to_epub']['--cover'] = cover_image_path
        
#         # Get the appropriate option set
#         conversion_key = f"{input_format}_to_{output_format}"
#         options = default_options.get(conversion_key, {})
        
#         # Merge with user options
#         if user_options:
#             for key, value in user_options.items():
#                 if value is None:
#                     options[f"--{key}"] = None
#                 else:
#                     options[f"--{key}"] = str(value)
        
#         # Convert options to command line arguments
#         cmd_options = []
#         for key, value in options.items():
#             if value is None:
#                 cmd_options.append(key)
#             else:
#                 # Properly escape values with spaces and special characters
#                 if any(char in str(value) for char in [' ', '<', '>', '&']):
#                     # For HTML templates, we need to properly escape
#                     escaped_value = f'"{value}"'
#                     cmd_options.extend([key, escaped_value])
#                 else:
#                     cmd_options.extend([key, str(value)])
        
#         return cmd_options

#     def add_watermark_to_epub(self, epub_path: str) -> bool:
#         """
#         Add watermark to existing EPUB file by modifying its content
#         This is a post-processing step for EPUB files
#         """
#         try:
#             # This would require EPUB manipulation library
#             # For now, we'll just note that EPUB watermarking is complex
#             print(f"💡 EPUB watermarking requires manual content modification")
#             print(f"💡 Watermark '{self.watermark_text}' can be added during EPUB creation in source document")
#             return True
#         except Exception as e:
#             print(f"⚠️ Could not add watermark to EPUB: {e}")
#             return False

#     def batch_convert(self, input_folder: str, output_folder: str, 
#                      output_format: str, pattern: str = "*") -> Dict[str, bool]:
#         """
#         Convert multiple files in a folder
#         """
#         results = {}
#         input_path = Path(input_folder)
#         output_path = Path(output_folder)
        
#         output_path.mkdir(parents=True, exist_ok=True)
        
#         for file_path in input_path.glob(pattern):
#             if file_path.suffix[1:].lower() in self.supported_formats['input']:
#                 output_file = output_path / file_path.with_suffix(f'.{output_format}').name
#                 success = self.convert_document(str(file_path), str(output_file))
#                 results[file_path.name] = success
        
#         return results

#     def set_watermark(self, text: str):
#         """Change watermark text"""
#         self.watermark_text = text
#         print(f"💧 Watermark updated to: '{self.watermark_text}'")

# # Specialized Converters with Correct Options
# class CalibreSpecializedConverters:
#     def __init__(self, converter: CalibreDocumentConverter):
#         self.converter = converter
    
#     def docx_to_epub(self, docx_path: str, epub_path: str = None, 
#                      options: Dict[str, Any] = None) -> bool:
#         """Convert DOCX to EPUB with automatic cover detection"""
#         default_opts = {
#             'epub-flatten': None,
#             'epub-version': '3',
#             'chapter': '//h:h1',
#             'page-breaks-before': '//h:h1',
#             'insert-blank-line': None,
#             'change-justification': 'left'
#         }
#         if options:
#             default_opts.update(options)
        
#         success = self.converter.convert_document(docx_path, epub_path, default_opts)
        
#         # Add watermark note for EPUB
#         if success and epub_path:
#             self.converter.add_watermark_to_epub(epup_path)
        
#         return success
    
#     def docx_to_pdf(self, docx_path: str, pdf_path: str = None,
#                    options: Dict[str, Any] = None) -> bool:
#         """Convert DOCX to PDF with page numbers and watermark"""
#         default_opts = {
#             'paper-size': 'a4',
#             'margin-left': '40',
#             'margin-right': '40',
#             'margin-top': '40',
#             'margin-bottom': '40',
#             'pdf-default-font-size': '11',
#         }
#         if options:
#             default_opts.update(options)
        
#         return self.converter.convert_document(docx_path, pdf_path, default_opts)
    
#     def pdf_to_epub(self, pdf_path: str, epub_path: str = None,
#                    options: Dict[str, Any] = None) -> bool:
#         """Convert PDF to EPUB"""
#         default_opts = {
#             'enable-heuristics': None,
#             'unwrap-lines': None,
#             'base-font-size': '12',
#         }
#         if options:
#             default_opts.update(options)
        
#         success = self.converter.convert_document(pdf_path, epub_path, default_opts)
        
#         # Add watermark note for EPUB
#         if success and epub_path:
#             self.converter.add_watermark_to_epub(epup_path)
        
#         return success

# Test the fixed converter
# if __name__ == "__main__":
#     # Initialize converter
#     calibre = CalibreDocumentConverter()
#     specialized = CalibreSpecializedConverters(calibre)
    
#     print("📚 Fixed Calibre Converter Ready!")
#     print(f"💧 Default Watermark: '{calibre.watermark_text}'")
#     print("✅ Using only valid Calibre options")
    
#     # Test with your file
#     test_file = "ebook_final.docx"
#     if os.path.exists(test_file):
#         print(f"\n{'='*50}")
#         print(f"🔄 Testing DOCX to EPUB: {test_file}")
        
#         epub_success = specialized.docx_to_epub(test_file)
        
#         if epub_success:
#             epub_output = Path(test_file).with_suffix('.epub')
#             print(f"✅ EPUB created: {epup_output}")
#         else:
#             print("❌ EPUB conversion failed")
        
#         print(f"\n🔄 Testing DOCX to PDF: {test_file}")
#         pdf_success = specialized.docx_to_pdf(test_file)
        
#         if pdf_success:
#             pdf_output = Path(test_file).with_suffix('.pdf')
#             print(f"✅ PDF created: {pdf_output}")
#         else:
#             print("❌ PDF conversion failed")
            
#     else:
#         print(f"\n⚠️ Test file not found: {test_file}")
#         print("Please update the test_file path in the code.")
        
############################### same problem ######################################################

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
from docx import Document
import zipfile

class CalibreDocumentConverter:
    """
    Complete Document Conversion Suite using Calibre with Cover Image Detection and Watermark
    """
    
    def __init__(self):
        self.supported_formats = {
            'input': ['epub', 'pdf', 'docx', 'doc', 'mobi', 'azw3', 'txt', 'html'],
            'output': ['epub', 'pdf', 'docx', 'mobi', 'azw3', 'html']
        }
        self.watermark_text = "Readbucks"
        self.check_calibre_installation()
    
    def check_calibre_installation(self):
        """Check if Calibre is installed and accessible"""
        try:
            result = subprocess.run(['ebook-convert', '--version'], 
                                  capture_output=True, text=True, encoding='utf-8', check=True)
            print(f"✅ Calibre found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Calibre not found!")
            print("Please install Calibre from: https://calibre-ebook.com/download")
            return False

    def _extract_cover_from_docx(self, docx_path: str) -> Optional[str]:
        """
        Extract cover image from DOCX file if exists
        """
        try:
            # Method 1: Extract using zipfile
            with zipfile.ZipFile(docx_path, 'r') as docx_zip:
                image_files = [f for f in docx_zip.namelist() if f.startswith('word/media/')]
                
                if image_files:
                    # Get the first image as cover
                    cover_image = image_files[0]
                    
                    # Extract to temporary file
                    temp_dir = Path("temp_covers")
                    temp_dir.mkdir(exist_ok=True)
                    
                    # Keep original extension
                    cover_ext = Path(cover_image).suffix
                    cover_path = temp_dir / f"cover_image{cover_ext}"
                    
                    with docx_zip.open(cover_image) as source, open(cover_path, 'wb') as target:
                        target.write(source.read())
                    
                    print(f"📸 Cover image found and extracted: {cover_path}")
                    return str(cover_path)
            
            print("📄 No cover image found in DOCX")
            return None
            
        except Exception as e:
            print(f"⚠️ Error extracting cover image: {e}")
            return None

    def _create_pdf_footer(self) -> str:
        """
        Create PDF footer template with watermark and page numbers
        Using Calibre's correct template syntax
        """
        # Calibre uses {page} and {numPages} for page numbers
        return f'''<div style="width: 100%; font-size: 9pt; font-family: Arial, sans-serif; padding: 5px;">
                        <div style="float: left; width: 45%; text-align: left;">
                            Page <span style="font-weight: bold;">{{page}}</span> of <span style="font-weight: bold;">{{numPages}}</span>
                        </div>
                        <div style="float: right; width: 45%; text-align: right; color: #666666; font-style: italic;">
                            {self.watermark_text}
                        </div>
                        <div style="clear: both;"></div>
                    </div>'''

  
    def _run_command_safe(self, cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
        """
        Safely run command with proper Unicode handling
        """
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='ignore',
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Conversion timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }

    def convert_document(self, input_path: str, output_path: str = None, 
                        options: Dict[str, Any] = None) -> bool:
        """
        Universal document converter with cover detection and watermark
        """
        try:
            # Validate input
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            input_ext = Path(input_path).suffix.lower()[1:]
            if input_ext not in self.supported_formats['input']:
                raise ValueError(f"Unsupported input format: {input_ext}")
            
            # Set default output path
            if output_path is None:
                if input_ext == 'docx':
                    output_path = str(Path(input_path).with_suffix('.epub'))
                else:
                    output_path = str(Path(input_path).with_suffix('.pdf'))
            
            output_ext = Path(output_path).suffix.lower()[1:]
            if output_ext not in self.supported_formats['output']:
                raise ValueError(f"Unsupported output format: {output_ext}")
            
            # Extract cover image for DOCX to PDF conversion
            cover_image_path = None
            if input_ext == 'docx' and output_ext == 'pdf':
                cover_image_path = self._extract_cover_from_docx(input_path)
            
            # Get format-specific options
            format_options = self._get_format_options(
                input_ext, output_ext, options, cover_image_path
            )
            
            print(f"🔄 Converting: {Path(input_path).name} → {Path(output_path).name}")
            if cover_image_path:
                print(f"📸 Using cover image: {Path(cover_image_path).name}")
            
            # Execute conversion
            cmd = ['ebook-convert', input_path, output_path]
            cmd.extend(format_options)
            
            # Print debug info
            print(f"🔧 Options applied:")
            for i in range(0, len(format_options), 2):
                if i+1 < len(format_options):
                    opt = format_options[i]
                    val = format_options[i+1]
                    if 'footer' in opt or 'header' in opt:
                        print(f"   {opt}: [HTML Template]")
                    else:
                        print(f"   {opt}: {val}")
            
            result = self._run_command_safe(cmd)
            
            # Clean up temporary cover image
            if cover_image_path and os.path.exists(cover_image_path):
                try:
                    os.remove(cover_image_path)
                    # Remove temp directory if empty
                    temp_dir = Path("temp_covers")
                    if temp_dir.exists() and not any(temp_dir.iterdir()):
                        temp_dir.rmdir()
                except:
                    pass
            
            if result['success']:
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"✅ Successfully created: {output_path} ({file_size:,} bytes)")
                    
                    # Show what features were applied
                    if output_ext == 'pdf':
                        print(f"💧 Watermark added: '{self.watermark_text}'")
                        print("🔢 Page numbers enabled in footer (using {page} and {numPages})")
                        if cover_image_path:
                            print("📸 Cover image added to PDF")
                    
                    return True
                else:
                    print(f"❌ Output file was not created: {output_path}")
                    return False
            else:
                error_msg = result['stderr'][:500] if result['stderr'] else 'Unknown error'
                print(f"❌ Conversion failed with error: {error_msg}")
                return False
                
        except Exception as e:
            print(f"❌ Error during conversion: {str(e)}")
            return False

    def _get_format_options(self, input_format: str, output_format: str, 
                           user_options: Dict[str, Any] = None, 
                           cover_image_path: str = None) -> List[str]:
        """Get format-specific conversion options with CORRECT Calibre options"""
        
        # Default options for all conversions
        default_options = {
            'epub_to_pdf': {
                '--paper-size': 'a4',
                '--pdf-page-margin-left': '40',
                '--pdf-page-margin-right': '40',
                '--pdf-page-margin-top': '40',
                '--pdf-page-margin-bottom': '40',
                '--pdf-default-font-size': '12',
                '--pdf-footer-template': self._create_pdf_footer(),
                # '--pdf-header-template': self._create_pdf_header(),
            },
            'docx_to_epub': {
                '--epub-flatten': None,
                '--epub-version': '3',
                '--chapter': '//h:h1',
                '--page-breaks-before': '//h:h1',
                '--insert-blank-line': None,
                '--change-justification': 'left',
            },
            'docx_to_pdf': {
                '--paper-size': 'a4',
                '--pdf-page-margin-left': '40',
                '--pdf-page-margin-right': '40',
                '--pdf-page-margin-top': '40',
                '--pdf-page-margin-bottom': '40',
                '--pdf-default-font-size': '11',
                '--pdf-footer-template': self._create_pdf_footer(),
                '--pdf-header-template': self._create_pdf_header(),
                '--preserve-cover-aspect-ratio': None,
            },
            'pdf_to_epub': {
                '--enable-heuristics': None,
                '--unwrap-lines': None,
                '--base-font-size': '12',
            }
        }
        
        # Add cover image for DOCX to PDF conversion
        if input_format == 'docx' and output_format == 'pdf' and cover_image_path:
            default_options['docx_to_pdf']['--cover'] = cover_image_path
        
        # Get the appropriate option set
        conversion_key = f"{input_format}_to_{output_format}"
        options = default_options.get(conversion_key, {})
        
        # Merge with user options
        if user_options:
            for key, value in user_options.items():
                if value is None:
                    options[f"--{key}"] = None
                else:
                    options[f"--{key}"] = str(value)
        
        # Convert options to command line arguments
        cmd_options = []
        for key, value in options.items():
            if value is None:
                cmd_options.append(key)
            else:
                # For HTML templates, we need to properly escape and quote
                if any(char in str(value) for char in [' ', '<', '>', '{', '}']):
                    # Remove newlines and extra spaces from HTML templates
                    cleaned_value = ' '.join(str(value).split())
                    cmd_options.extend([key, f'"{cleaned_value}"'])
                else:
                    cmd_options.extend([key, str(value)])
        
        return cmd_options

    def batch_convert(self, input_folder: str, output_folder: str, 
                     output_format: str, pattern: str = "*") -> Dict[str, bool]:
        """
        Convert multiple files in a folder
        """
        results = {}
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in input_path.glob(pattern):
            if file_path.suffix[1:].lower() in self.supported_formats['input']:
                output_file = output_path / file_path.with_suffix(f'.{output_format}').name
                success = self.convert_document(str(file_path), str(output_file))
                results[file_path.name] = success
        
        return results

    def set_watermark(self, text: str):
        """Change watermark text"""
        self.watermark_text = text
        print(f"💧 Watermark updated to: '{self.watermark_text}'")

# Specialized Converters with Enhanced PDF Features
class CalibreSpecializedConverters:
    def __init__(self, converter: CalibreDocumentConverter):
        self.converter = converter
    
    def docx_to_epub(self, docx_path: str, epub_path: str = None, 
                     options: Dict[str, Any] = None) -> bool:
        """Convert DOCX to EPUB with automatic cover detection"""
        default_opts = {
            'epub-flatten': None,
            'epub-version': '3',
            'chapter': '//h:h1',
            'page-breaks-before': '//h:h1',
            'insert-blank-line': None,
            'change-justification': 'left'
        }
        if options:
            default_opts.update(options)
        
        return self.converter.convert_document(docx_path, epub_path, default_opts)
    
    def docx_to_pdf(self, docx_path: str, pdf_path: str = None,
                   options: Dict[str, Any] = None) -> bool:
        """Convert DOCX to PDF with page numbers, watermark and cover"""
        default_opts = {
            'paper-size': 'a4',
            'margin-left': '40',
            'margin-right': '40',
            'margin-top': '40',
            'margin-bottom': '40',
            'pdf-default-font-size': '11',
            'preserve-cover-aspect-ratio': None,
        }
        if options:
            default_opts.update(options)
        
        return self.converter.convert_document(docx_path, pdf_path, default_opts)
    
    def pdf_to_epub(self, pdf_path: str, epub_path: str = None,
                   options: Dict[str, Any] = None) -> bool:
        """Convert PDF to EPUB"""
        default_opts = {
            'enable-heuristics': None,
            'unwrap-lines': None,
            'base-font-size': '12',
        }
        if options:
            default_opts.update(options)
        
        return self.converter.convert_document(pdf_path, epub_path, default_opts)

# Test the enhanced converter
# if __name__ == "__main__":
#     # Initialize converter
#     calibre = CalibreDocumentConverter()
#     specialized = CalibreSpecializedConverters(calibre)
    
#     print("📚 Enhanced PDF Converter Ready!")
#     print(f"💧 Default Watermark: '{calibre.watermark_text}'")
#     print("🔢 Using correct page number variables: {page} and {numPages}")
    
#     # Test with your file
#     test_file = "ebook_final.docx"
#     if os.path.exists(test_file):
#         print(f"\n{'='*50}")
#         print(f"🔄 Testing DOCX to PDF with enhanced features: {test_file}")
        
#         pdf_success = specialized.docx_to_pdf(test_file)
        
#         if pdf_success:
#             pdf_output = Path(test_file).with_suffix('.pdf')
#             print(f"✅ PDF created with features:")
#             print(f"   • Page numbers (Page X of Y)")
#             print(f"   • Watermark: '{calibre.watermark_text}'")
#             print(f"   • Cover image (if available in DOCX)")
#             print(f"   • Professional header and footer")
#         else:
#             print("❌ PDF conversion failed")
            
#     else:
#         print(f"\n⚠️ Test file not found: {test_file}")
#         print("Please update the test_file path in the code.")


   
        