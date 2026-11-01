"""Build and execute the fully expanded academic report generator for Modular-Agent.
Target: Minimum of 50 to 60 pages in Microsoft Word.
Preserves all preliminary matter, exact tables, figures, screenshots, and references.
"""

import sys
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path("C:/Users/LENOVO/.gemini/antigravity/scratch/modular_agent/scripts")
sys.path.insert(0, str(SCRIPTS_DIR))

from report_ch1_ch2 import get_ch1_ch2_code
from report_ch3 import get_ch3_code
from report_ch4_ch5 import get_ch4_ch5_code

TARGET_GEN = SCRIPTS_DIR / "generate_extended_project_report_docx.py"

print("[INFO] Reading original template...")
with open(TARGET_GEN, "r", encoding="utf-8") as f:
    orig_lines = f.readlines()

preamble = "".join(orig_lines[:456])

# Find line where Appendix A begins
app_idx = -1
for idx, line in enumerate(orig_lines):
    if 'chapter_title("APPENDIX A' in line:
        app_idx = idx
        break

if app_idx == -1:
    raise ValueError("Could not find APPENDIX A in original generator")

epilogue = "".join(orig_lines[app_idx - 1:])

ch1_ch2 = get_ch1_ch2_code()
ch3 = get_ch3_code()
ch4_ch5 = get_ch4_ch5_code()

full_content = preamble + ch1_ch2 + ch3 + ch4_ch5 + epilogue

with open(TARGET_GEN, "w", encoding="utf-8") as f:
    f.write(full_content)

print(f"[OK] Successfully assembled {TARGET_GEN} ({len(full_content)} chars)")
