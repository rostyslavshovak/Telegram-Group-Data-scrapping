# Telegram Group Image OCR Processor (for private or open groups)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Telegram OCR Processor](#telegram-ocr-processor)


## Overview

This script connects to a Telegram group, retrieves images, performs OCR to extract text, and saves the results into an Excel file.

## Features

### Telegram OCR Processor

- **Connect to Telegram Groups**: Connects to specified Telegram groups using the Telethon library.
- **Image Retrieval**: Fetch images from the group, with the ability to specify the number of images and resume processing from a specific message ID, if errors occured during script running.
- **OCR Processing**: Utilize EasyOCR to extract text from images, supporting Ukrainian and Russian languages (you may change it).
- **Data Storage**: Compile extracted text along with metadata (Message ID, Image Link) into a single Excel (`.xlsx`) file, appending new data without overwriting existing entries.
- **No Local Image Storage**: Process images in-memory to conserve disk space, making the tool scalable for large volumes of images.
- **Progress Visualization**: Integrated `tqdm` for real-time progress bars during processing.
- **Flexible Configuration**: Customize runtime arguments such as API credentials, group identification, output paths, and OCR settings.

## Technologies Used
- **Telethon**: For interacting with the Telegram API.
- **EasyOCR**: For Optical Character Recognition.
- **Pandas**: For data manipulation and Excel file handling.
- **Tqdm**: For progress visualization.
- **OpenPyXL**: For reading and writing Excel files.
- **Pillow (PIL)**: For image processing.

## Installation

### Clone the Repository

```bash
git clone https://github.com/rostyslavshovak/Telegram-Group-Data-scrapping.git
cd telegram-ocr-processor
```

### Example: Run the Telegram OCR Processor

```bash
python name.py --api_id API_ID --api_hash "API_HASH" --group_name sdksfsasdc --limit 1500 --output result.xlsx --language ru uk --start_from_id 712
```

