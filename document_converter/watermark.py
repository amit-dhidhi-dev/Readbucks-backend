import os
import shutil
from zipfile import ZipFile
from pathlib import Path

def add_epub_watermark(epub_path: str, watermark_text="Readbucks"):
    """Inject CSS watermark into EPUB after creation."""
    tmp_dir = "temp_epub"
    
    # Clean up old temp directory if exists
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    
    os.makedirs(tmp_dir, exist_ok=True)
    
    # Extract EPUB
    with ZipFile(epub_path, "r") as zin:
        zin.extractall(tmp_dir)
    
    # Find OPF file first to determine content directory
    content_opf = None
    content_dir = None
    
    for root, dirs, files in os.walk(tmp_dir):
        for f_name in files:
            if f_name.endswith(".opf"):
                content_opf = os.path.join(root, f_name)
                content_dir = root
                break
        if content_opf:
            break
    
    if not content_opf:
        print("❌ Error: .opf file not found!")
        return
    

   # Create watermark CSS in the same directory as OPF
    css_path = os.path.join(content_dir, "watermark.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(f"""
                    body::after {{
                        content: "{watermark_text}";
                        position: fixed;
                        bottom: 1%;
                        right: 1%;
                        font-size: 11pt;
                        color: rgba(200, 200, 200, 0.7);   
                        z-index: -1;
                        pointer-events: none;
                    }}
                """)
    
    # Update OPF manifest
    with open(content_opf, "r", encoding="utf-8") as f:
        opf_data = f.read()
    
    if "watermark.css" not in opf_data:
        # Add CSS to manifest (NOT to spine - spine is only for content)
        opf_data = opf_data.replace(
            "</manifest>", 
            '  <item id="watermark-css" href="watermark.css" media-type="text/css"/>\n</manifest>'
        )
        
        with open(content_opf, "w", encoding="utf-8") as f:
            f.write(opf_data)
    
    # Link CSS to all XHTML/HTML files
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith((".xhtml", ".html")):
                html_path = os.path.join(root, file)
                
                with open(html_path, "r", encoding="utf-8") as f:
                    html_data = f.read()
                
                # Skip if watermark CSS already linked
                if "watermark.css" in html_data:
                    continue
                
                # Calculate relative path from HTML file to CSS
                html_dir = os.path.dirname(html_path)
                rel_css_path = os.path.relpath(css_path, html_dir).replace("\\", "/")
                
                # Add CSS link in <head>
                css_link = f'<link rel="stylesheet" type="text/css" href="{rel_css_path}"/>'
                
                if "<head>" in html_data:
                    html_data = html_data.replace("<head>", f"<head>\n  {css_link}")
                elif "<html" in html_data:
                    # If no <head>, add one
                    html_data = html_data.replace("<html", f"<html>\n<head>\n  {css_link}\n</head>", 1)
                
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_data)
    
    # Re-zip to EPUB (maintain proper EPUB structure)
    new_epub = epub_path.replace(".epub", "_watermarked.epub")
    
    with ZipFile(new_epub, "w") as zout:
        # First, add mimetype (uncompressed, first file)
        mimetype_path = os.path.join(tmp_dir, "mimetype")
        if os.path.exists(mimetype_path):
            zout.write(mimetype_path, "mimetype", compress_type=0)
        
        # Then add all other files
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                if file == "mimetype":
                    continue  # Already added
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, tmp_dir)
                zout.write(full_path, rel_path)
    
    # Cleanup
    shutil.rmtree(tmp_dir)
    
    print(f"✅ Watermarked EPUB saved at: {new_epub}")
    return new_epub


# Usage example
if __name__ == "__main__":
    # Replace with your EPUB file path
    epub_file = "./documents/ebook_final.epub"
    add_epub_watermark(epub_file, watermark_text="Readbucks")