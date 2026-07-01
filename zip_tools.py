from pathlib import Path
import zipfile


def extract_all_zips(
    input_folder,
    output_folder,
    logger=print,
):
    """
    Extract every ZIP file into its own folder.

    Example

    Input

        ABC.zip
        XYZ.zip

    Output

        ABC/
        XYZ/
    """

    input_folder = Path(input_folder)

    output_folder = Path(output_folder)

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    zip_files = sorted(
        input_folder.rglob("*.zip"),
        key=lambda x: x.name.lower()
    )

    if len(zip_files) == 0:

        logger("No ZIP files found.")

        return

    logger("")
    logger(f"{len(zip_files)} ZIP file(s) found.")
    logger("")

    for index, zip_file in enumerate(zip_files, start=1):

        logger(
            f"[{index}/{len(zip_files)}] {zip_file.name}"
        )

        destination = output_folder / zip_file.stem

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            with zipfile.ZipFile(
                zip_file,
                "r"
            ) as archive:

                archive.extractall(
                    destination
                )

            logger(
                f"    Extracted → {destination.name}"
            )

        except zipfile.BadZipFile:

            logger(
                "    Invalid ZIP archive."
            )

        except Exception as e:

            logger(
                f"    {e}"
            )

    logger("")
    logger("ZIP extraction completed.")