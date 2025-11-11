from utils.r2_utils import download_pdf_from_r2
from utils.cleanup_utils import cleanup_file
# from services.toc_extractor import extract_toc_and_chapters
# from database.connection import books_collection
from bson import ObjectId
from utils.chapter_extractor import extract_toc_and_chapters


async def process_book():
    pdf_path = None
    print('inside process ')
    try:
        # Step 1. Download PDF from R2
        # pdf_path = download_pdf_from_r2(book_data["book_content_url"])
        pdf_path = download_pdf_from_r2('https://4e2de902c9c96022ca5a34538b962d83.r2.cloudflarestorage.com/ebookstorage/documents/final_with_pageno_20251107_000802_40227273.pdf')
        print('pdf download path',pdf_path)
        # Step 2. Extract TOC
        toc_data = extract_toc_and_chapters(pdf_path)
        print('extracted toc or chapters',toc_data)
        # Step 3. Save metadata + TOC in MongoDB
        # new_book = {
        #     "title": book_data["title"],
        #     "author": book_data["author"],
        #     "book_content_url": book_data["book_content_url"],
        #     "toc": toc_data,
        #     "ai_processed": False
        # }

        # result = await books_collection.insert_one(new_book)
        # new_book["_id"] = str(result.inserted_id)
        # return new_book
        return {'work done'}

    finally:
        if pdf_path:
            # cleanup_file(pdf_path)
            print('done')
