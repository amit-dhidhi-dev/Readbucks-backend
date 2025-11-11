import os


def create_pdf_footer() -> str:
        """Create PDF footer template with watermark and page numbers."""
        return f'''<div style="width: 100%; font-size: 10pt; font-family: Arial, sans-serif;">
                    <div style="float: left; width: 50%; text-align: left;">
                        Page <span style="font-weight: bold;">_PAGENUM_</span>
                    </div>
                    <div style="float: right; width: 50%; text-align: right; color: #666666; font-style: italic;">
                        {os.environ.get("WEBSITE_NAME",'Readbucks')}
                    </div>
                </div>'''

        