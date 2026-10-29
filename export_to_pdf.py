#!/usr/bin/env python3
"""
Automated PDF exporter using Apple Pages on macOS.
Converts DCDSL Project Report .docx to high-fidelity PDF.
"""
import os
import subprocess

def export_docx_to_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_docx = os.path.join(base_dir, "docs", "DCDS_PROJECT_REPORT.docx")
    output_pdf = os.path.join(base_dir, "docs", "DCDS_PROJECT_REPORT.pdf")
    root_pdf = os.path.join(base_dir, "DCDS_PROJECT_REPORT.pdf")

    if not os.path.exists(input_docx):
        input_docx = os.path.join(base_dir, "docs", "DCDSL_PROJECT_REPORT.docx")

    print(f"📄 Converting '{input_docx}' to PDF via Pages...")

    applescript = f'''
    tell application "Pages"
        set docPath to POSIX file "{input_docx}"
        set pdfPath to POSIX file "{output_pdf}"
        set myDoc to open docPath
        export myDoc to file pdfPath as PDF
        close myDoc saving no
    end tell
    '''

    res = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ Generated PDF: {output_pdf}")
        # Copy to root and mirror compatibility names
        import shutil
        shutil.copyfile(output_pdf, root_pdf)
        shutil.copyfile(output_pdf, os.path.join(base_dir, "docs", "DCDSL_PROJECT_REPORT.pdf"))
        shutil.copyfile(output_pdf, os.path.join(base_dir, "DCDSL_PROJECT_REPORT.pdf"))
        print(f"✅ Saved copies to root and docs/")
    else:
        print("❌ Error converting to PDF:", res.stderr)

if __name__ == "__main__":
    export_docx_to_pdf()
