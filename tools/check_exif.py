from PIL import Image, ExifTags
import sys

if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    print("Usage: python check_exif.py <path_to_image>")
    sys.exit(1)

try:
    img = Image.open(file_path)
    exif_data = img.getexif()

    if not exif_data:
        print("No EXIF data found.")
    else:
        print(f"EXIF data for {file_path}:")
        for tag_id in exif_data:
            # Get the tag name, use the ID if not found
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)
            
            # Decode bytes if possible for better readability
            if isinstance(data, bytes):
                try:
                    # Try decoding as utf-16le (Windows XP tags)
                    decoded = data.decode('utf-16le').rstrip('\x00')
                    print(f"{tag}: {decoded} (decoded from utf-16le)")
                except:
                    try:
                        decoded = data.decode('utf-8')
                        print(f"{tag}: {decoded}")
                    except:
                        print(f"{tag}: {data}")
            else:
                print(f"{tag}: {data}")

except FileNotFoundError:
    print(f"File not found: {file_path}")
except Exception as e:
    print(f"Error reading EXIF: {e}")
