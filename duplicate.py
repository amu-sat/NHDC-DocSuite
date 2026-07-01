from pathlib import Path
import hashlib
import fitz


# ---------------------------------------------------------

def sha256(pdf):

    h = hashlib.sha256()

    with open(pdf, "rb") as f:

        while True:

            block = f.read(1024 * 1024)

            if not block:
                break

            h.update(block)

    return h.hexdigest()


# ---------------------------------------------------------

def page_count(pdf):

    try:

        doc = fitz.open(pdf)

        pages = len(doc)

        doc.close()

        return pages

    except:

        return -1


# ---------------------------------------------------------

def scan_duplicates(root_folder):
    """
    Scan ALL extracted folders.

    Duplicate criteria

        File Size
        +
        Page Count
        +
        SHA256
    """

    root = Path(root_folder)

    pdfs = sorted(
        root.rglob("*.pdf"),
        key=lambda x: x.name.lower()
    )

    duplicates = []

    checked = set()

    total = len(pdfs)

    for i in range(total):

        pdf1 = pdfs[i]

        if pdf1 in checked:
            continue

        size1 = pdf1.stat().st_size

        pages1 = page_count(pdf1)

        hash1 = None

        for pdf2 in pdfs[i + 1:]:

            if pdf2 in checked:
                continue

            if pdf2.stat().st_size != size1:
                continue

            if page_count(pdf2) != pages1:
                continue

            if hash1 is None:
                hash1 = sha256(pdf1)

            if sha256(pdf2) == hash1:

                duplicates.append(
                    (
                        pdf1,
                        pdf2
                    )
                )

                checked.add(pdf2)

    return duplicates


# ---------------------------------------------------------

def apply_choice(
    duplicates,
    choice,
):

    """
    choice

    0 Keep Original

    1 Keep Duplicate

    2 Keep Both
    """

    if choice == 2:
        return

    for original, duplicate in duplicates:

        try:

            if choice == 0:

                duplicate.unlink(
                    missing_ok=True
                )

            elif choice == 1:

                original.unlink(
                    missing_ok=True
                )

        except Exception:

            pass