#!/usr/bin/env python3
"""
Code to PDF Converter with C++ Syntax Highlighting
Supports Catppuccin (mocha | latte) and Kanagawa (wave | lotus | dragon) themes
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
from reportlab.platypus.flowables import Flowable

# =============================
# Theme Palette Definitions
# =============================

THEMES = {
    "catppuccin-mocha": {
        "bg": "#1e1e2e",
        "bg_page": "#11111b",  # crust for page background
        "border": "#313244",
        "linenr": "#6c7086",
        "text": "#cdd6f4",
        "text_dim": "#bac2de",  # subtext1 for headers
        "comment": "#6c7086",
        "keyword": "#cba6f7",
        "function": "#89b4fa",
        "string": "#a6e3a1",
        "number": "#fab387",
        "preproc": "#f5c2e7",
        "type": "#f9e2af",
        "variable": "#cdd6f4",
        "property": "#89dceb",
        "operator": "#94e2d5",
        "punctuation": "#bac2de",
    },
    "catppuccin-latte": {
        "bg": "#eff1f5",
        "bg_page": "#e6e9ef",  # mantle for page background
        "border": "#ccd0da",
        "linenr": "#8c8fa1",
        "text": "#4c4f69",
        "text_dim": "#5c5f77",  # subtext1 for headers
        "comment": "#9ca0b0",
        "keyword": "#8839ef",
        "function": "#1e66f5",
        "string": "#40a02b",
        "number": "#fe640b",
        "preproc": "#ea76cb",
        "type": "#df8e1d",
        "variable": "#4c4f69",
        "property": "#04a5e5",
        "operator": "#179299",
        "punctuation": "#5c5f77",
    },
    "kanagawa-wave": {
        "bg": "#1F1F28",  # sumiInk3
        "bg_page": "#16161D",  # sumiInk0 for page
        "border": "#54546D",  # sumiInk6
        "linenr": "#54546D",
        "text": "#DCD7BA",  # fujiWhite
        "text_dim": "#C8C093",  # oldWhite
        "comment": "#727169",  # fujiGray
        "keyword": "#957FB8",  # oniViolet
        "function": "#7E9CD8",  # crystalBlue
        "string": "#98BB6C",  # springGreen
        "number": "#FFA066",  # surimiOrange
        "preproc": "#E46876",  # waveRed
        "type": "#E6C384",  # carpYellow
        "variable": "#DCD7BA",
        "property": "#7FB4CA",  # springBlue
        "operator": "#C0A36E",  # boatYellow2
        "punctuation": "#C8C093",
    },
    "kanagawa-dragon": {
        "bg": "#181616",  # dragonBlack3
        "bg_page": "#0d0c0c",  # dragonBlack0
        "border": "#625e5a",  # dragonBlack6
        "linenr": "#625e5a",
        "text": "#c5c9c5",  # dragonWhite
        "text_dim": "#a6a69c",  # dragonGray
        "comment": "#7a8382",  # dragonGray3
        "keyword": "#8992a7",  # dragonViolet
        "function": "#8ba4b0",  # dragonBlue2
        "string": "#87a987",  # dragonGreen
        "number": "#b98d7b",  # dragonOrange2
        "preproc": "#c4746e",  # dragonRed
        "type": "#c4b28a",  # dragonYellow
        "variable": "#c5c9c5",
        "property": "#8ea4a2",  # dragonAqua
        "operator": "#b6927b",  # dragonOrange
        "punctuation": "#9e9b93",  # dragonGray2
    },
    "kanagawa-lotus": {
        "bg": "#f2ecbc",  # lotusWhite1
        "bg_page": "#d5cea3",  # lotusWhite0
        "border": "#b5cbd2",  # lotusGray2
        "linenr": "#b5cbd2",
        "text": "#545464",  # lotusInk1
        "text_dim": "#43436c",  # lotusInk2
        "comment": "#9fb5c9",  # lotusGray
        "keyword": "#8a6596",  # lotusViolet3
        "function": "#6693bf",  # lotusBlue3
        "string": "#6f894e",  # lotusGreen3
        "number": "#e98a00",  # lotusOrange
        "preproc": "#c84053",  # lotusRed3
        "type": "#836f4a",  # lotusYellow4
        "variable": "#545464",
        "property": "#4e8ca2",  # lotusAqua2
        "operator": "#8a6596",
        "punctuation": "#625e5a",
    },
}

# Default theme
SELECTED_THEME = "kanagawa-wave"


class SyntaxHighlightedCode(Flowable):
    """Custom flowable for syntax-highlighted C++ code"""

    def __init__(
        self,
        code,
        width,
        language="cpp",
        start_line=1,
        is_first_chunk=True,
        is_last_chunk=True,
        in_block_comment=False,
    ):
        Flowable.__init__(self)
        self.code = code
        self.width = width
        self.language = language
        self.start_line = start_line
        self.is_first_chunk = is_first_chunk
        self.is_last_chunk = is_last_chunk
        self.lines = code.split("\n")
        self.line_height = 11
        self.font_size = 8
        self.in_block_comment = in_block_comment

    def wrap(self, availWidth, availHeight):
        padding_top = 12
        padding_bottom = 12
        total_height = len(self.lines) * self.line_height + padding_top + padding_bottom
        return (self.width, total_height)

    def draw(self):
        theme = THEMES[SELECTED_THEME]
        canvas = self.canv

        padding_top = 10 if self.is_first_chunk else 5
        padding_bottom = 10 if self.is_last_chunk else 5
        total_height = len(self.lines) * self.line_height + padding_top + padding_bottom

        canvas.saveState()

        # Background
        canvas.setFillColor(HexColor(theme["bg"]))
        canvas.rect(0, 0, self.width, total_height, fill=1, stroke=0)

        # Borders
        canvas.setStrokeColor(HexColor(theme["border"]))
        canvas.setLineWidth(1)
        canvas.line(0, 0, 0, total_height)
        canvas.line(self.width, 0, self.width, total_height)

        if self.is_first_chunk:
            canvas.line(0, total_height, self.width, total_height)
        if self.is_last_chunk:
            canvas.line(0, 0, self.width, 0)

        # Draw code
        y_position = len(self.lines) * self.line_height + padding_top - 5
        in_comment = self.in_block_comment

        for line_num, line in enumerate(self.lines, self.start_line):
            # Line numbers
            canvas.setFillColor(HexColor(theme["linenr"]))
            canvas.setFont("Courier", self.font_size - 1)
            canvas.drawString(5, y_position, f"{line_num:3d}")

            x_offset = 35
            in_comment = self.draw_highlighted_line(
                canvas, line, x_offset, y_position, in_comment
            )
            y_position -= self.line_height

        canvas.restoreState()

    def draw_highlighted_line(self, canvas, line, x, y, in_block_comment):
        """Draw a line with C++ syntax highlighting"""
        theme = THEMES[SELECTED_THEME]

        # C++ keywords
        keywords = {
            "if",
            "else",
            "while",
            "for",
            "do",
            "switch",
            "case",
            "default",
            "break",
            "continue",
            "return",
            "goto",
            "const",
            "static",
            "extern",
            "auto",
            "register",
            "volatile",
            "mutable",
            "inline",
            "virtual",
            "explicit",
            "friend",
            "typedef",
            "public",
            "private",
            "protected",
            "class",
            "struct",
            "union",
            "enum",
            "namespace",
            "using",
            "template",
            "typename",
            "try",
            "catch",
            "throw",
            "new",
            "delete",
            "this",
            "const_cast",
            "dynamic_cast",
            "reinterpret_cast",
            "static_cast",
            "true",
            "false",
            "nullptr",
        }

        # C++ types
        types = {
            "int",
            "float",
            "double",
            "char",
            "bool",
            "void",
            "long",
            "short",
            "unsigned",
            "signed",
            "wchar_t",
            "char16_t",
            "char32_t",
            "size_t",
            "ptrdiff_t",
            "nullptr_t",
            "int8_t",
            "int16_t",
            "int32_t",
            "int64_t",
            "uint8_t",
            "uint16_t",
            "uint32_t",
            "uint64_t",
            "string",
            "vector",
            "map",
            "set",
            "list",
            "deque",
            "array",
            "pair",
            "tuple",
            "unique_ptr",
            "shared_ptr",
            "weak_ptr",
        }

        preprocessor_pattern = r"^\s*#"

        # Handle block comments
        if in_block_comment:
            end_pos = line.find("*/")
            if end_pos != -1:
                comment_part = line[: end_pos + 2]
                rest_of_line = line[end_pos + 2 :]

                canvas.setFillColor(HexColor(theme["comment"]))
                canvas.setFont("Courier-Oblique", self.font_size)
                canvas.drawString(x, y, comment_part)

                width = canvas.stringWidth(
                    comment_part, "Courier-Oblique", self.font_size
                )
                new_x = x + width

                if rest_of_line:
                    self.draw_highlighted_line(canvas, rest_of_line, new_x, y, False)

                return False
            else:
                canvas.setFillColor(HexColor(theme["comment"]))
                canvas.setFont("Courier-Oblique", self.font_size)
                canvas.drawString(x, y, line)
                return True

        # Check for block comment start
        block_comment_start = line.find("/*")
        if block_comment_start != -1:
            block_comment_end = line.find("*/", block_comment_start + 2)

            if block_comment_end != -1:
                before = line[:block_comment_start]
                comment = line[block_comment_start : block_comment_end + 2]
                after = line[block_comment_end + 2 :]

                if before:
                    x = self.draw_code_tokens(canvas, before, x, y, keywords, types)

                canvas.setFillColor(HexColor(theme["comment"]))
                canvas.setFont("Courier-Oblique", self.font_size)
                canvas.drawString(x, y, comment)
                width = canvas.stringWidth(comment, "Courier-Oblique", self.font_size)
                x += width

                if after:
                    self.draw_code_tokens(canvas, after, x, y, keywords, types)

                return False
            else:
                before = line[:block_comment_start]
                comment = line[block_comment_start:]

                if before:
                    x = self.draw_code_tokens(canvas, before, x, y, keywords, types)

                canvas.setFillColor(HexColor(theme["comment"]))
                canvas.setFont("Courier-Oblique", self.font_size)
                canvas.drawString(x, y, comment)

                return True

        # Preprocessor directive
        if re.match(preprocessor_pattern, line):
            canvas.setFillColor(HexColor(theme["preproc"]))
            canvas.setFont("Courier-Bold", self.font_size)
            canvas.drawString(x, y, line)
            return False

        # Single-line comment
        if "//" in line:
            comment_start = line.find("//")
            before = line[:comment_start]
            comment = line[comment_start:]

            if before:
                x = self.draw_code_tokens(canvas, before, x, y, keywords, types)

            canvas.setFillColor(HexColor(theme["comment"]))
            canvas.setFont("Courier-Oblique", self.font_size)
            canvas.drawString(x, y, comment)
            return False

        # Regular code
        self.draw_code_tokens(canvas, line, x, y, keywords, types)
        return False

    def draw_code_tokens(self, canvas, line, x, y, keywords, types):
        """Tokenize and highlight C++ code"""
        theme = THEMES[SELECTED_THEME]

        # Enhanced tokenizer for C++
        token_pattern = r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'|0x[0-9a-fA-F]+|[0-9]+\.?[0-9]*[fFlLuU]*|[A-Za-z_]\w*|::|->|\+\+|--|<<|>>|<=|>=|==|!=|&&|\|\||[+\-*/%=<>!&|^~?:]|\(|\)|\[|\]|\{|\}|;|,|\.|#|\s+'
        tokens = re.findall(token_pattern, line)

        current_x = x
        prev_token = None

        for i, token in enumerate(tokens):
            next_token = tokens[i + 1] if i + 1 < len(tokens) else None

            # Strings
            if (token.startswith('"') and token.endswith('"')) or (
                token.startswith("'") and token.endswith("'")
            ):
                canvas.setFillColor(HexColor(theme["string"]))
                canvas.setFont("Courier", self.font_size)

            # Keywords
            elif token in keywords:
                canvas.setFillColor(HexColor(theme["keyword"]))
                canvas.setFont("Courier-Bold", self.font_size)

            # Types
            elif token in types:
                canvas.setFillColor(HexColor(theme["type"]))
                canvas.setFont("Courier", self.font_size)

            # Function calls
            elif (
                re.match(r"^[A-Za-z_]\w*$", token)
                and next_token
                and next_token.strip() == "("
            ):
                canvas.setFillColor(HexColor(theme["function"]))
                canvas.setFont("Courier", self.font_size)

            # Member access
            elif prev_token in [".", "->"] and re.match(r"^[A-Za-z_]\w*$", token):
                canvas.setFillColor(HexColor(theme["property"]))
                canvas.setFont("Courier", self.font_size)

            # Namespace/class access
            elif prev_token == "::" and re.match(r"^[A-Za-z_]\w*$", token):
                canvas.setFillColor(HexColor(theme["type"]))
                canvas.setFont("Courier", self.font_size)

            # Pointers and references
            elif token in ["*", "&", "->", "::"]:
                canvas.setFillColor(HexColor(theme["operator"]))
                canvas.setFont("Courier-Bold", self.font_size)

            # Operators
            elif token in [
                "+",
                "-",
                "/",
                "%",
                "=",
                "<",
                ">",
                "!",
                "|",
                "^",
                "~",
                "?",
                "++",
                "--",
                "<<",
                ">>",
                "<=",
                ">=",
                "==",
                "!=",
                "&&",
                "||",
            ]:
                canvas.setFillColor(HexColor(theme["operator"]))
                canvas.setFont("Courier", self.font_size)

            # Numbers
            elif re.match(r"^(0x[0-9a-fA-F]+|\d+\.?\d*[fFlLuU]*)$", token):
                canvas.setFillColor(HexColor(theme["number"]))
                canvas.setFont("Courier", self.font_size)

            # Punctuation
            elif token in ["(", ")", "[", "]", "{", "}", ";", ",", "#"]:
                canvas.setFillColor(HexColor(theme["punctuation"]))
                canvas.setFont("Courier", self.font_size)

            # Whitespace
            elif token.isspace():
                width = canvas.stringWidth(token, "Courier", self.font_size)
                current_x += width
                prev_token = token
                continue

            # Variables and identifiers
            else:
                canvas.setFillColor(HexColor(theme["variable"]))
                canvas.setFont("Courier", self.font_size)

            canvas.drawString(current_x, y, token)
            width = canvas.stringWidth(token, "Courier", self.font_size)
            current_x += width
            prev_token = token.strip()

        return current_x


def find_cpp_project_files(start_path):
    """Find all C++ related files in the project"""
    cpp_extensions = {".cpp", ".cc", ".cxx", ".c++", ".h", ".hpp", ".hxx", ".h++", ".c"}
    project_files = []
    start_dir = os.path.dirname(os.path.abspath(start_path))

    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d not in ["build", "bin", "obj", "Debug", "Release"]
        ]

        for file in files:
            if Path(file).suffix in cpp_extensions:
                full_path = os.path.join(root, file)
                project_files.append(full_path)

    def sort_key(filepath):
        ext = Path(filepath).suffix
        return (0, filepath) if ext in {".h", ".hpp", ".hxx", ".h++"} else (1, filepath)

    project_files.sort(key=sort_key)
    return project_files


def create_pdf(
    code_file,
    output_pdf=None,
    student_name="",
    assignment_title="",
    course="",
    include_project=True,
):
    """Convert C++ code file(s) to a themed PDF with syntax highlighting"""

    if output_pdf is None:
        base_name = os.path.splitext(os.path.basename(code_file))[0]
        output_pdf = f"{base_name}_submission.pdf"

    if include_project:
        files_to_include = find_cpp_project_files(code_file)
        if not files_to_include:
            files_to_include = [code_file]
        print(f"Found {len(files_to_include)} C++ files in project:")
        for f in files_to_include:
            print(f"  - {os.path.basename(f)}")
    else:
        files_to_include = [code_file]

    theme = THEMES[SELECTED_THEME]

    # Custom canvas to set page background
    def add_page_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(HexColor(theme["bg_page"]))
        canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
        canvas.restoreState()

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "CustomHeader",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=HexColor(theme["text"]),
        spaceAfter=12,
        alignment=1,
    )

    file_header_style = ParagraphStyle(
        "FileHeader",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=HexColor(theme["function"]),
        spaceAfter=8,
        spaceBefore=15,
        backColor=HexColor(theme["bg"]),
        borderColor=HexColor(theme["border"]),
        borderWidth=1,
        borderPadding=5,
    )

    info_style = ParagraphStyle(
        "InfoStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor(theme["text_dim"]),
        spaceAfter=6,
    )

    if assignment_title:
        elements.append(Paragraph(assignment_title, header_style))
        elements.append(Spacer(1, 0.2 * inch))

    if student_name:
        elements.append(Paragraph(f"<b>Student:</b> {student_name}", info_style))

    if course:
        elements.append(Paragraph(f"<b>Course:</b> {course}", info_style))

    elements.append(
        Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", info_style)
    )
    elements.append(
        Paragraph(f"<b>Files Included:</b> {len(files_to_include)}", info_style)
    )
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>Project Files:</b>", info_style))
    for f in files_to_include:
        elements.append(Paragraph(f"&nbsp;&nbsp;ΓÇó {os.path.basename(f)}", info_style))

    elements.append(Spacer(1, 0.3 * inch))

    for i, filepath in enumerate(files_to_include):
        if i > 0:
            elements.append(PageBreak())

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code_content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            continue

        relative_path = os.path.relpath(filepath, os.path.dirname(code_file))
        elements.append(Paragraph(f"File: {relative_path}", file_header_style))
        elements.append(Spacer(1, 0.1 * inch))

        max_lines_per_chunk = 55
        lines = code_content.split("\n")
        num_chunks = (len(lines) + max_lines_per_chunk - 1) // max_lines_per_chunk

        if len(lines) > max_lines_per_chunk:
            in_block_comment = False
            for chunk_idx in range(num_chunks):
                chunk_start = chunk_idx * max_lines_per_chunk
                chunk_end = min(chunk_start + max_lines_per_chunk, len(lines))
                chunk_code = "\n".join(lines[chunk_start:chunk_end])

                is_first = chunk_idx == 0
                is_last = chunk_idx == num_chunks - 1

                code_flowable = SyntaxHighlightedCode(
                    chunk_code,
                    6.5 * inch,
                    start_line=chunk_start + 1,
                    is_first_chunk=is_first,
                    is_last_chunk=is_last,
                    in_block_comment=in_block_comment,
                )
                elements.append(code_flowable)

                for line in lines[chunk_start:chunk_end]:
                    if "/*" in line and "*/" not in line:
                        in_block_comment = True
                    elif "*/" in line:
                        in_block_comment = False
        else:
            code_flowable = SyntaxHighlightedCode(code_content, 6.5 * inch)
            elements.append(code_flowable)
        elements.append(Spacer(1, 0.2 * inch))

    try:
        doc.build(
            elements, onFirstPage=add_page_background, onLaterPages=add_page_background
        )
        print(f"\nΓ£ô PDF created successfully: {output_pdf}")
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function to handle command line arguments"""

    if len(sys.argv) < 2:
        print("C++ Code to PDF Converter with Themed Syntax Highlighting")
        print("=" * 65)
        print("\nUsage: python code_to_pdf.py <code_file> [options]")
        print("\nOptions:")
        print("  -o, --output <file>       Output PDF filename")
        print("  -n, --name <name>         Student name")
        print("  -t, --title <title>       Assignment title")
        print("  -c, --course <course>     Course name/number")
        print("  --theme <theme>           Color theme (default: catppuccin-latte)")
        print(
            "                            Options: catppuccin-mocha, catppuccin-latte,"
        )
        print(
            "                                     kanagawa-wave, kanagawa-dragon, kanagawa-lotus"
        )
        print("  --no-project              Only convert the specified file")
        print("\nExample:")
        print("  python code_to_pdf.py main.cpp -n 'John Doe' -t 'Assignment 1' \\")
        print("         -c 'CS101' --theme kanagawa-wave")
        print("\nBy default, finds and includes all .cpp, .h, .hpp files")
        print("in the same directory and subdirectories.")
        sys.exit(1)

    code_file = sys.argv[1]
    output_pdf = None
    student_name = ""
    assignment_title = ""
    course = ""
    include_project = True
    global SELECTED_THEME

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--theme":
            theme = sys.argv[i + 1].lower()
            if theme not in THEMES:
                print(f"Unknown theme: {theme}")
                print(f"Available themes: {', '.join(THEMES.keys())}")
                sys.exit(1)
            SELECTED_THEME = theme
            i += 2
            continue

        if sys.argv[i] in ["-o", "--output"]:
            output_pdf = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] in ["-n", "--name"]:
            student_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] in ["-t", "--title"]:
            assignment_title = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] in ["-c", "--course"]:
            course = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--no-project":
            include_project = False
            i += 1
        else:
            print(f"Unknown option: {sys.argv[i]}")
            sys.exit(1)

    create_pdf(
        code_file, output_pdf, student_name, assignment_title, course, include_project
    )


if __name__ == "__main__":
    main()
