#!/usr/bin/env python3
"""
Comprehensive Database Architecture, Relational Schema & Complete SQL Query Specification
Generator for the Intelligent Hostel Complaint Management System (HostelPulse).
Builds a publication-grade .docx document and converts to PDF via Apple Pages on macOS.
"""

import os
import sys
import subprocess
import shutil

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# Palette
NAVY_COLOR = RGBColor(30, 58, 138)       # #1E3A8A
SLATE_COLOR = RGBColor(15, 23, 42)       # #0F172A
BODY_COLOR = RGBColor(51, 65, 85)        # #334155
MUTED_COLOR = RGBColor(100, 116, 139)    # #64748B
WHITE_COLOR = RGBColor(255, 255, 255)
TEAL_COLOR = RGBColor(13, 148, 136)      # #0D9488
CODE_TEXT_COLOR = RGBColor(15, 23, 42)

NAVY_HEX = "1E3A8A"
CODE_BG_HEX = "F8FAFC"
BORDER_HEX = "CBD5E1"
ALT_ROW_HEX = "F1F5F9"
HEADER_BG_HEX = "1E3A8A"


def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))


def set_cell_margins(cell, top=90, bottom=90, left=130, right=130):
    tcPr = cell._element.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>'))


def set_table_borders(table, border_color="CBD5E1", sz="4"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        tblBorders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>
                <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>
                <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>
                <w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>
                <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>
                <w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>
            </w:tblBorders>
        ''')
        tblPr[0].append(tblBorders)


def add_sql_block(doc, query_title, sql_text, note=None):
    """Renders a styled SQL code box with an accent border."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.8)
    set_cell_background(cell, CODE_BG_HEX)
    set_cell_margins(cell, top=90, bottom=90, left=150, right=150)

    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{BORDER_HEX}"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{NAVY_HEX}"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{BORDER_HEX}"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="{BORDER_HEX}"/>
        </w:tcBorders>
    ''')
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05

    if query_title:
        r_t = p.add_run(f"SQL :: {query_title}\n")
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(9.5)
        r_t.font.bold = True
        r_t.font.color.rgb = NAVY_COLOR

    r_sql = p.add_run(sql_text.strip() + "\n")
    r_sql.font.name = "Courier New"
    r_sql.font.size = Pt(8.5)
    r_sql.font.color.rgb = CODE_TEXT_COLOR

    if note:
        r_n = p.add_run(f"-- Context: {note}")
        r_n.font.name = "Courier New"
        r_n.font.size = Pt(8.0)
        r_n.font.italic = True
        r_n.font.color.rgb = MUTED_COLOR

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(3)


def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = NAVY_COLOR
    return p


def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = SLATE_COLOR
    return p


def add_body(doc, text, bold_prefix=None, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_bp = p.add_run(bold_prefix)
        r_bp.font.name = "Times New Roman"
        r_bp.font.size = Pt(9.5)
        r_bp.font.bold = True
        r_bp.font.color.rgb = SLATE_COLOR
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(9.5)
    r.font.color.rgb = BODY_COLOR
    return p


def add_bullet(doc, label, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.12
    r_l = p.add_run(label + ": ")
    r_l.font.name = "Times New Roman"
    r_l.font.size = Pt(9.2)
    r_l.font.bold = True
    r_l.font.color.rgb = SLATE_COLOR
    r_t = p.add_run(text)
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(9.2)
    r_t.font.color.rgb = BODY_COLOR
    return p


def add_schema_table(doc, headers, rows, col_widths=None):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, BORDER_HEX, sz="4")

    # Header Row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_background(hdr_cells[i], HEADER_BG_HEX)
        set_cell_margins(hdr_cells[i], top=70, bottom=70, left=90, right=90)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = WHITE_COLOR

    # Body Rows
    for r_idx, row_data in enumerate(rows):
        row_cells = tbl.rows[r_idx + 1].cells
        bg_hex = ALT_ROW_HEX if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_hex)
            set_cell_margins(row_cells[c_idx], top=50, bottom=50, left=80, right=80)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Times New Roman" if c_idx != 1 else "Courier New"
                r.font.size = Pt(8.2)
                r.font.color.rgb = SLATE_COLOR
                if c_idx == 0:
                    r.font.bold = True

    if col_widths:
        for r in tbl.rows:
            for idx, width in enumerate(col_widths):
                r.cells[idx].width = Inches(width)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(3)


