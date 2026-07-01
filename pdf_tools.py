from pathlib import Path
import math
import fitz

MAX_SIZE_MB = 20
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def natural_sort(files):
    return sorted(files, key=lambda x: x.name.lower())


def file_size_bytes(pdf):
    return pdf.stat().st_size


def file_size_mb(pdf):
    return file_size_bytes(pdf) / (1024 * 1024)


# ---------------------------------------------------------
# Compression
# ---------------------------------------------------------

def compress_pdf(pdf, logger):

    size = file_size_mb(pdf)

    if size <= MAX_SIZE_MB:

        logger(
            f"    Size : {size:.2f} MB (No compression required)"
        )

        return pdf

    logger(
        f"    Compressing ({size:.2f} MB)..."
    )

    temp = pdf.with_suffix(".tmp.pdf")

    doc = fitz.open(pdf)

    doc.save(
        temp,
        garbage=4,
        clean=True,
        deflate=True,
    )

    doc.close()

    if temp.exists():

        new_size = file_size_mb(temp)

        if new_size < size:

            pdf.unlink()

            temp.rename(pdf)

            logger(
                f"    New Size : {new_size:.2f} MB"
            )

        else:

            temp.unlink()

            logger(
                "    Compression not effective."
            )

    return pdf


# ---------------------------------------------------------
# Split
# ---------------------------------------------------------

def split_pdf(pdf, logger):

    size = file_size_bytes(pdf)

    if size <= MAX_SIZE_BYTES:

        return

    logger("    Splitting PDF...")

    doc = fitz.open(pdf)

    pages = len(doc)

    average = size / pages

    pages_per_part = max(
        1,
        int(MAX_SIZE_BYTES / average)
    )

    total_parts = math.ceil(
        pages / pages_per_part
    )

    for part in range(total_parts):

        start = part * pages_per_part

        end = min(
            pages,
            start + pages_per_part
        )

        out = fitz.open()

        out.insert_pdf(
            doc,
            from_page=start,
            to_page=end - 1
        )

        filename = pdf.with_name(
            f"{pdf.stem}_Part{part+1}.pdf"
        )

        out.save(
            filename,
            garbage=4,
            deflate=True,
        )

        out.close()

        logger(
            f"    Created {filename.name}"
        )

    doc.close()

    pdf.unlink()

    logger(
        "    Original merged PDF removed."
    )


# ---------------------------------------------------------
# Merge
# ---------------------------------------------------------

def merge_folder(
    folder,
    final_folder,
    logger,
):

    folder = Path(folder)

    pdfs = [
        pdf
        for pdf in natural_sort(
            folder.rglob("*.pdf")
        )
        if pdf.is_file()
    ]

    if not pdfs:

        logger(
            "    No PDFs found."
        )

        return None

    final_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = final_folder / f"{folder.name}.pdf"

    if len(pdfs) == 1:

        logger(
            "    Single PDF. Copying..."
        )

        doc = fitz.open(
            pdfs[0]
        )

        doc.save(output)

        doc.close()

        return output

    logger(
        f"    Merging {len(pdfs)} PDFs"
    )

    merged = fitz.open()

    for pdf in pdfs:

        logger(
            f"      + {pdf.name}"
        )

        src = fitz.open(pdf)

        merged.insert_pdf(src)

        src.close()

    merged.save(
        output,
        garbage=4,
        deflate=True,
    )

    merged.close()

    logger(
        f"    Saved : {output.name}"
    )

    return output
# ---------------------------------------------------------
# Main Processing
# ---------------------------------------------------------

def process_pdfs(
    root_folder,
    compress=True,
    split=True,
    logger=print,
    progress=None,
    status=None,
):

    root = Path(root_folder)

    final_folder = root / "Final PDFs"

    final_folder.mkdir(
        exist_ok=True
    )

    folders = sorted(
        [
            folder
            for folder in root.iterdir()
            if folder.is_dir()
            and folder.name != "Final PDFs"
        ],
        key=lambda x: x.name.lower(),
    )

    total = len(folders)

    if total == 0:

        logger("No folders found.")

        return

    for index, folder in enumerate(folders, start=1):

        if status:

            status(
                f"Processing {folder.name} ({index}/{total})"
            )

        if progress:

            # Keep worker's initial progress (40%)
            percent = 35 + int(
                (index / total) * 65
            )

            progress(percent)

        logger("")
        logger("=" * 60)
        logger(
            f"Folder {index} of {total}"
        )
        logger(folder.name)
        logger("=" * 60)

        merged = merge_folder(
            folder,
            final_folder,
            logger,
        )

        if merged is None:
            continue

        if compress:

            compress_pdf(
                merged,
                logger,
            )

        if split:

            split_pdf(
                merged,
                logger,
            )

    logger("")
    logger("=" * 60)
    logger("All folders processed successfully.")
    logger("=" * 60)