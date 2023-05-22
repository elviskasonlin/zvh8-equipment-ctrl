
menu_texts = {
    "menu_title_text_main_menu": "MAIN MENU",
    "menu_title_text_settings": "[2] SETTINGS",
    "menu_body_text_main_menu": """[1] Initialise Connected Devices\n[2] Settings\n[3] Start Data Acquisition\n[0] Quit\n\nEnter your choice below""",
    "menu_body_text_settings": """[1] Change Save Folder Name (Default: "results" in ./)\n[2] Change Save File Name (Default: logfile.csv)\n[3] Change Arduino Port (Default: None)\n[4] Change R&S Instrument Port (Default: TCPIP0::172.16.10.10::INSTR)\n[0] Exit\n\nEnter your choice below"""
}
def get_menu_text(menuName: str):
    """
    Returns a beautified standardised menu text as stored in the dictionary "menu_texts" in gui.py
    Args:
        menuName: (str) Available: "main_menu", "settings_menu"

    Returns:
        output: (str) Returns the menu with a line sep., title, line sep., and body text

    """
    # Text formatting
    # Yanked from https://stackoverflow.com/questions/8924173/how-do-i-print-bold-text-in-python
    class TypeFormat:
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        DARKCYAN = '\033[36m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

    title_text = str()
    body_text = str()

    match menuName:
        case "main_menu":
            title_text = menu_texts["menu_title_text_main_menu"]
            body_text = menu_texts["menu_body_text_main_menu"]
        case "settings_menu":
            title_text = menu_texts["menu_title_text_settings"]
            body_text = menu_texts["menu_body_text_settings"]
        case _:
            title_text = "ERROR"
            body_text = "Menu function error in gui.py"

    title_text.format(TypeFormat.BOLD, TypeFormat.END).center(get_longest_width(text=body_text))
    body_text.format(TypeFormat.BOLD, TypeFormat.END, TypeFormat.PURPLE)
    line_separator = create_separator(char="-", length=get_longest_width(text=body_text), includeNewLine=True)

    output = line_separator + title_text + line_separator + body_text
    return output

# Find longest width from a string
def get_longest_width(text: str):
    lines = text.split('\n')
    width = max(map(len, lines))
    return width

# Creates a long separator
def create_separator(char: str, length: int, includeNewLine: bool):
    output = None
    if (includeNewLine == True):
        output = "\n" + (char * length) + "\n"
    else:
        output = char * length
    return output