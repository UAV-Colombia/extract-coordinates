from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import csv


def get_exif(filename):
    """
    Returns a dictionary with the EXIF metadata of an image.
    """
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def get_geotagging(exif):
    """
    Returns a dictionary with the geotagging data decoded from the EXIF tags.
    """
    if not exif:
        raise ValueError("No EXIF metadata found")

    geotagging = {}
    for idx, tag in TAGS.items():
        if tag == "GPSInfo":
            if idx not in exif:
                raise ValueError("No EXIF geotagging found")
            for key, val in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]

    return geotagging


def convert(tude):
    """
    Converts GPS coordinates to decimal degrees.
    """
    return sum(float(x) / 60**n for n, x in enumerate(tude))


def extract_coordinates_from_images(path):
    """
    Extracts all coordinates from images in the specified path, including subfolders.
    """
    coordinates = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if (
                file.endswith(".jpg")
                or file.endswith(".jpeg")
                or file.endswith(".png")
                or file.endswith(".JPG")
                or file.endswith(".JPEG")
                or file.endswith(".PNG")
            ):
                try:
                    filename = os.path.join(root, file)
                    exif_data = get_exif(filename)
                    geotagging = get_geotagging(exif_data)
                    if "GPSLatitude" in geotagging and "GPSLongitude" in geotagging:
                        latitude = convert(geotagging["GPSLatitude"])
                        longitude = convert(geotagging["GPSLongitude"])
                        folder_name = os.path.relpath(
                            root, path
                        )  # Get the relative subfolder path
                        coordinates.append((folder_name, file, latitude, longitude))
                except (ValueError, AttributeError, KeyError, TypeError):
                    pass

    return coordinates


# Prompt the user to enter the path
path = input("Enter the path to extract coordinates from: ")
coordinates = extract_coordinates_from_images(path)

# Save coordinates to a CSV file
output_file = "coordinates.csv"
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["subfolder", "file_name", "latitude", "longitude"])
    writer.writerows(coordinates)

print(f"Coordinates saved to {output_file}.")
