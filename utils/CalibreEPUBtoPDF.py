import subprocess
import os
import json
from pathlib import Path
from typing import Dict, Any

class CalibreEPUBtoPDF:
    """
    Advanced EPUB to PDF converter using Calibre
    """
    
    def __init__(self):
        self.check_calibre_installation()
    
    def check_calibre_installation(self):
        """Check if Calibre is installed and accessible"""
        try:
            result = subprocess.run(['ebook-convert', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Calibre found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Calibre not found!")
            print("Please install Calibre from: https://calibre-ebook.com/download")
            print("Or install via:")
            print("  - Windows: Download from website")
            print("  - macOS: brew install calibre")
            print("  - Linux: sudo apt-get install calibre")
            return False
    
    def convert_epub_to_pdf(self, epub_path: str, pdf_path: str = None, 
                           options: Dict[str, Any] = None) -> bool:
        """
        Convert EPUB to PDF with customizable options
        
        Args:
            epub_path: Input EPUB file path
            pdf_path: Output PDF file path (optional)
            options: Conversion options dictionary
        
        Returns:
            bool: Success status
        """
        try:
            # Validate input
            if not os.path.exists(epub_path):
                raise FileNotFoundError(f"EPUB file not found: {epub_path}")
            
            # Set default output path
            if pdf_path is None:
                pdf_path = str(Path(epub_path).with_suffix('.pdf'))
            
            # Default options
            default_options = {
                'paper_size': 'a4',
                'margin_left': '40',
                'margin_right': '40',
                'margin_top': '40',
                'margin_bottom': '40',
                'font_family': 'Times New Roman',
                'font_size': '12',
                'header': None,
                'footer': None
            }
            
            # Merge with user options
            if options:
                default_options.update(options)
            
            # Build command
            cmd = ['ebook-convert', epub_path, pdf_path]
            
            # Add options to command
            conversion_options = {
                '--paper-size': default_options['paper_size'],
                '--pdf-page-margin-left': default_options['margin_left'],
                '--pdf-page-margin-right': default_options['margin_right'],
                '--pdf-page-margin-top': default_options['margin_top'],
                '--pdf-page-margin-bottom': default_options['margin_bottom'],
                '--pdf-default-font-size': default_options['font_size'],
                '--pdf-header-template': default_options['header'],
                '--pdf-footer-template': default_options['footer']
            }
            
            for key, value in conversion_options.items():
                if value:  # Only add if value is not None
                    cmd.extend([key, str(value)])
            
            # Add font family if specified
            if default_options['font_family']:
                cmd.extend(['--embed-font-family', default_options['font_family']])
            
            print(f"🔄 Converting: {Path(epub_path).name} → {Path(pdf_path).name}")
            print(f"⚙️  Options: {default_options}")
            
            # Execute conversion
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                file_size = os.path.getsize(pdf_path)
                print(f"✅ Successfully created: {pdf_path} ({file_size:,} bytes)")
                return True
            else:
                print(f"❌ Conversion failed with error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Conversion timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Error during conversion: {str(e)}")
            return False
    
    def get_pdf_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        Return predefined conversion presets
        """
        return {
            'standard': {
                'paper_size': 'a4',
                'margin_left': '40',
                'margin_right': '40',
                'margin_top': '40',
                'margin_bottom': '40',
                'font_family': 'Times New Roman',
                'font_size': '12'
            },
            'compact': {
                'paper_size': 'a5',
                'margin_left': '20',
                'margin_right': '20',
                'margin_top': '20',
                'margin_bottom': '20',
                'font_family': 'Arial',
                'font_size': '10'
            },
            'large_print': {
                'paper_size': 'a4',
                'margin_left': '30',
                'margin_right': '30',
                'margin_top': '30',
                'margin_bottom': '30',
                'font_family': 'Georgia',
                'font_size': '16'
            },
            'academic': {
                'paper_size': 'a4',
                'margin_left': '50',
                'margin_right': '50',
                'margin_top': '50',
                'margin_bottom': '50',
                'font_family': 'Times New Roman',
                'font_size': '11',
                'header': '<div style="text-align: center;">$TITLE</div>',
                'footer': '<div style="text-align: center;">Page $PAGE of $PAGES</div>'
            }
        }
        
        
                