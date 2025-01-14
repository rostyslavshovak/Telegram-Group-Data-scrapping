import argparse
import asyncio
import os
import sys
from datetime import datetime
from io import BytesIO

import pandas as pd
from telethon import TelegramClient, errors
from telethon.tl.types import InputMessagesFilterPhotos
from tqdm import tqdm

import easyocr
from PIL import Image


def parse_arguments():
    """
    Parse command-line arguments for the Telegram Group Image OCR Processor.
    """
    parser = argparse.ArgumentParser(description="Telegram Group Image OCR Processor")
    parser.add_argument(
        "--api_id",
        type=int,
        required=False,
        help="Telegram API ID. Alternatively, set TELEGRAM_API_ID environment variable.",
    )
    parser.add_argument(
        "--api_hash",
        type=str,
        required=False,
        help="Telegram API Hash. Alternatively, set TELEGRAM_API_HASH environment variable.",
    )
    parser.add_argument(
        "--group",
        type=str,
        required=True,
        help="Telegram group username or ID to connect to.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=6,
        help="Number of images to retrieve from the group (default: 6).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="parsed_data.xlsx",
        help="Path to the output XLSX file (default: parsed_data.xlsx).",
    )
    parser.add_argument(
        "--session",
        type=str,
        default="session",
        help="Telethon session name (default: session).",
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["uk", "ru"],
        help="Languages for the OCR engine (default: ['uk', 'ru']).",
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU for OCR if available (default: CPU).",
    )
    return parser.parse_args()

async def fetch_images(client: TelegramClient, group, limit: int):
    """
    Fetch up to `limit` image messages from the specified group.
    Args:
        client (TelegramClient): The Telethon client.
        group: The group entity (username or ID).
        limit (int): Number of images to fetch.
    Returns:
        list: A list of Telethon message objects containing images.
    """
    images = []
    try:
        # Here limit=None is used for iter_messages, but we break once we have enough images
        async for message in client.iter_messages(group, limit=None, filter=InputMessagesFilterPhotos):
            if message.photo:
                images.append(message)
                if len(images) >= limit:
                    break
    except errors.FloodWaitError as e:
        print(f"Flood wait error. Need to wait for {e.seconds} seconds.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while fetching images: {e}")
        sys.exit(1)
    return images


def perform_ocr(reader, image_bytes: bytes) -> str:
    """
    Perform OCR on the given image bytes using the provided EasyOCR reader.
    Args:
        reader: An instance of easyocr.Reader
        image_bytes (bytes): Bytes of the image.
    Returns:
        str: Extracted text from the image (or empty string if OCR fails).
    """
    try:
        image = Image.open(BytesIO(image_bytes)).convert('RGB')
        #Save to a temporary BytesIO object in a format compatible with easyocr
        with BytesIO() as output:
            image.save(output, format="JPEG")
            temp_bytes = output.getvalue()
        result = reader.readtext(temp_bytes, detail=0, paragraph=True)
        return " ".join(result)
    except Exception as e:
        print(f"OCR failed for image: {e}")
        return ""

def append_to_excel(output_path: str, data: list):
    """
    Append the collected data to the specified Excel file. If the file doesn't exist, create it. Otherwise, append to existing data.

    Args:
        output_path (str): Path to the output XLSX file.
        data (list): A list of dictionaries, each representing a row of data to append.
    """
    df = pd.DataFrame(data)
    if not os.path.exists(output_path):
        df.to_excel(output_path, index=False)
    else:
        existing_df = pd.read_excel(output_path)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_excel(output_path, index=False)

async def main():
    args = parse_arguments()

    api_id = args.api_id or os.getenv("TELEGRAM_API_ID")
    api_hash = args.api_hash or os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        print("API ID and API Hash are required. Provide them via arguments or set TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables.")
        sys.exit(1)

    #Initialize Telethon client
    client = TelegramClient(args.session, api_id, api_hash)

    #start the Telethon client
    try:
        await client.start()
    except errors.ApiIdInvalidError:
        print("Invalid API ID or API Hash.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start Telegram client: {e}")
        sys.exit(1)

    try:
        group_entity = await client.get_entity(args.group)
    except errors.UsernameNotOccupiedError:
        print(f"The group '{args.group}' does not exist.")
        await client.disconnect()
        sys.exit(1)
    except errors.ChannelPrivateError:
        print(f"The group '{args.group}' is private or you don't have access.")
        await client.disconnect()
        sys.exit(1)
    except Exception as e:
        print(f"Failed to get the group entity: {e}")
        await client.disconnect()
        sys.exit(1)

    print(f"Connected to group: {getattr(group_entity, 'title', args.group)}")

    images = await fetch_images(client, group_entity, args.limit)

    if not images:
        print("No images found in the specified group.")
        await client.disconnect()
        sys.exit(0)

    print(f"Fetched {len(images)} image(s) from the group.")

    reader = easyocr.Reader(args.languages, gpu=args.gpu)

    data_to_append = []

    print("Started OCR processing.")
    for message in tqdm(images, desc="Processing images"):
        try:
            image_bytes = await message.download_media(bytes)

            if not image_bytes:
                print(f"Failed to download image from message ID {message.id}")
                continue

            text = perform_ocr(reader, image_bytes)

            if hasattr(group_entity, "username") and group_entity.username:
                message_link = f"https://t.me/{group_entity.username}/{message.id}"
            else:
                message_link = ""

            data_to_append.append(
                {
                    "Message ID": message.id,
                    "Date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "Image Link": message_link,
                    "Extracted Text": text,
                }
            )

        except Exception as e:
            print(f"Error processing message ID {message.id}: {e}")
            continue

    # Append data to Excel
    if data_to_append:
        append_to_excel(args.output, data_to_append)
        print(f"Data successfully appended to {args.output}")
    else:
        print("No data to append to Excel.")

    # Disconnect the client
    await client.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting...")
