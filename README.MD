# Telegram Group Image OCR Processor (for private or open groups)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Telegram OCR Processor](#telegram-ocr-processor)


## Overview

The **Telegram Group Image OCR Processor** is a Python-based tool to automate the extraction of text from images shared within a Telegram group. 
Combining Telegram's API and Optical Character Recognition (OCR) tools, this project retrieves images, processes them to extract relevant text, and compiles the results into Excel file.

## Features

### Telegram OCR Processor

- **Connect to Telegram Groups**: Connects to specified Telegram groups using the Telethon library.
- **Image Retrieval**: Fetch images from the group, with the ability to specify the number of images and resume processing from a specific message ID, if errors occured during script running.
- **OCR Processing**: Utilize EasyOCR to extract text from images, supporting Ukrainian and Russian languages (you may change it).
- **Data Storage**: Compile extracted text along with metadata (Message ID, Image Link) into a single Excel (`.xlsx`) file, appending new data without overwriting existing entries.
- **No Local Image Storage**: Process images in-memory to conserve disk space, making the tool scalable for large volumes of images.
- **Progress Visualization**: Integrated `tqdm` for real-time progress bars during processing.
- **Flexible Configuration**: Customize runtime arguments such as API credentials, group identification, output paths, and OCR settings.

## Installation

### Prerequisites

- **Python 3.7 or higher**: Ensure Python is installed on your system.

### Clone the Repository

```bash
git clone https://github.com/rostyslavshovak/Telegram-Group-Data-scrapping.git
cd telegram-ocr-processor
