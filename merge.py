import os, logging

import logconf
from weasyprint import HTML, CSS
from pathlib import Path
import glob

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logconf.loggerLevel)

from book import bookId

if (not os.path.exists(os.path.join("output", bookId))):
    logger.error("Output folder does not exist. Please run the download.py script first.")
    exit()

PAGE_SIZES = {
    'A4': (210, 297),
    'A5': (148, 210),
    'Letter': (215.9, 279.4),
    'Legal': (215.9, 355.6),
    'Tabloid': (279.4, 431.8),
}

def merge_htmls_to_pdf(output_dir="output", book_id=None, page_size=None, margin='0'):
    """
    Merge HTML files from a book directory into a single PDF.
    
    Args:
        output_dir: Base output directory (default: "output")
        book_id: Book ID to process. If None, will process first found book.
        page_size: Page size - 'A4', 'A5', 'Letter', etc, or tuple (width, height) in mm.
                   If None (default), uses the HTML content size (595px × 841px = A4)
        margin: Page margin (default: '0' for exact content match)
    """
    output_path = Path(output_dir)
    
    # Find book directory (output/some_dir/book_id/)
    if book_id:
        book_dir = output_path / book_id
    else:
        # Get first subdirectory
        subdirs = [d for d in output_path.iterdir() if d.is_dir()]
        if not subdirs:
            print(f"No subdirectories found in {output_dir}")
            return
        book_dir = subdirs[0]
        book_id = book_dir.name
    
    if not book_dir.exists():
        print(f"Directory not found: {book_dir}")
        return
    
    print(f"Processing book: {book_id}")
    print(f"Book directory: {book_dir}")
    
    # Find all HTML files
    html_files = sorted(glob.glob(str(book_dir / "*.html")))
    
    if not html_files:
        print(f"No HTML files found in {book_dir}")
        return
    
    print(f"Found {len(html_files)} HTML files")
    
    if page_size is None:
        # Use HTML content size: 595px × 841px
        # Convert pixels to mm at 96 DPI (CSS reference pixel)
        # 595px * 25.4mm/inch / 96 DPI ≈ 157.4mm
        # 841px * 25.4mm/inch / 96 DPI ≈ 222.5mm
        # OR use the CSS pixel dimensions directly
        size_str = "595px 841px"
    elif isinstance(page_size, str):
        if page_size in PAGE_SIZES:
            width, height = PAGE_SIZES[page_size]
            size_str = f"{width}mm {height}mm"
        else:
            size_str = page_size
    else:
        width, height = page_size
        size_str = f"{width}mm {height}mm"
    
    # Create CSS for page size and margins
    page_css = CSS(string=f'''
        @page {{
            size: {size_str};
            margin: {margin};
        }}
        html, body {{
            margin: 0;
            padding: 0;
        }}
    ''')
    
    print(f"Page size: {size_str}")
    print(f"Margins: {margin}")
    
    pdf_path = output_path / f"{book_id}.pdf"
    
    documents = []
    
    for html_file in html_files:
        print(f"Processing: {Path(html_file).name}")
        html = HTML(filename=html_file, base_url=str(book_dir))
        documents.append(html)
    
    # Render all documents and combine
    if documents:
        print("Rendering PDF...")
        
        all_pages = []
        for doc in documents:
            rendered = doc.render(stylesheets=[page_css])
            all_pages.extend(rendered.pages)
        
        first_render = documents[0].render(stylesheets=[page_css])
        first_render.pages = all_pages
        first_render.write_pdf(pdf_path)
        
        print(f"\nPDF created successfully: {pdf_path}")
        print(f"Total pages: {len(all_pages)}")
    
if __name__ == "__main__":
    merge_htmls_to_pdf(output_dir="output", book_id=bookId)