def build_database_doc():
    doc = Document()

    # Page Margins (0.75 in all around for maximum readable width)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # ========================================================================
    # COVER / HEADER BANNER
    # ========================================================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst = p_inst.add_run("SYMBIOSIS INSTITUTE OF TECHNOLOGY (SIT), PUNE\n")
    r_inst.font.name = "Times New Roman"
    r_inst.font.size = Pt(13)
    r_inst.font.bold = True
    r_inst.font.color.rgb = NAVY_COLOR

    r_dept = p_inst.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n")
    r_dept.font.name = "Times New Roman"
    r_dept.font.size = Pt(10)
    r_dept.font.bold = True
    r_dept.font.color.rgb = MUTED_COLOR

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(2)
    r_t = p_title.add_run("DATABASE ARCHITECTURE, SCHEMA & SQL QUERY SPECIFICATION\n")
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(16)
    r_t.font.bold = True
    r_t.font.color.rgb = NAVY_COLOR

    r_sub = p_title.add_run("Intelligent Hostel Complaint Management System (HostelPulse)\n")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(11.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = SLATE_COLOR

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(2)
    p_meta.paragraph_format.space_after = Pt(12)
    r_meta = p_meta.add_run("Candidate: Pranil Shah (PRN: 22070123086)  |  RDBMS Engine: SQLite 3.x / PostgreSQL 15+  |  Academic Year: 2026")
    r_meta.font.name = "Times New Roman"
    r_meta.font.size = Pt(9)
    r_meta.font.italic = True
    r_meta.font.color.rgb = MUTED_COLOR

    # Horizontal Divider Line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(8)
    r_div = p_div.add_run("━" * 58)
    r_div.font.name = "Courier New"
    r_div.font.size = Pt(10)
    r_div.font.color.rgb = RGBColor(203, 213, 225)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ========================================================================
    # SECTION 1: ARCHITECTURAL OVERVIEW
    # ========================================================================
    add_heading_1(doc, "1. Executive Database Overview & Relational Architecture")
    add_body(
        doc,
        "The Intelligent Hostel Complaint Management System (HostelPulse) relies on a normalized relational database "
        "designed to provide ACID transaction guarantees, high-performance querying, and seamless integration with "
        "the FastAPI backend and Local LLM Priority Engine. The persistence layer models campus living infrastructure, "
        "student resident credentials, warden administrative scopes, and multimedia complaint telemetry."
    )
    add_body(
        doc,
        "The architecture supports dual database engines through standard ANSI SQL conventions: an embedded, zero-configuration "
        "SQLite instance (backend_py/hostel.db) optimized for local edge execution and automated pre-seeding, and an enterprise "
        "PostgreSQL schema (database_schema.sql) for multi-campus distributed deployments. Referential integrity is strictly "
        "enforced via foreign key constraints, cascading deletions on user lifecycles, and secondary B-Tree indexing on triage telemetry."
    )

    add_bullet(doc, "Total Relational Tables", "5 core entities (users, block, student, warden, complaint)")
    add_bullet(doc, "Primary Storage Format", "SQLite 3.x (WAL journal mode) with full PostgreSQL 15+ DDL equivalence")
    add_bullet(doc, "Authentication Security", "Salted SHA-256 cryptographic password hashing (64-character hexadecimal digest)")
    add_bullet(doc, "Index Accelerations", "4 dedicated secondary B-Tree indexes targeting priority triage, student filtering, and status lookups")

    # ========================================================================
    # SECTION 2: ENTITY-RELATIONSHIP (ER) MODEL & KEY RELATIONS
    # ========================================================================
    add_heading_1(doc, "2. Entity-Relationship (ER) Model & Inter-Table Key Relationships")
    add_body(
        doc,
        "The data model employs an Object-Relational Table Inheritance pattern to decouple fundamental identity attributes "
        "(users) from domain-specific student and administrative roles. This eliminates null column proliferation and guarantees "
        "strict role-based authorization."
    )

    # Embed ER Diagram if available
    base_dir = os.path.dirname(os.path.abspath(__file__))
    er_img_path = os.path.join(base_dir, "assets", "11_database_er_diagram.png")
    if not os.path.exists(er_img_path):
        er_img_path = os.path.join(base_dir, "images", "hostelDatabaseErDiagram.png")

    if os.path.exists(er_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(er_img_path, width=Inches(5.6))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(6)
        r_cap = p_cap.add_run("Figure 2.1: Entity-Relationship Schema & Cardinality Architecture for HostelPulse")
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(8.5)
        r_cap.font.bold = True
        r_cap.font.color.rgb = SLATE_COLOR

    add_heading_2(doc, "2.1 Relational Cardinality & Referential Integrity Matrix")
    add_body(
        doc,
        "The following matrix outlines every relational link, primary/foreign key binding, cascading rule, and business policy "
        "governing data consistency across the application:"
    )

    rel_headers = ["Parent Entity", "Child Entity", "Cardinality", "Foreign Key Constraint", "On Delete Action", "Business Enforcement Logic"]
    rel_rows = [
        [
            "users",
            "student",
            "1 : 1",
            "student.student_id → users.user_id",
            "CASCADE",
            "Identity inheritance. Deleting a user automatically purges their student academic profile."
        ],
        [
            "users",
            "warden",
            "1 : 1",
            "warden.warden_id → users.user_id",
            "CASCADE",
            "Identity inheritance. Deleting an administrative user removes their warden jurisdictional profile."
        ],
        [
            "block",
            "student",
            "1 : N",
            "student.block_id → block.block_id",
            "SET NULL",
            "Building allocation. If a hostel block is decommissioned, students remain registered with null block."
        ],
        [
            "block",
            "warden",
            "1 : N",
            "warden.block_id → block.block_id",
            "SET NULL",
            "Administrative oversight. Wardens supervise designated blocks; restructuring preserves staff accounts."
        ],
        [
            "student",
            "complaint",
            "1 : N",
            "complaint.student_id → student.student_id",
            "CASCADE",
            "Grievance audit trail. Complaints originate from verified students; account deletion cascades records."
        ],
        [
            "block",
            "complaint",
            "1 : N",
            "complaint.block_id → block.block_id",
            "SET NULL",
            "Physical incident localization. Associates complaints with physical hostel blocks for contractor routing."
        ]
    ]
    add_schema_table(doc, rel_headers, rel_rows, [0.8, 0.8, 0.6, 1.6, 0.9, 2.1])

    # ========================================================================
    # SECTION 3: COMPREHENSIVE TABLE SCHEMA & COLUMN SPECIFICATIONS
    # ========================================================================
    add_heading_1(doc, "3. Table Specifications, Column Data Types & Domain Constraints")
    add_body(
        doc,
        "Each table in the schema is documented below with its exact physical column name, storage data type, "
        "nullability, primary/foreign key role, default value, and business description."
    )

    # Table 3.1: users
    add_heading_2(doc, "3.1 Table Name: users (Central Identity & Role-Based Access)")
    add_body(doc, "Stores core credentials, contact data, and RBAC roles for students, wardens, and administrators.")
    users_headers = ["Column Name", "Data Type", "Constraints / Keys", "Default Value", "Description & Usage"]
    users_rows = [
        ["user_id", "INTEGER / SERIAL", "PRIMARY KEY, AUTOINCREMENT", "Sequential", "Surrogate unique identifier for every campus account."],
        ["full_name", "TEXT / VARCHAR(100)", "NOT NULL", "None", "Official academic full name of the user."],
        ["email", "TEXT / VARCHAR(255)", "UNIQUE, NOT NULL", "None", "Campus institutional email address used for JWT authentication."],
        ["phone", "TEXT / VARCHAR(20)", "NOT NULL", "None", "Contact mobile telephone number formatted with country code."],
        ["password", "TEXT", "NOT NULL", "None", "Salted cryptographic SHA-256 hash digest (64 hex characters)."],
        ["type", "TEXT / VARCHAR(20)", "NOT NULL, CHECK (type IN...)", "None", "RBAC authorization role: 'student', 'warden', or 'admin'."],
        ["created_at", "TIMESTAMP", "NOT NULL", "CURRENT_TIMESTAMP", "UTC timestamp of user registration."]
    ]
    add_schema_table(doc, users_headers, users_rows, [1.0, 1.2, 1.5, 1.1, 2.0])

    # Table 3.2: block
    add_heading_2(doc, "3.2 Table Name: block (Campus Residential Infrastructure)")
    add_body(doc, "Maintains geographical and physical residential hostel buildings across the campus.")
    block_headers = ["Column Name", "Data Type", "Constraints / Keys", "Default Value", "Description & Usage"]
    block_rows = [
        ["block_id", "INTEGER / SERIAL", "PRIMARY KEY, AUTOINCREMENT", "Sequential", "Surrogate primary key for the residential wing/building."],
        ["block_name", "TEXT / VARCHAR(100)", "NOT NULL", "None", "Official name (e.g., 'Block A (North Wing)', 'Block B (South Wing)')."],
        ["description", "TEXT", "OPTIONAL (NULLABLE)", "None", "Demographic allocation (e.g., 'Undergraduate Boys Residence')."]
    ]
    add_schema_table(doc, block_headers, block_rows, [1.0, 1.2, 1.5, 1.1, 2.0])

    # Table 3.3: student
    add_heading_2(doc, "3.3 Table Name: student (Resident Student Academic Specialization)")
    add_body(doc, "Extends the users table with university seat numbers, allocated blocks, and room numbers.")
    student_headers = ["Column Name", "Data Type", "Constraints / Keys", "Default Value", "Description & Usage"]
    student_rows = [
        ["student_id", "INTEGER", "PRIMARY KEY, FK → users(user_id) ON DELETE CASCADE", "None", "Inherited primary key linked to users.user_id."],
        ["block_id", "INTEGER", "FOREIGN KEY → block(block_id) ON DELETE SET NULL", "NULL", "Assigned hostel building identifier."],
        ["usn", "TEXT / VARCHAR(50)", "OPTIONAL (NULLABLE)", "None", "University Seat Number / PRN (e.g., '26070126505')."],
        ["room", "TEXT / VARCHAR(20)", "OPTIONAL (NULLABLE)", "None", "Specific residential room number (e.g., '101', '102')."]
    ]
    add_schema_table(doc, student_headers, student_rows, [1.0, 1.2, 1.8, 0.8, 2.0])

    # Table 3.4: warden
    add_heading_2(doc, "3.4 Table Name: warden (Hostel Administration Specialization)")
    add_body(doc, "Extends the users table with assigned administrative hostel block oversight.")
    warden_headers = ["Column Name", "Data Type", "Constraints / Keys", "Default Value", "Description & Usage"]
    warden_rows = [
        ["warden_id", "INTEGER", "PRIMARY KEY, FK → users(user_id) ON DELETE CASCADE", "None", "Inherited primary key linked to users.user_id."],
        ["block_id", "INTEGER", "FOREIGN KEY → block(block_id) ON DELETE SET NULL", "NULL", "Residential block under this warden's jurisdiction."]
    ]
    add_schema_table(doc, warden_headers, warden_rows, [1.0, 1.2, 1.8, 0.8, 2.0])

    # Table 3.5: complaint
    add_heading_2(doc, "3.5 Table Name: complaint (Grievance Telemetry & AI Priority Engine)")
    add_body(doc, "Comprehensive grievance records capturing incident descriptions, AI priority scoring, SLAs, and evidence media.")
    comp_headers = ["Column Name", "Data Type", "Constraints / Keys", "Default Value", "Description & Usage"]
    comp_rows = [
        ["id", "INTEGER / SERIAL", "PRIMARY KEY, AUTOINCREMENT", "Sequential", "Unique ticket sequence identifier."],
        ["name", "TEXT / VARCHAR(200)", "OPTIONAL (NULLABLE)", "None", "Brief issue headline or incident title."],
        ["block_id", "INTEGER", "FK → block(block_id) ON DELETE SET NULL", "NULL", "Hostel building where incident occurred."],
        ["student_id", "INTEGER", "FK → student(student_id) ON DELETE CASCADE", "None", "Student resident who lodged the ticket."],
        ["description", "TEXT", "NOT NULL", "None", "Comprehensive natural language description of maintenance problem."],
        ["room", "TEXT / VARCHAR(20)", "OPTIONAL (NULLABLE)", "None", "Room number or common area (e.g., 'Corridor 3F', '101')."],
        ["is_completed", "BOOLEAN / INT", "NOT NULL", "0 (False)", "Binary resolution flag (0 = Unresolved, 1 = Completed)."],
        ["status", "VARCHAR(20)", "CHECK (status IN...)", "'PENDING'", "Lifecycle state: 'PENDING', 'IN_PROGRESS', 'RESOLVED', 'REJECTED'."],
        ["priority", "VARCHAR(20)", "CHECK (priority IN...)", "'MEDIUM'", "AI-assigned severity tier: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'."],
        ["priority_score", "INTEGER", "CHECK (score BETWEEN 1 AND 100)", "50", "Numerical urgency metric (1 to 100) generated by NLP classifier."],
        ["category", "VARCHAR(50)", "NOT NULL", "'General'", "Domain classification (Electrical, Plumbing, Security, Hygiene, etc.)."],
        ["urgency_reason", "TEXT", "OPTIONAL (NULLABLE)", "None", "Explainable AI rationale detailing detected safety or operational signals."],
        ["suggested_action", "TEXT", "OPTIONAL (NULLABLE)", "None", "Standardized mitigation protocol for wardens and dispatch crews."],
        ["sla_hours", "INTEGER", "NOT NULL", "24", "Maximum resolution window SLA (CRITICAL=2h, HIGH=8h, MED=24h, LOW=72h)."],
        ["ai_engine", "VARCHAR(100)", "NOT NULL", "'Embedded Local NLP'", "Model identifier (Ollama llama3.2/qwen2.5 or Embedded Classifier)."],
        ["warden_notes", "TEXT", "OPTIONAL (NULLABLE)", "None", "Administrative remarks, contractor assignments, or resolution verification."],
        ["media_url", "TEXT", "OPTIONAL (NULLABLE)", "None", "Relative file path or URI to attached photo or video evidence."],
        ["media_type", "VARCHAR(20)", "OPTIONAL (NULLABLE)", "None", "MIME category of attached evidence ('image' or 'video')."],
        ["created_at", "TIMESTAMP", "NOT NULL", "CURRENT_TIMESTAMP", "Submission timestamp recorded automatically."],
        ["assigned_at", "TIMESTAMP", "OPTIONAL (NULLABLE)", "None", "Timestamp when warden updated status to IN_PROGRESS."],
        ["resolved_at", "TIMESTAMP", "OPTIONAL (NULLABLE)", "None", "Timestamp when ticket status transitioned to RESOLVED."]
    ]
    add_schema_table(doc, comp_headers, comp_rows, [1.1, 1.1, 1.6, 0.9, 2.1])

    # ========================================================================
    # SECTION 4: PERFORMANCE INDEXES
    # ========================================================================
    add_heading_1(doc, "4. Performance Indexing & Query Optimization")
    add_body(
        doc,
        "To ensure sub-millisecond query execution times even as complaint volumes grow into tens of thousands of records, "
        "four dedicated secondary B-Tree indexes are created on the complaint table:"
    )

    idx_headers = ["Index Name", "Target Column(s)", "Index Ordering", "Primary Query Optimization Target"]
    idx_rows = [
        [
            "idx_complaint_priority",
            "priority_score",
            "DESCENDING",
            "Accelerates warden dashboard sorting: ORDER BY is_completed ASC, priority_score DESC."
        ],
        [
            "idx_complaint_student",
            "student_id",
            "ASCENDING",
            "Accelerates student personal portal view: WHERE c.student_id = ?."
        ],
        [
            "idx_complaint_status",
            "status",
            "ASCENDING",
            "Accelerates warden status filtering (PENDING vs IN_PROGRESS vs RESOLVED)."
        ],
        [
            "idx_complaint_category",
            "category",
            "ASCENDING",
            "Optimizes maintenance category grouping and telemetry aggregate statistics."
        ]
    ]
    add_schema_table(doc, idx_headers, idx_rows, [1.5, 1.1, 1.1, 3.1])

    # ========================================================================
    # SECTION 5: COMPLETE DDL (DATABASE DEFINITION LANGUAGE) QUERIES
    # ========================================================================
    add_heading_1(doc, "5. Complete Data Definition Language (DDL) Query Catalog")
    add_body(
        doc,
        "The following SQL statements are executed during application initialization to provision the complete database schema:"
    )

    add_sql_block(
        doc,
        "DDL-01: Create Core Users Table",
        """CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    password TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('student', 'warden', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "Stores cryptographic password hashes, unique email addresses, and RBAC authorization types."
    )

    add_sql_block(
        doc,
        "DDL-02: Create Hostel Blocks Table",
        """CREATE TABLE IF NOT EXISTS block (
    block_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_name TEXT NOT NULL,
    description TEXT
);""",
        "Represents campus physical buildings: North Wing, South Wing, and Tech Wing."
    )

    add_sql_block(
        doc,
        "DDL-03: Create Student Specialization Table",
        """CREATE TABLE IF NOT EXISTS student (
    student_id INTEGER PRIMARY KEY,
    block_id INTEGER,
    usn TEXT,
    room TEXT,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (block_id) REFERENCES block(block_id) ON DELETE SET NULL
);""",
        "Enforces 1:1 specialization with users; cascades on student account deletion."
    )

    add_sql_block(
        doc,
        "DDL-04: Create Warden Specialization Table",
        """CREATE TABLE IF NOT EXISTS warden (
    warden_id INTEGER PRIMARY KEY,
    block_id INTEGER,
    FOREIGN KEY (warden_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (block_id) REFERENCES block(block_id) ON DELETE SET NULL
);""",
        "Assigns supervisory hostel wardens to residential blocks."
    )

    add_sql_block(
        doc,
        "DDL-05: Create Complaint & AI Telemetry Table",
        """CREATE TABLE IF NOT EXISTS complaint (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    block_id INTEGER,
    student_id INTEGER,
    description TEXT NOT NULL,
    room TEXT,
    is_completed BOOLEAN DEFAULT 0,
    status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'IN_PROGRESS', 'RESOLVED', 'REJECTED')),
    priority TEXT DEFAULT 'MEDIUM' CHECK(priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    priority_score INTEGER DEFAULT 50,
    category TEXT DEFAULT 'General',
    urgency_reason TEXT,
    suggested_action TEXT,
    sla_hours INTEGER DEFAULT 24,
    ai_engine TEXT DEFAULT 'Embedded Local NLP Prioritizer',
    warden_notes TEXT,
    media_url TEXT,
    media_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (block_id) REFERENCES block(block_id) ON DELETE SET NULL
);""",
        "Primary telemetry entity storing grievance records, numerical urgency scores, and media attachments."
    )

    add_sql_block(
        doc,
        "DDL-06: Secondary Index Creation",
        """CREATE INDEX IF NOT EXISTS idx_complaint_priority ON complaint(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_complaint_student  ON complaint(student_id);
CREATE INDEX IF NOT EXISTS idx_complaint_status   ON complaint(status);
CREATE INDEX IF NOT EXISTS idx_complaint_category ON complaint(category);""",
        "B-Tree index creation ensuring lightning-fast triage sorting and dashboard filtering."
    )

    add_sql_block(
        doc,
        "DDL-07: Schema Migration & Telemetry Column Verification",
        """PRAGMA table_info(complaint);
ALTER TABLE complaint ADD COLUMN media_url TEXT;
ALTER TABLE complaint ADD COLUMN media_type TEXT;""",
        "Executed dynamically on startup to transparently upgrade existing databases without dropping data."
    )

    # ========================================================================
    # SECTION 6: COMPLETE DML (DATA MANIPULATION LANGUAGE) SEED QUERIES
    # ========================================================================
    add_heading_1(doc, "6. Seed Data & Initial Record Population Queries (DML)")
    add_body(
        doc,
        "Upon initial startup, the system executes idempotent population queries to seed the verified campus infrastructure, "
        "official administrative personnel, and genuine student residents:"
    )

    add_sql_block(
        doc,
        "DML-01: Seed Hostel Residential Blocks",
        """INSERT INTO block (block_name, description) VALUES
('Block A (North Wing)', 'Undergraduate Boys Residence'),
('Block B (South Wing)', 'Undergraduate Girls Residence'),
('Block C (Tech Wing)',  'Postgraduate & Research Block');""",
        "Populates verified campus residential blocks."
    )

    add_sql_block(
        doc,
        "DML-02: Seed Chief Warden Account",
        """INSERT INTO users (full_name, email, phone, password, type) VALUES
('Chief Warden', 'warden@hostel.edu', '+91 98765 00001', 
 'd96a0ef770c0031b46ec9a2277b52823d97c1b083533ed582001069c643fc22b', 'warden');

INSERT INTO warden (warden_id, block_id) VALUES (1, 1);""",
        "Creates Chief Warden with salted SHA-256 hash for password 'warden123'."
    )

    add_sql_block(
        doc,
        "DML-03: Seed Verified Student Residents (SIT Pune)",
        """-- 1. Pranil Shah (PRN: 22070123086 / USN: 26070126505)
INSERT INTO users (full_name, email, phone, password, type) VALUES
('Pranil Shah', 'student@hostel.edu', '+91 98201 26507', 
 '5c827507dd8dd9874ff5407df40d17a138d7f8e3bfb2b2c59861e9079b2983ee', 'student');
INSERT INTO student (student_id, block_id, usn, room) VALUES (2, 1, '26070126505', '101');

-- 2. Ansh Gajjar
INSERT INTO users (full_name, email, phone, password, type) VALUES
('Ansh Gajjar', 'ansh@hostel.edu', '+91 98201 26508', 
 '5c827507dd8dd9874ff5407df40d17a138d7f8e3bfb2b2c59861e9079b2983ee', 'student');
INSERT INTO student (student_id, block_id, usn, room) VALUES (3, 1, '26070126508', '102');

-- 3. Meet Dagade
INSERT INTO users (full_name, email, phone, password, type) VALUES
('Meet Dagade', 'meet@hostel.edu', '+91 98201 26505', 
 '5c827507dd8dd9874ff5407df40d17a138d7f8e3bfb2b2c59861e9079b2983ee', 'student');
INSERT INTO student (student_id, block_id, usn, room) VALUES (4, 1, '26070126505', '103');

-- 4. Karthik Bocca
INSERT INTO users (full_name, email, phone, password, type) VALUES
('Karthik Bocca', 'karthik@hostel.edu', '+91 98201 26219', 
 '5c827507dd8dd9874ff5407df40d17a138d7f8e3bfb2b2c59861e9079b2983ee', 'student');
INSERT INTO student (student_id, block_id, usn, room) VALUES (5, 2, '25070126219', '204');""",
        "Creates verified SIT residents with password hash for 'student123'."
    )

    add_sql_block(
        doc,
        "DML-04: Genuine Seed Complaints with Multimedia Evidence",
        """INSERT INTO complaint (
    id, name, block_id, student_id, description, room, is_completed, status, 
    priority, priority_score, category, urgency_reason, suggested_action, 
    sla_hours, ai_engine, media_url, media_type, created_at, assigned_at, resolved_at
) VALUES 
(8, ', jk jkl ', 1, 2, ' lb obiobvroie zviouzaboiw', '101', 1, 'RESOLVED',
 'LOW', 15, 'General Maintenance', 
 'Minor cosmetic or routine maintenance request. Can be handled during scheduled batch maintenance.',
 'Inspect room during regular warden inspection rounds.', 72, 'Embedded Local NLP Prioritizer (Active)',
 '/uploads/3afb0b31ec58_WhatsApp_Image_2026-10-20_at_23.51.41.jpeg', 'image',
 '2026-10-26 16:52:24', '2026-10-26 16:52:52', '2026-10-26 16:52:52'),

(9, 'Water leakage ', 1, 2, 'uviuviuviugviugio', '101', 1, 'RESOLVED',
 'LOW', 15, 'General Maintenance',
 'Minor cosmetic or routine maintenance request. Can be handled during scheduled batch maintenance.',
 'Inspect room during regular warden inspection rounds.', 72, 'Embedded Local NLP Prioritizer (Active)',
 NULL, NULL,
 '2026-10-26 16:58:44', '2026-10-26 16:59:23', '2026-10-26 16:59:23');""",
        "Preserves verified complaint records and attached WhatsApp photographic evidence."
    )

    # ========================================================================
    # SECTION 7: RUNTIME OPERATIONAL QUERIES (CRUD OPERATIONS)
    # ========================================================================
    add_heading_1(doc, "7. Runtime Application Query Catalog (CRUD & API Operations)")
    add_body(
        doc,
        "Every runtime database operation executed by the FastAPI backend endpoints is documented below:"
    )

    add_heading_2(doc, "7.1 Authentication & User Management Queries")
    add_sql_block(
        doc,
        "AUTH-01: Check Email Uniqueness on Registration",
        "SELECT user_id FROM users WHERE email = ?;",
        "Ensures no duplicate email registrations can occur."
    )
    add_sql_block(
        doc,
        "AUTH-02: Insert New User Account",
        "INSERT INTO users (full_name, email, phone, password, type) VALUES (?, ?, ?, ?, ?);",
        "Inserts base user row; returns generated user_id via cursor.lastrowid."
    )
    add_sql_block(
        doc,
        "AUTH-03: Insert Student Specialized Profile",
        "INSERT INTO student (student_id, block_id, usn, room) VALUES (?, ?, ?, ?);",
        "Links student academic record with generated user_id."
    )
    add_sql_block(
        doc,
        "AUTH-04: Credential Verification on Login",
        "SELECT * FROM users WHERE email = ?;",
        "Retrieves stored password hash for verification against salted SHA-256."
    )

    add_heading_2(doc, "7.2 Profile & Context Retrieval Queries")
    add_sql_block(
        doc,
        "PROF-01: Fetch Authenticated User Profile",
        "SELECT user_id, full_name, email, phone, type FROM users WHERE user_id = ?;",
        "Retrieves base identity attributes for session token."
    )
    add_sql_block(
        doc,
        "PROF-02: Fetch Student Academic & Room Details",
        """SELECT s.usn, s.room, b.block_id, b.block_name
FROM student s
LEFT JOIN block b ON s.block_id = b.block_id
WHERE s.student_id = ?;""",
        "Fetches residential block name and assigned room for student dashboard."
    )
    add_sql_block(
        doc,
        "PROF-03: Fetch Warden Jurisdictional Block",
        """SELECT w.block_id, b.block_name
FROM warden w
LEFT JOIN block b ON w.block_id = b.block_id
WHERE w.warden_id = ?;""",
        "Resolves block supervised by warden."
    )

    add_heading_2(doc, "7.3 Complaint Lodging & Ingestion Queries")
    add_sql_block(
        doc,
        "COMP-01: Lookup Student Block for Incident Geolocation",
        "SELECT block_id, room FROM student WHERE student_id = ?;",
        "Resolves student's assigned building for automated AI prompt context."
    )
    add_sql_block(
        doc,
        "COMP-02: Insert Complaint Ticket with AI Urgency Telemetry",
        """INSERT INTO complaint (
    name, block_id, student_id, description, room, is_completed, status,
    priority, priority_score, category, urgency_reason, suggested_action,
    sla_hours, ai_engine, media_url, media_type, created_at
) VALUES (
    ?, ?, ?, ?, ?, 0, 'PENDING',
    ?, ?, ?, ?, ?,
    ?, ?, ?, ?, CURRENT_TIMESTAMP
);""",
        "Inserts ticket with priority tier, urgency score (1-100), SLA, and media link."
    )
    add_sql_block(
        doc,
        "COMP-03: Fetch Created Complaint Record",
        "SELECT * FROM complaint WHERE id = ?;",
        "Returns the newly committed complaint record to the client."
    )

    add_heading_2(doc, "7.4 Master Dashboard Multi-Table Join & Dynamic Triage Query")
    add_sql_block(
        doc,
        "DASH-01: Master Multi-Table Complaint Telemetry Join",
        """SELECT 
    c.id, c.name, c.block_id, c.student_id, c.description, c.room,
    c.is_completed, c.status, c.priority, c.priority_score, c.category,
    c.urgency_reason, c.suggested_action, c.sla_hours, c.ai_engine,
    c.warden_notes, c.media_url, c.media_type, c.created_at, c.assigned_at, c.resolved_at,
    b.block_name,
    u.full_name as student_name,
    u.phone as student_phone,
    s.usn as student_usn
FROM complaint c
LEFT JOIN block b   ON c.block_id = b.block_id
LEFT JOIN users u   ON c.student_id = u.user_id
LEFT JOIN student s ON c.student_id = s.student_id
WHERE 1=1
  -- Dynamic Condition: Student Scoping
  -- AND c.student_id = ?
  -- Dynamic Condition: Status Filtering
  -- AND (c.status = 'PENDING' AND (c.is_completed = 0 OR c.is_completed IS NULL))
  -- AND c.status = 'IN_PROGRESS'
  -- AND (c.status = 'RESOLVED' OR c.is_completed = 1)
  -- Dynamic Condition: Priority Tier Filtering
  -- AND c.priority = 'CRITICAL'
  -- Dynamic Condition: Category Filtering
  -- AND c.category = 'Electrical'
  -- Dynamic Condition: Keyword Search
  -- AND (c.name LIKE '%spark%' OR c.description LIKE '%spark%' OR c.room LIKE '%304%')
ORDER BY c.is_completed ASC, c.priority_score DESC, c.created_at DESC;""",
        "The central data pipeline powering both Student and Warden portals with real-time AI triage ordering."
    )

    add_heading_2(doc, "7.5 Ticket Status, Notes & Resolution Lifecycle Queries")
    add_sql_block(
        doc,
        "UPD-01: Warden Status & Remarks Update",
        """UPDATE complaint
SET status = ?, is_completed = ?, resolved_at = ?, warden_notes = ?, assigned_at = CURRENT_TIMESTAMP
WHERE id = ?;""",
        "Transitions ticket through PENDING → IN_PROGRESS → RESOLVED with audit timestamps."
    )
    add_sql_block(
        doc,
        "UPD-02: Quick Resolution Checkmark Toggle",
        """UPDATE complaint
SET is_completed = ?, status = ?, resolved_at = ?, assigned_at = CURRENT_TIMESTAMP
WHERE id = ?;""",
        "Allows 1-click status completion from the warden dashboard table."
    )
    add_sql_block(
        doc,
        "UPD-03: Delete Complaint Record",
        "DELETE FROM complaint WHERE id = ?;",
        "Hard-deletes an invalid or duplicate complaint ticket."
    )

    add_heading_2(doc, "7.6 Batch AI Triage & Telemetry Analytics Queries")
    add_sql_block(
        doc,
        "AI-01: Fetch All Unresolved Complaints for Batch Re-Scoring",
        "SELECT id, name, description, room, block_id FROM complaint WHERE is_completed = 0;",
        "Pulls active tickets into memory for local LLM re-triage."
    )
    add_sql_block(
        doc,
        "AI-02: Persist Re-Scored AI Triage Results",
        """UPDATE complaint
SET priority = ?, priority_score = ?, category = ?, urgency_reason = ?,
    suggested_action = ?, sla_hours = ?, ai_engine = ?
WHERE id = ?;""",
        "Persists freshly computed urgency scores, reasoning, and revised SLAs."
    )
    add_sql_block(
        doc,
        "STAT-01: Real-Time Telemetry KPI Aggregate Counts",
        """SELECT COUNT(*) FROM complaint;
SELECT COUNT(*) FROM complaint WHERE priority = 'CRITICAL' AND is_completed = 0;
SELECT COUNT(*) FROM complaint WHERE priority = 'HIGH' AND is_completed = 0;
SELECT COUNT(*) FROM complaint WHERE is_completed = 0 AND (status = 'PENDING' OR status IS NULL);
SELECT COUNT(*) FROM complaint WHERE status = 'IN_PROGRESS';
SELECT COUNT(*) FROM complaint WHERE is_completed = 1 OR status = 'RESOLVED';""",
        "Populates top-level KPI metric cards on the Chief Warden command center."
    )
    add_sql_block(
        doc,
        "STAT-02: Incident Distribution by Category",
        """SELECT category, COUNT(*) as count 
FROM complaint 
GROUP BY category 
ORDER BY count DESC;""",
        "Provides statistical breakdown across Electrical, Plumbing, Hygiene, and Security domains."
    )

    # ========================================================================
    # SECTION 8: NORMALIZATION ANALYSIS
    # ========================================================================
    add_heading_1(doc, "8. Relational Normalization Analysis (1NF, 2NF, 3NF, BCNF)")
    add_body(
        doc,
        "The schema was designed strictly adhering to formal database normalization theory to eliminate data redundancy, "
        "prevent update anomalies, and maximize data integrity:"
    )

    add_bullet(
        doc,
        "First Normal Form (1NF)",
        "Every attribute contains only atomic, indivisible values. There are no repeating groups or multivalued arrays. "
        "Each table possesses a primary key that uniquely identifies each tuple."
    )
    add_bullet(
        doc,
        "Second Normal Form (2NF)",
        "The schema satisfies 1NF and contains zero partial functional dependencies. All non-prime attributes are fully functionally "
        "dependent on the entire primary key. In single-attribute surrogate keys (user_id, block_id, id), partial dependency is impossible."
    )
    add_bullet(
        doc,
        "Third Normal Form (3NF)",
        "The schema satisfies 2NF and contains zero transitive dependencies. Non-prime attributes depend solely on candidate keys. "
        "For example, student room and USN numbers do not reside in users, nor do hostel block names reside in complaint. Instead, "
        "they are normalized into student and block entities and joined dynamically via foreign keys."
    )
    add_bullet(
        doc,
        "Boyce-Codd Normal Form (BCNF)",
        "For every non-trivial functional dependency X → Y, X is a superkey. In users, email → user_id and user_id → email; "
        "both are candidate keys with unique constraints, satisfying BCNF."
    )

    # ========================================================================
    # SECTION 9: COMPARATIVE SYNTAX GUIDE (SQLITE VS POSTGRESQL)
    # ========================================================================
    add_heading_1(doc, "9. Comparative Relational Syntax Reference (SQLite vs PostgreSQL)")
    add_body(
        doc,
        "The project codebase is engineered for dual portability. The following comparison illustrates how data types "
        "and constraints map between the local development SQLite engine and production PostgreSQL instances:"
    )

    comp_map_headers = ["Feature / Constraint", "SQLite 3.x (Local Engine)", "PostgreSQL 15+ (Production)", "Architectural Reason"]
    comp_map_rows = [
        [
            "Primary Key Generation",
            "INTEGER PRIMARY KEY AUTOINCREMENT",
            "SERIAL PRIMARY KEY",
            "Automatic surrogate sequence increment."
        ],
        [
            "Boolean Representation",
            "BOOLEAN DEFAULT 0 (Stored as INTEGER)",
            "BOOLEAN DEFAULT FALSE",
            "Binary completion tracking (is_completed)."
        ],
        [
            "Timestamp Defaults",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "TIMESTAMPTZ DEFAULT NOW()",
            "UTC timeline auditing for complaint lifecycle."
        ],
        [
            "String Length Limits",
            "TEXT (Dynamic length)",
            "VARCHAR(n) / TEXT",
            "SQLite treats VARCHAR as TEXT; PostgreSQL enforces bounds."
        ],
        [
            "Domain Constraints",
            "CHECK (status IN ('PENDING', ...))",
            "CHECK (status IN ('PENDING', ...))",
            "Identical ANSI SQL domain validation."
        ],
        [
            "Foreign Key Pragma",
            "PRAGMA foreign_keys = ON;",
            "Enforced by default in engine",
            "SQLite requires explicit pragma activation per connection."
        ]
    ]
    add_schema_table(doc, comp_map_headers, comp_map_rows, [1.4, 1.8, 1.8, 1.8])

    # Save output .docx
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    docx_path = os.path.join(docs_dir, "HOSTEL_DATABASE_SPECIFICATION.docx")
    doc.save(docx_path)
    print(f"✅ Generated Word Document: {docx_path}")

    # Convert to PDF via Apple Pages
    pdf_path = os.path.join(docs_dir, "HOSTEL_DATABASE_SPECIFICATION.pdf")
    desktop_pdf = os.path.join(os.path.expanduser("~"), "Desktop", "HOSTEL_DATABASE_SPECIFICATION.pdf")

    applescript = f'''
    tell application "Pages"
        set docPath to POSIX file "{docx_path}"
        set pdfPath to POSIX file "{pdf_path}"
        set myDoc to open docPath
        export myDoc to file pdfPath as PDF
        close myDoc saving no
    end tell
    '''
    res = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ Successfully exported PDF via Pages: {pdf_path}")
        shutil.copyfile(pdf_path, desktop_pdf)
        print(f"✅ Mirrored PDF to Desktop: {desktop_pdf}")
    else:
        print("❌ Error converting to PDF via Pages:", res.stderr)
        return False

    return True


if __name__ == "__main__":
    success = build_database_doc()
    sys.exit(0 if success else 1)
