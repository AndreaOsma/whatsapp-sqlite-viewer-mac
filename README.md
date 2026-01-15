# macOS WhatsApp Desktop Viewer

A Python-based utility to parse the WhatsApp Desktop SQLite database (`ChatStorage.sqlite`) on macOS and generate a standalone, searchable HTML interface for message recovery and archiving.

## Overview

WhatsApp Desktop for macOS stores message history in a local SQLite database. This tool extracts that data—including metadata for images, videos, and voice notes—and renders it into a high-performance HTML5 interface.

## Features

- **Performance**: Optimized for large databases (tested with 85,000+ messages).
- **Search Engine**: Instant filtering of contacts and group sessions via JavaScript.
- **Media Integration**: Automatic linking of local media using relative paths.
- **Smart Navigation**: Includes "Scroll to Bottom" and "Scroll to Top" functionality.
- **Theming**: Integrated toggle for Dark and Light modes.
- **Privacy**: Local processing. No data leaves the local environment.

## Directory Structure

Maintain the following structure for correct media rendering:

```text
.
├── whatsapp_viewer.py     # Main execution script
├── ChatStorage.sqlite     # WhatsApp database file
├── Media/                 # Local copy of WhatsApp Media folder
└── .gitignore             # Git exclusion rules

```

## Usage

1. **Database Acquisition**:
   The database is typically located at:
   `~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite`

2. **Media Setup**:
   Copy the `Media` folder from the same path into the project root to enable attachment visualization within the viewer.

3. **Execution**:
   Run the script using Python 3:
   ```bash
   python3 whatsapp_viewer.py

4. Access:
   The script generates an `index.html` file in the same directory. Open this file in any modern web browser. Chrome or Brave are recommended for handling large log files and optimal rendering.

## Requirements

- Python 3.x
- No external dependencies (uses standard library: `sqlite3`, `os`, `datetime`).

## License

This project is licensed under the MIT License.
