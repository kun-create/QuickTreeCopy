Quick Tree Copy
=============

QuickTreeCopy is a lightweight Tkinter application that generates and copies a directory tree structure in plain-text form—ideal for quickly feeding your file hierarchy into AI tools or documentation.

Features
--------

*   Browse and select any local directory.
*   Generate an interactive tree view of files and folders.
*   Render a styled text representation (Classic, Modern, Minimal).
*   Copy the generated tree text to clipboard in one click.
*   Responsive UI with dark theme (using `sv_ttk`).
*   Background scanning via threads to avoid freezing the UI.

Prerequisites
-------------

*   Python 3.8 or higher
*   [sv\_ttk](https://pypi.org/project/sv-ttk/) (for dark/light theming)
*   [tkfontawesome](https://pypi.org/project/tkfontawesome/) (for SVG icons)
*   A working Tkinter installation (usually bundled with Python)

Installation
------------

1.  Clone this repository:
    
        git clone https://github.com/kun-create/QuickTreeCopy.git
        cd QuickTreeCopy
    
2.  Create and activate a virtual environment (optional but recommended):
    
        python3 -m venv .venv
        source .venv/bin/activate      # macOS/Linux
        .venv\Scripts\activate         # Windows
    
3.  Install required packages:
    
        pip install sv-ttk tkfontawesome
    

Usage
-----

1.  Run the application:
    
        python main.py
    
2.  In the UI:
    *   Click **Browse** to select a folder.
    *   Click **Generate** to scan and display the folder structure.
    *   Toggle **Output Style** between Classic, Modern, or Minimal to see different text formats.
    *   Click **Copy** to copy the rendered tree text to your clipboard.
3.  Paste the copied text into any AI prompt, documentation file, or code comment.

Example
-------

1\. Select a directory `~/projects/example/`. 2. Generate output in “Modern” style:

    example/
    ├─ src/
    │  ├─ main.py
    │  ├─ utils.py
    │  └─ components/
    │     └─ button.py
    ├─ README.md
    └─ requirements.txt

3\. Copy and paste this text into your AI tool to analyze or document your project structure.

Customization
-------------

*   Change the dark/light theme by modifying `sv_ttk.set_theme("dark")` to `"light"`.
*   Adjust the font or row-height calculation by editing `self.tv_font` and `compute_needed_rowheight` in `main.py`.
*   Add or replace FontAwesome icons by updating the calls in `load_icons()`.

Troubleshooting
---------------

*   **Tkinter ImportError**: Ensure Python was installed with Tk support. On Linux, install `python3-tk` (e.g., `sudo apt install python3-tk`).
*   **SVG Icons Not Showing**: Verify that `tkfontawesome` is installed and up to date.
*   **Performance Issues on Large Folders**: The app uses a background thread to scan—wait for completion. For extremely large trees, consider excluding deep or system folders.

License
-------

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.