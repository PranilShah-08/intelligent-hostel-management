import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import os

def build_report():
    input_file = "DCDSL PROJECT REPORT format.docx"
    doc = docx.Document(input_file)
    print("Opened base document. Paragraphs count:", len(doc.paragraphs))

    # --- 1. UPDATE FRONT MATTER (Cover Page & Certificate) ---
    # Paragraph 2 is the Cover Page Header
    doc.paragraphs[2].text = "A DCDS PROJECT REPORT"
    for run in doc.paragraphs[2].runs:
        run.font.name = "Times Roman"
        run.font.size = Pt(14)
        run.bold = True

    # Paragraph 8 is the Title on Cover Page
    doc.paragraphs[8].text = "INTELLIGENT HOSTEL COMPLAINT MANAGEMENT SYSTEM WITH LOCAL LLM PRIORITY TRIAGE & MULTI-MEDIA EVIDENCE TRACKING"
    for run in doc.paragraphs[8].runs:
        run.font.name = "Times Roman"
        run.font.size = Pt(16)
        run.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102) # Deep institutional navy
    
    # Paragraph 9 had trailing quote
    doc.paragraphs[9].text = ""

    # Update Student Names and PRNs on Cover Page
    students = [
        ("Pranil Shah", "26070126505"),
        ("Ansh Gajjar", "26070126508"),
        ("Meet Dagade", "26070126505"),
        ("Karthik Bocca", "25070126219")
    ]
    p_indices = [13, 14, 15, 16]
    for idx, (name, prn) in zip(p_indices, students):
        doc.paragraphs[idx].text = f"{name}\t{prn}"
        for run in doc.paragraphs[idx].runs:
            run.font.name = "Times Roman"
            run.font.size = Pt(12)

    # Paragraph 28 is the Academic Year on Cover Page
    doc.paragraphs[28].text = "A.Y. 2026-27"
    for run in doc.paragraphs[28].runs:
        run.font.name = "Times Roman"
        run.font.size = Pt(12)
        run.bold = True

    # Paragraph 37 is the Certificate description
    cert_p = doc.paragraphs[37]
    cert_p.text = (
        "This is to certify that the DCDS Project work entitled “Intelligent Hostel Complaint Management "
        "System with Local LLM Priority Triage & Multi-Media Evidence Tracking” is carried out by "
        "Pranil Shah (26070126505), Ansh Gajjar (26070126508), Meet Dagade (26070126505), "
        "and Karthik Bocca (25070126219), in Artificial Intelligence & Machine Learning, "
        "Symbiosis International (Deemed University), Pune during the academic year 2026-2027."
    )
    for run in cert_p.runs:
        run.font.name = "Times Roman"
        run.font.size = Pt(12)

    # Footer in section 2: fix typo "AL&ML" -> "AI & ML"
    if len(doc.sections) > 2 and doc.sections[2].footer.paragraphs:
        doc.sections[2].footer.paragraphs[0].text = "Department of AI & ML"
        for r in doc.sections[2].footer.paragraphs[0].runs:
            r.font.name = "Times Roman"
            r.font.size = Pt(10)

    # --- 2. UPDATE TABLE OF CONTENTS TABLE ---
    toc_table = doc.tables[0]
    # Update page numbers in the table of contents
    page_map = {
        "Introduction": "1",
        "Problem Statement": "3",
        "System architecture and Modules": "4",
        "Functional requirements": "7",
        "Entities, relationships and attributes": "9",
        "Relational schema": "12",
        "Implementation": "14",
        "User Interface": "18",
        "Conclusion": "24",
        "References": "25"
    }
    # Clean prompts from TOC table and format cleanly
    toc_clean_names = {
        8: "Implementation",
        9: "User Interface"
    }
    for row_idx, clean_text in toc_clean_names.items():
        if row_idx < len(toc_table.rows):
            cell_0 = toc_table.rows[row_idx].cells[0]
            # Keep only the main heading title
            while len(cell_0.paragraphs) > 1:
                p_elem = cell_0.paragraphs[-1]._p
                cell_0._tc.remove(p_elem)
            cell_0.paragraphs[0].text = clean_text
            for r in cell_0.paragraphs[0].runs:
                r.font.name = "Times Roman"
                r.font.size = Pt(12)

    for row in toc_table.rows:
        text = row.cells[0].text
        for key, p_val in page_map.items():
            if key in text and len(row.cells) > 1:
                row.cells[1].text = p_val
                for p in row.cells[1].paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    for r in p.runs:
                        r.font.name = "Times Roman"
                        r.font.size = Pt(12)

    # --- 3. REMOVE PLACEHOLDER CHAPTER PARAGRAPHS (from p75 onwards) ---
    body = doc._element.body
    for p in doc.paragraphs[75:]:
        body.remove(p._p)

    print("Cleared placeholder chapters. Paragraphs left before adding content:", len(doc.paragraphs))

    # Helper functions for adding styled content
    def add_chapter_title(title_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title_text)
        run.font.name = "Times Roman"
        run.font.size = Pt(18)
        run.bold = True
        run.font.color.rgb = RGBColor(17, 24, 39) # Slate 900
        return p

    def add_heading_2(heading_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(heading_text)
        run.font.name = "Times Roman"
        run.font.size = Pt(14)
        run.bold = True
        run.font.color.rgb = RGBColor(30, 58, 138) # Dark blue
        return p

    def add_heading_3(heading_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(heading_text)
        run.font.name = "Times Roman"
        run.font.size = Pt(12)
        run.bold = True
        run.font.color.rgb = RGBColor(51, 65, 85) # Slate 700
        return p

    def add_body_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Times Roman"
            r_pre.font.size = Pt(12)
            r_pre.bold = True
        run = p.add_run(text)
        run.font.name = "Times Roman"
        run.font.size = Pt(12)
        return p

    def add_bullet_item(bold_label, text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_bullet = p.add_run("• ")
        r_bullet.font.name = "Times Roman"
        r_bullet.font.size = Pt(12)
        r_bullet.bold = True
        r_lbl = p.add_run(bold_label + ": ")
        r_lbl.font.name = "Times Roman"
        r_lbl.font.size = Pt(12)
        r_lbl.bold = True
        run = p.add_run(text)
        run.font.name = "Times Roman"
        run.font.size = Pt(12)
        return p

    def add_code_block(code_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.right_indent = Inches(0.25)
        run = p.add_run(code_text)
        run.font.name = "Courier New"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_figure(image_filename, caption_text, width=Inches(5.8)):
        image_path = os.path.join("assets", image_filename)
        if os.path.exists(image_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(10)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(image_path, width=width)

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(12)
            r_cap = p_cap.add_run(caption_text)
            r_cap.font.name = "Times Roman"
            r_cap.font.size = Pt(10.5)
            r_cap.bold = True
            r_cap.italic = True
            r_cap.font.color.rgb = RGBColor(71, 85, 105)
        else:
            print(f"Warning: image {image_path} not found.")

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    add_chapter_title("1. Introduction")
    add_body_p(
        "Residential university hostels house thousands of students who depend daily on critical residential "
        "infrastructure, including electrical systems, plumbing, sanitary fixtures, Wi-Fi networking, furniture, and "
        "safety locks. Efficient maintenance of these facilities is vital for student safety, mental well-being, and "
        "academic success. However, traditional complaint handling in academic institutions predominantly relies on "
        "manual physical register books, fragmented emails, or unstructured WhatsApp group messages. These legacy "
        "methods suffer from crippling communication bottlenecks, unrecorded physical damage, absence of verifiable "
        "telemetry, and complete failure to prioritize life-safety emergencies over routine issues."
    )
    add_body_p(
        "The Intelligent Hostel Complaint Management System is an end-to-end web-based engineering solution designed "
        "to modernize campus facility operations. Built with a clean, high-contrast white aesthetic, the platform integrates "
        "a reactive modern client, a robust Python FastAPI backend, a normalized relational database engine, and a "
        "locally deployed Large Language Model (LLM) priority triage engine. The system automates grievance lodging, "
        "multimedia evidence ingestion, intelligent risk scoring (0 to 100), automated warden command dispatch, and "
        "real-time complaint lifecycle tracking."
    )
    add_body_p(
        "A critical innovation of this project is the integration of Local LLM Priority Triage with zero-cloud data leakage. "
        "Running local quantized models via Ollama (such as Llama 3, Mistral, or DeepSeek) combined with an embedded heuristic "
        "NLP fallback, the platform parses unstructured student narratives in real-time. It determines whether a reported issue "
        "poses an immediate electrical fire hazard, a water leakage hazard, or a routine maintenance task, instantly calculating "
        "a deterministic Priority Score. Furthermore, students can attach visual proof (high-resolution photographs and video clips) "
        "directly from their smartphones or laptops, eliminating dispute over work completion and providing wardens with "
        "irrefutable ground truth before dispatching repair technicians."
    )
    add_body_p(
        "This project serves as a comprehensive demonstration of Database & Distributed Computing Systems (DCDS) "
        "principles, including normalized 3NF relational modeling, strict referential integrity, foreign key cascading rules, "
        "B-Tree index optimization for descending priority queues, parameterized SQL execution against SQL injection, and "
        "asynchronous file streaming."
    )

    # =========================================================================
    # CHAPTER 2: PROBLEM STATEMENT & OBJECTIVES
    # =========================================================================
    add_chapter_title("2. Problem Statement")
    add_body_p(
        "In traditional university hostel administrative setups, student maintenance grievances are logged into paper registers "
        "kept at the security desk or warden office. This manual operating model introduces severe operational failure points:"
    )
    add_bullet_item("Strict First-Come First-Served (FIFO) Processing", 
        "Manual registers lack severity-based triage. An electrical sparking emergency or major water pipe rupture logged in the evening "
        "remains queued behind cosmetic issues such as a loose desk handle or squeaky chair reported earlier that morning.")
    add_bullet_item("Absence of Verifiable Media Evidence", 
        "Textual descriptions in registers are ambiguous and brief (e.g., 'water leaking'). Maintenance contractors frequently arrive "
        "with incorrect tools or replacement parts, causing repeated trips and multi-day delays. Disagreements routinely occur over whether "
        "a repair was executed satisfactorily.")
    add_bullet_item("Zero Real-Time Visibility and Accountability", 
        "Students have no mechanism to track whether their complaint has been reviewed, dispatched, or scheduled. Wardens cannot query "
        "cross-block failure trends, identify chronic electrical breakdowns, or audit contractor resolution turnaround times.")
    add_bullet_item("Data Privacy Risks and Cloud Subscription Costs", 
        "Commercial SaaS complaint platforms require recurring monthly subscriptions and transmit sensitive student names, room numbers, "
        "and residential patterns to public third-party cloud servers.")

    add_heading_2("Project Objectives")
    add_bullet_item("Structured Relational Database Design", 
        "To engineer a normalized SQLite relational schema modeling users, hostel blocks, student credentials, warden assignments, "
        "and complaints with strict foreign keys, check constraints, and B-tree indexes for fast analytical filtering.")
    add_bullet_item("Multi-Media Evidence Streaming Pipeline", 
        "To implement an asynchronous multipart file upload pipeline supporting photos (.png, .jpg, .jpeg) and video files (.mp4, .mov, .webm) "
        "stored under a secure uploads repository and rendered with live browser video controls and zoom previews.")
    add_bullet_item("Local LLM-Driven Dynamic Risk Triage", 
        "To engineer a privacy-preserving triage engine running local quantized LLMs (via Ollama) coupled with deterministic NLP fallback rules, "
        "calculating priority scores (0 to 100) and actionable reasoning without cloud dependency.")
    add_bullet_item("Warden Executive Command Center", 
        "To provide chief hostel wardens with real-time complaint queues ordered strictly by risk score descending, multi-criteria block filters, "
        "one-click status updates (Pending -> In Progress -> Resolved), and interactive evidence inspection modals.")
    add_bullet_item("Interactive Student Grievance Portal", 
        "To build a responsive portal where students receive live AI triage feedback while typing, lodge grievances with visual evidence, "
        "and monitor resolution progress through a step-by-step timeline tracker.")
    add_bullet_item("Performance, Security, and Integrity", 
        "To guarantee sub-50ms API query latencies, JWT authentication with salted bcrypt password hashing, input sanitization, and atomic "
        "status lifecycle transitions.")

    # =========================================================================
    # CHAPTER 3: SYSTEM ARCHITECTURE AND MODULES
    # =========================================================================
    add_chapter_title("3. System Architecture and Modules")
    add_heading_2("3.1 System Architecture")
    add_body_p(
        "The system employs a modern Four-Tier Architecture designed for high throughput, sub-second client responsiveness, "
        "and complete hardware autonomy. The four integrated tiers operate as follows:"
    )
    add_bullet_item("1. Presentation Tier (Client)", 
        "Engineered with React 18, Vite, and Tailwind CSS. Provides a clean, modern white theme with responsive UI cards, dynamic debounced "
        "live AI triage previews, multi-media drag-and-drop file uploaders, audio/video playback containers, and SVG status timelines.")
    add_bullet_item("2. Application & API Tier (FastAPI)", 
        "Built on Python 3.12 and FastAPI running asynchronously on Uvicorn ASGI. Implements JSON Web Token (JWT) bearer authentication, "
        "role-based route protection, multipart/form-data evidence streaming with MIME validation, and local LLM orchestration.")
    add_bullet_item("3. Relational Database Tier (SQLite Relational Engine)", 
        "Employs SQLite 3 with Write-Ahead Logging (WAL), foreign key cascade constraints, and B-Tree indexes on priority scores and block codes. "
        "Ensures ACID transaction compliance and zero external configuration overhead.")
    add_bullet_item("4. Local AI Inference Tier (Ollama LLM & NLP Heuristics)", 
        "Interfaces with local Ollama endpoints (http://localhost:11434) running open-source instruction-tuned models (Llama 3, Mistral, DeepSeek). "
        "Features an embedded fail-safe deterministic heuristic parser ensuring zero-downtime classification even when the LLM service is offline.")

    add_body_p(
        "Figure 1 illustrates the comprehensive database entity relationship schema and architectural tier interactions governing the system."
    )
    add_figure("11_database_er_diagram.png", "Figure 1: Relational Database Schema & System Architecture ER Diagram")

    add_heading_2("3.2 System Modules")
    add_bullet_item("Module 1: Authentication & Role-Based Access Control (RBAC)", 
        "Manages user registration and authentication for Students and Wardens. Passwords are encrypted using salted bcrypt hashes. "
        "Issues tamper-proof JWT bearer tokens containing user_id, email, and role claims. Restricts administrative status actions to wardens.")
    add_bullet_item("Module 2: Student Grievance Lodging & Live AI Preview", 
        "Captures student grievance title, category, hostel block, room number, detailed narrative, and optional photo/video evidence. "
        "As the student types, an asynchronous debounced API trigger fetches live AI triage analysis, displaying real-time risk scores.")
    add_bullet_item("Module 3: Multi-Media Evidence Streaming Pipeline", 
        "Accepts high-resolution photographic captures and video clips up to 25MB. Validates MIME headers, assigns unique UUID filenames, "
        "stores files under the backend uploads directory, and records persistent media_url and media_type metadata in the database.")
    add_bullet_item("Module 4: Local LLM Priority Triage Engine", 
        "Executes zero-shot structured prompts against local LLM endpoints. Extracts severity levels (High/Medium/Low), numerical priority scores "
        "(0 to 100), and concise analytical justifications. Automatically falls back to keyword-weighted heuristic analysis if Ollama is unreachable.")
    add_bullet_item("Module 5: Warden Executive Command Center", 
        "Equips wardens with an executive queue ordered strictly by priority_score DESC. Features multi-parameter filtering across hostel blocks "
        "(Block A, Block B, Block C, Block D), grievance categories, and resolution stages. Displays color-coded risk badges.")
    add_bullet_item("Module 6: Interactive Media Telemetry & Status Workflow", 
        "Enables wardens to inspect high-definition photo evidence and stream embedded video recordings directly inside an interactive modal. "
        "Permits immediate status updates ('Pending' -> 'In Progress' -> 'Resolved') with automated timestamp recording.")
    add_bullet_item("Module 7: Student Complaint Timeline Tracker", 
        "Provides students with full operational transparency. Displays an interactive progress timeline indicating submission date, "
        "assigned priority score, AI risk justification, media attachments, and official resolution timestamps.")
    add_bullet_item("Module 8: Query & Performance Optimization", 
        "Maintains specialized B-tree indexes over the complaint table, reducing sorting latencies from O(N) linear scans to O(log N) indexed lookups. "
        "Protects database transactions through WAL concurrency.")

    # =========================================================================
    # CHAPTER 4: FUNCTIONAL & NON-FUNCTIONAL REQUIREMENTS
    # =========================================================================
    add_chapter_title("4. Functional Requirements")
    add_heading_2("4.1 Functional Requirements Specifications")
    add_bullet_item("FR-1: User Registration and Authentication", 
        "The system shall allow students to register with their institutional roll number, hostel block, and room number. It shall allow wardens "
        "to register with their employee credentials. Passwords must be hashed using bcrypt, and authenticated sessions must issue JWT tokens.")
    add_bullet_item("FR-2: Dynamic Block and Category Retrieval", 
        "The system shall dynamically populate hostel blocks (Block A, Block B, Block C, Block D) and grievance categories (Electrical, Plumbing, "
        "Carpentry, Internet/Wi-Fi, Cleanliness, Safety/Security) directly from the relational database.")
    add_bullet_item("FR-3: Live AI Priority Triage Preview", 
        "As a student inputs their grievance description, the client shall debounce input by 600ms and query the /api/ai/preview-priority endpoint. "
        "The system shall return a real-time predicted category, priority score (0-100), and severity justification.")
    add_bullet_item("FR-4: Multi-Media Evidence Attachment", 
        "Students shall be able to attach an image (.png, .jpg, .jpeg) or a video (.mp4, .mov, .webm) up to 25MB. The backend must validate "
        "file integrity, store it on the server filesystem, and record the relative URL path in the complaint database record.")
    add_bullet_item("FR-5: Prioritized Warden Queue", 
        "The warden command center shall render all complaints sorted by priority_score descending (100 down to 0). Urgent life-safety hazards "
        "must automatically pin to the top of the queue regardless of submission order.")
    add_bullet_item("FR-6: Evidence Playback and Inspection", 
        "Wardens shall be able to click on any grievance to open an evidence modal. The modal must render full-size photographs and stream "
        "video recordings with native playback controls.")
    add_bullet_item("FR-7: Lifecycle Status Progression", 
        "Authorized wardens shall be able to update complaint status from 'Pending' to 'In Progress' and 'Resolved'. The system shall update "
        "the resolved_at timestamp automatically upon resolution.")
    add_bullet_item("FR-8: Interactive API Documentation", 
        "The FastAPI backend shall automatically generate and host interactive OpenAPI Swagger documentation at /docs for system verification.")

    add_heading_2("4.2 Non-Functional Requirements")
    add_bullet_item("NFR-1: Performance & Response Latency", 
        "Relational database lookups and queue sorting operations shall execute in under 50 milliseconds. The local LLM triage response shall "
        "return in under 1.5 seconds on modern multi-core workstations.")
    add_bullet_item("NFR-2: Data Privacy & Air-Gapped Operation", 
        "All AI inference shall execute on local hardware via Ollama without making outbound cloud API calls. Student complaints, room numbers, "
        "and media evidence shall never leave the campus server network.")
    add_bullet_item("NFR-3: Reliability & Referential Integrity", 
        "The database shall enforce strict foreign key constraints (PRAGMA foreign_keys = ON) and handle atomic transactions to ensure zero "
        "orphan records or partial writes upon power disruption.")
    add_bullet_item("NFR-4: Security & Input Validation", 
        "All API endpoints must sanitize string inputs against SQL injection and cross-site scripting (XSS). Uploaded files must be renamed to "
        "UUID strings to prevent path traversal vulnerabilities.")
    add_bullet_item("NFR-5: Modern Visual Usability", 
        "The interface shall adhere to a clean, crisp, high-contrast white and slate aesthetic with intuitive iconography, zero visual clutter, "
        "and complete mobile responsiveness.")

    # =========================================================================
    # CHAPTER 5: ENTITIES, RELATIONSHIPS AND ATTRIBUTES
    # =========================================================================
    add_chapter_title("5. Entities, Relationships and Attributes")
    add_body_p(
        "The data model is engineered following Third Normal Form (3NF) relational design principles. It captures institutional "
        "credentials, residential block layouts, student profiles, warden assignments, and detailed complaint records."
    )
    add_heading_2("5.1 Entity: users")
    add_body_p("Represents institutional user accounts for both students and hostel wardens.")
    add_bullet_item("user_id", "INTEGER PRIMARY KEY AUTOINCREMENT. Unique surrogate key identifying each user.")
    add_bullet_item("name", "VARCHAR(100) NOT NULL. Full legal name of the student or warden.")
    add_bullet_item("email", "VARCHAR(150) NOT NULL UNIQUE. Institutional email address used for login authentication.")
    add_bullet_item("password_hash", "VARCHAR(255) NOT NULL. Salted bcrypt cryptographic password hash.")
    add_bullet_item("role", "VARCHAR(20) NOT NULL CHECK (role IN ('student', 'warden')). Security authorization scope.")
    add_bullet_item("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP. Account registration timestamp.")

    add_heading_2("5.2 Entity: block")
    add_body_p("Represents residential hostel buildings within the university campus.")
    add_bullet_item("block_id", "INTEGER PRIMARY KEY AUTOINCREMENT. Unique identifier for the hostel block.")
    add_bullet_item("name", "VARCHAR(50) NOT NULL. Descriptive name (e.g., 'Block A - Nalanda Hostel').")
    add_bullet_item("code", "VARCHAR(10) NOT NULL UNIQUE. Short abbreviation code (e.g., 'BLK-A').")
    add_bullet_item("description", "TEXT. Structural or demographic details regarding the building.")
    add_bullet_item("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP. Record initialization timestamp.")

    add_heading_2("5.3 Entity: student")
    add_body_p("Stores residential and academic metadata for students registered in the hostel system.")
    add_bullet_item("student_id", "INTEGER PRIMARY KEY AUTOINCREMENT. Unique identifier for the student profile.")
    add_bullet_item("user_id", "INTEGER NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE. Foreign key to the user account.")
    add_bullet_item("roll_number", "VARCHAR(30) NOT NULL UNIQUE. University student registration number.")
    add_bullet_item("block_id", "INTEGER NOT NULL REFERENCES block(block_id) ON DELETE RESTRICT. Assigned hostel block.")
    add_bullet_item("room_number", "VARCHAR(20) NOT NULL. Specific residential room number.")
    add_bullet_item("phone", "VARCHAR(20). Contact telephone number.")
    add_bullet_item("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP. Profile creation timestamp.")

    add_heading_2("5.4 Entity: warden")
    add_body_p("Maintains administrative credentials and supervisory authority for hostel wardens.")
    add_bullet_item("warden_id", "INTEGER PRIMARY KEY AUTOINCREMENT. Unique identifier for the warden profile.")
    add_bullet_item("user_id", "INTEGER NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE. Foreign key to the user account.")
    add_bullet_item("employee_id", "VARCHAR(30) NOT NULL UNIQUE. Institutional employee identification code.")
    add_bullet_item("phone", "VARCHAR(20). Official contact number for maintenance dispatches.")
    add_bullet_item("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP. Profile initialization timestamp.")

    add_heading_2("5.5 Entity: complaint")
    add_body_p("The central transaction entity recording student grievances, AI priority assessments, media evidence, and lifecycle states.")
    add_bullet_item("complaint_id", "INTEGER PRIMARY KEY AUTOINCREMENT. Unique surrogate key identifying the complaint.")
    add_bullet_item("student_id", "INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE. Originating student.")
    add_bullet_item("block_id", "INTEGER NOT NULL REFERENCES block(block_id) ON DELETE RESTRICT. Location of the grievance.")
    add_bullet_item("title", "VARCHAR(200) NOT NULL. Concise summary of the maintenance grievance.")
    add_bullet_item("description", "TEXT NOT NULL. Detailed narrative explaining the malfunction or safety hazard.")
    add_bullet_item("category", "VARCHAR(50) NOT NULL. Classification (Electrical, Plumbing, Carpentry, Internet, Cleanliness, Safety).")
    add_bullet_item("priority_score", "INTEGER NOT NULL DEFAULT 50 CHECK (priority_score BETWEEN 0 AND 100). LLM-computed risk index.")
    add_bullet_item("status", "VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Resolved')).")
    add_bullet_item("media_url", "VARCHAR(255). Relative web path to attached photograph or video evidence.")
    add_bullet_item("media_type", "VARCHAR(20). MIME category ('image' or 'video') informing browser rendering.")
    add_bullet_item("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP. Lodging timestamp.")
    add_bullet_item("resolved_at", "DATETIME. Timestamp when warden marked the grievance as Resolved.")

    add_heading_2("5.6 Entity Relationships & Cardinalities")
    add_bullet_item("users to student (1 : 0..1)", 
        "Each user record corresponds to at most one student profile. When a user is deleted, the student profile is deleted in cascade.")
    add_bullet_item("users to warden (1 : 0..1)", 
        "Each user record corresponds to at most one warden profile.")
    add_bullet_item("block to student (1 : N)", 
        "A hostel block houses many students. Deletion of a block is restricted while active students reside within it.")
    add_bullet_item("block to complaint (1 : N)", 
        "A hostel block accumulates multiple complaints over time, facilitating block-level maintenance analytics.")
    add_bullet_item("student to complaint (1 : N)", 
        "A student can lodge multiple maintenance grievances across their academic tenure.")

    # =========================================================================
    # CHAPTER 6: RELATIONAL SCHEMA
    # =========================================================================
    add_chapter_title("6. Relational Schema")
    add_body_p(
        "The relational schema is formalized below with primary keys underlined and foreign key dependencies explicitly declared:"
    )
    add_code_block(
        "users (user_id [PK], name, email [UQ], password_hash, role, created_at)\n\n"
        "block (block_id [PK], name, code [UQ], description, created_at)\n\n"
        "student (student_id [PK], user_id [FK -> users.user_id, UQ], roll_number [UQ],\n"
        "         block_id [FK -> block.block_id], room_number, phone, created_at)\n\n"
        "warden (warden_id [PK], user_id [FK -> users.user_id, UQ], employee_id [UQ],\n"
        "        phone, created_at)\n\n"
        "complaint (complaint_id [PK], student_id [FK -> student.student_id],\n"
        "           block_id [FK -> block.block_id], title, description, category,\n"
        "           priority_score, status, media_url, media_type, created_at, resolved_at)"
    )

    add_heading_2("6.1 Primary and Foreign Key Integrity")
    add_bullet_item("Primary Keys", 
        "Every entity utilizes an AUTOINCREMENT surrogate integer primary key (user_id, block_id, student_id, warden_id, complaint_id). "
        "Surrogate keys decouple relational join performance from mutable business identifiers such as email or roll number.")
    add_bullet_item("Foreign Key Constraints", 
        "student.user_id references users.user_id with ON DELETE CASCADE. If an institutional account is decommissioned, "
        "its associated student profile is purged automatically. Similarly, complaint.student_id references student.student_id with ON DELETE CASCADE.")
    add_bullet_item("Restricted Deletes", 
        "complaint.block_id references block.block_id with ON DELETE RESTRICT. A hostel block cannot be deleted from the database if active "
        "complaints are linked to it, preserving audit integrity.")

    add_heading_2("6.2 Domain Constraints & Check Validation")
    add_bullet_item("Priority Score Range", 
        "CHECK (priority_score >= 0 AND priority_score <= 100). Prevents erroneous or malformed scores from corrupting queue sorting.")
    add_bullet_item("Lifecycle Status Integrity", 
        "CHECK (status IN ('Pending', 'In Progress', 'Resolved')). Restricts complaints strictly to valid lifecycle states.")
    add_bullet_item("Role Authorization Scope", 
        "CHECK (role IN ('student', 'warden')). Ensures that only legitimate institutional roles can access protected system boundaries.")

    add_heading_2("6.3 Indexing Strategy for High-Throughput Sorting")
    add_body_p(
        "In a busy university campus housing 5,000 students, the complaint table experiences thousands of entries per semester. "
        "Without proper indexing, rendering the warden command queue requires a full table scan (O(N) time complexity). "
        "To guarantee sub-50ms execution, the following B-Tree indexes are defined:"
    )
    add_code_block(
        "-- Index for high-speed priority queue sorting (Descending order)\n"
        "CREATE INDEX idx_complaint_priority_desc ON complaint(priority_score DESC);\n\n"
        "-- Composite index for block-level and status-level operational filtering\n"
        "CREATE INDEX idx_complaint_status_block ON complaint(status, block_id);\n\n"
        "-- Index for accelerating student history timeline retrieval\n"
        "CREATE INDEX idx_complaint_student_created ON complaint(student_id, created_at DESC);"
    )

    # =========================================================================
    # CHAPTER 7: IMPLEMENTATION
    # =========================================================================
    add_chapter_title("7. Implementation")
    add_heading_2("7.1 Database Setup and Execution Environment")
    add_body_p(
        "The project is implemented using an asynchronous Python FastAPI architecture with SQLite. The setup workflow is as follows:"
    )
    add_bullet_item("Step 1: Virtual Environment Initialization", 
        "A dedicated Python virtual environment is provisioned: python3 -m venv .venv followed by source .venv/bin/activate.")
    add_bullet_item("Step 2: Dependency Installation", 
        "Install production dependencies: pip install fastapi uvicorn pydantic requests python-multipart passlib[bcrypt] pyjwt.")
    add_bullet_item("Step 3: Database & Media Storage Provisioning", 
        "The application automatically creates the SQLite database hostel.db and provisions the uploads/ directory for multipart media storage.")
    add_bullet_item("Step 4: Launching Local LLM & Backend Server", 
        "Start Ollama service via ollama run llama3 (or mistral). Execute the FastAPI backend daemon: uvicorn backend_py.main:app --port 3000 --reload.")
    add_bullet_item("Step 5: Frontend Build & Dev Server", 
        "Inside the frontend directory, execute npm install followed by npm run dev. The application binds to http://localhost:5173.")

    add_heading_2("7.2 Table Creation Scripts (SQL DDL)")
    add_body_p(
        "The complete Data Definition Language (DDL) scripts executed to initialize the normalized schema are presented below:"
    )
    add_code_block(
        "CREATE TABLE IF NOT EXISTS users (\n"
        "    user_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    name VARCHAR(100) NOT NULL,\n"
        "    email VARCHAR(150) NOT NULL UNIQUE,\n"
        "    password_hash VARCHAR(255) NOT NULL,\n"
        "    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'warden')),\n"
        "    created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n"
        ");\n\n"
        "CREATE TABLE IF NOT EXISTS block (\n"
        "    block_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    name VARCHAR(50) NOT NULL,\n"
        "    code VARCHAR(10) NOT NULL UNIQUE,\n"
        "    description TEXT,\n"
        "    created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n"
        ");\n\n"
        "CREATE TABLE IF NOT EXISTS student (\n"
        "    student_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    user_id INTEGER NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,\n"
        "    roll_number VARCHAR(30) NOT NULL UNIQUE,\n"
        "    block_id INTEGER NOT NULL REFERENCES block(block_id) ON DELETE RESTRICT,\n"
        "    room_number VARCHAR(20) NOT NULL,\n"
        "    phone VARCHAR(20),\n"
        "    created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n"
        ");\n\n"
        "CREATE TABLE IF NOT EXISTS warden (\n"
        "    warden_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    user_id INTEGER NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,\n"
        "    employee_id VARCHAR(30) NOT NULL UNIQUE,\n"
        "    phone VARCHAR(20),\n"
        "    created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n"
        ");\n\n"
        "CREATE TABLE IF NOT EXISTS complaint (\n"
        "    complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,\n"
        "    block_id INTEGER NOT NULL REFERENCES block(block_id) ON DELETE RESTRICT,\n"
        "    title VARCHAR(200) NOT NULL,\n"
        "    description TEXT NOT NULL,\n"
        "    category VARCHAR(50) NOT NULL,\n"
        "    priority_score INTEGER NOT NULL DEFAULT 50 CHECK (priority_score BETWEEN 0 AND 100),\n"
        "    status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Resolved')),\n"
        "    media_url VARCHAR(255),\n"
        "    media_type VARCHAR(20),\n"
        "    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,\n"
        "    resolved_at DATETIME\n"
        ");"
    )

    add_heading_2("7.3 Stored Analytical Views and Complex SQL Queries")
    add_body_p(
        "To provide actionable administrative insights, the backend utilizes parameterized SQL queries and analytical views:"
    )
    add_code_block(
        "-- Query 1: Priority Queue Retrieval with Student & Block Relational Joins\n"
        "SELECT \n"
        "    c.complaint_id, c.title, c.category, c.priority_score, c.status,\n"
        "    c.media_url, c.media_type, c.created_at,\n"
        "    u.name AS student_name, s.roll_number, s.room_number,\n"
        "    b.name AS block_name, b.code AS block_code\n"
        "FROM complaint c\n"
        "JOIN student s ON c.student_id = s.student_id\n"
        "JOIN users u ON s.user_id = u.user_id\n"
        "JOIN block b ON c.block_id = b.block_id\n"
        "WHERE c.status != 'Resolved'\n"
        "ORDER BY c.priority_score DESC, c.created_at ASC;\n\n"
        "-- Query 2: Block-Level Maintenance Performance & Resolution Analytics\n"
        "SELECT \n"
        "    b.code AS hostel_block,\n"
        "    COUNT(c.complaint_id) AS total_complaints,\n"
        "    SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,\n"
        "    SUM(CASE WHEN c.priority_score >= 80 THEN 1 ELSE 0 END) AS emergency_count,\n"
        "    ROUND(AVG(c.priority_score), 1) AS average_risk_score\n"
        "FROM block b\n"
        "LEFT JOIN complaint c ON b.block_id = c.block_id\n"
        "GROUP BY b.block_id\n"
        "ORDER BY total_complaints DESC;"
    )

    add_heading_2("7.4 Local LLM Integration & Prompt Engineering")
    add_body_p(
        "The triage engine communicates with the local Ollama API via synchronous/asynchronous HTTP POST requests. "
        "The system prompt instructs the model to return valid JSON containing priority assessment fields:"
    )
    add_code_block(
        "SYSTEM_PROMPT = \"\"\"\n"
        "You are an expert university hostel triage officer. Evaluate the student complaint.\n"
        "Return ONLY a JSON object with:\n"
        "{\n"
        "  \"priority_score\": <integer 0-100>,\n"
        "  \"category\": <\"Electrical\" | \"Plumbing\" | \"Carpentry\" | \"Internet\" | \"Cleanliness\" | \"Safety\">,\n"
        "  \"severity\": <\"High\" | \"Medium\" | \"Low\">,\n"
        "  \"reasoning\": <concise 1-sentence explanation of life safety or structural risk>\n"
        "}\n"
        "Scoring Guide:\n"
        "- 85-100: Critical hazard (sparking wire, fire, burst water pipe, lock failure)\n"
        "- 60-84:  Disruptive failure (no water in washroom, complete Wi-Fi blackout, ceiling fan breakdown)\n"
        "- 20-59:  Routine inconvenience (loose study chair, slow internet, bulb replacement)\n"
        "\"\"\""
    )

    # =========================================================================
    # CHAPTER 8: USER INTERFACE
    # =========================================================================
    add_chapter_title("8. User Interface")
    add_body_p(
        "The user interface has been designed from the ground up using a clean, modern white theme (#ffffff background, "
        "#f8fafc slate card surfaces, #e2e8f0 borders, and #2563eb royal blue primary accents). This aesthetic completely "
        "replaces dark modes with high-contrast, institutional-grade readability. All functional screens were verified "
        "and captured live from the running system."
    )

    add_heading_2("8.1 Screenshots of the Running System")

    add_figure("01_login_page.png", 
        "Figure 2: Clean White Authentication Portal with Role Selection and Demo Credentials")
    add_body_p(
        "Figure 2 illustrates the primary authentication screen. Users can sign in using their institutional email and "
        "password. Convenient quick-fill buttons allow immediate testing for Chief Warden and Student personas without typing."
    )

    add_figure("02_registration_page.png", 
        "Figure 3: Student & Warden Registration Portal with Institutional Block and Room Mapping")
    add_body_p(
        "Figure 3 displays the registration workflow. Students select their assigned hostel block (Block A through D), "
        "specify room numbers, and establish bcrypt-hashed credentials."
    )

    add_figure("03_warden_command_center.png", 
        "Figure 4: Warden Executive Command Center with Priority Queue (100 to 0) and Block Filtering")
    add_body_p(
        "Figure 4 shows the Warden Executive Command Center. Maintenance grievances are ranked strictly in descending "
        "order of priority_score. Critical hazards (such as sparking switchboards with score 94) appear at the top with "
        "red emergency badges, followed by moderate and routine issues."
    )

    add_figure("04_warden_local_llm_settings_modal.png", 
        "Figure 5: Warden Local LLM Priority Engine Settings & Model Selection Configuration Modal")
    add_body_p(
        "Figure 5 highlights the Local LLM Configuration Modal. Wardens can select active local Ollama models (Llama 3, "
        "Mistral, DeepSeek), test connection latency, and toggle heuristic fallback parameters without cloud subscriptions."
    )

    add_figure("05_warden_complaint_telemetry_modal.png", 
        "Figure 6: Warden Complaint Telemetry Modal with Detailed LLM Risk Analysis and Reasoning")
    add_body_p(
        "Figure 6 depicts the complaint inspection telemetry modal, showing the exact AI reasoning, calculated score, "
        "student contact details, and timestamp history."
    )

    add_figure("06_student_grievance_portal.png", 
        "Figure 7: Student Grievance Lodging Portal with Live Form Validation")
    add_body_p(
        "Figure 7 shows the student grievance portal. Students provide a title, category, narrative description, and "
        "have the option to attach photographic or video proof."
    )

    add_figure("07_student_live_ai_triage_preview.png", 
        "Figure 8: Student Live AI Triage Preview Dynamically Computing Priority Score While Typing")
    add_body_p(
        "Figure 8 demonstrates the real-time debounced AI triage preview. As the student types an electrical sparking narrative, "
        "the local engine immediately computes a Priority Score of 94/100 and displays an emergency alert badge."
    )

    add_figure("08_student_complaints_timeline_tracker.png", 
        "Figure 9: Student Grievance Timeline Tracker Showing End-to-End Status Progression")
    add_body_p(
        "Figure 9 depicts the student complaint history portal. Students track their grievance lifecycle through "
        "Pending, In Progress, and Resolved stages with visual timestamp milestones."
    )

    add_figure("09_account_profile_page.png", 
        "Figure 10: Institutional Account Profile Screen Showing Role, Block, and Contact Information")
    add_body_p(
        "Figure 10 shows the user profile screen displaying authenticated session metadata, verified hostel block, and room mapping."
    )

    add_figure("10_fastapi_swagger_api_docs.png", 
        "Figure 11: Interactive FastAPI Swagger OpenAPI Documentation at /docs")
    add_body_p(
        "Figure 11 showcases the backend OpenAPI / Swagger documentation at http://localhost:3000/docs, documenting all REST "
        "endpoints, request schemas, and authentication headers."
    )

    add_figure("12_student_media_evidence_upload.png", 
        "Figure 12: Student Grievance Submission with Photographic and Video Evidence Upload")
    add_body_p(
        "Figure 12 illustrates the multi-media upload interface. Students can upload photos and video evidence (.mp4, .png, .jpg) "
        "demonstrating physical damage with real-time file size indicators and removal controls."
    )

    add_figure("13_warden_media_evidence_telemetry.png", 
        "Figure 13: Warden Multi-Media Evidence Inspection Modal with Full-Resolution Image and Video Playback")
    add_body_p(
        "Figure 13 demonstrates the warden evidence telemetry modal. Wardens can stream video recordings and inspect high-resolution "
        "photographs directly within the browser, verifying contractor repairs before closing complaints."
    )

    add_heading_2("8.2 Operational Usage Instructions")
    add_body_p(
        "The following operational workflows guide students and hostel wardens in interacting with the system:"
    )
    add_heading_3("Student Workflow:")
    add_bullet_item("1. Login", "Navigate to http://localhost:5173 and log in with student credentials, or click 'Student Demo'.")
    add_bullet_item("2. Lodge Grievance", "Click 'Report Complaint' in the top navigation. Enter a concise title and select the category.")
    add_bullet_item("3. Live AI Preview", "Type the problem description. Observe the live AI preview card calculating the priority score in real-time.")
    add_bullet_item("4. Attach Proof", "Click 'Upload Evidence' to attach an image or video file showing the physical breakdown.")
    add_bullet_item("5. Submit & Track", "Submit the grievance and monitor its status in real-time under 'My Complaints'.")

    add_heading_3("Warden Workflow:")
    add_bullet_item("1. Access Dashboard", "Sign in with warden credentials, or click 'Chief Warden' on the login screen.")
    add_bullet_item("2. Triage Queue", "Inspect the complaint queue. Notice that critical emergencies (Score >= 80) are pinned at the top.")
    add_bullet_item("3. Inspect Evidence", "Click on any complaint card to view the student's attached photo or stream video evidence.")
    add_bullet_item("4. Update Lifecycle", "Transition status from 'Pending' to 'In Progress' when technicians are dispatched, and to 'Resolved' upon repair.")
    add_bullet_item("5. Configure AI Engine", "Click 'AI Settings' in the header to switch between local Ollama models or inspect heuristic rules.")

    # =========================================================================
    # CHAPTER 9: CONCLUSION
    # =========================================================================
    add_chapter_title("9. Conclusion")
    add_body_p(
        "The Intelligent Hostel Complaint Management System successfully demonstrates how modern Database Management System "
        "(DBMS) principles can be synergized with on-premise Large Language Models to solve critical campus infrastructure challenges. "
        "By replacing paper registers with a normalized, indexed relational database, the system eliminates lost complaints, enforces "
        "referential integrity, and provides sub-50ms query performance."
    )
    add_body_p(
        "The integration of local LLM priority triage fundamentally shifts hostel administration from arbitrary First-Come First-Served "
        "processing to risk-driven triage. Life-safety hazards such as electrical sparking and severe flooding are escalated "
        "immediately to wardens with computed priority scores (0-100), while non-critical repairs are queued systematically. "
        "Furthermore, by hosting quantized models locally via Ollama with zero-cloud API calls, the system guarantees 100% student data "
        "privacy and eliminates recurring commercial software licensing costs."
    )
    add_body_p(
        "The multi-media evidence pipeline provides irrefutable ground truth, eliminating contractor disputes and reducing technician "
        "turnaround time. The clean, professional white aesthetic ensures an intuitive user experience for both students and hostel staff."
    )
    add_body_p(
        "Future Enhancements include: (1) An automated WhatsApp bot dispatching notifications to maintenance technicians; "
        "(2) A technician mobile application with QR-code room scanning to verify on-site arrival; (3) Predictive maintenance analytics "
        "forecasting plumbing and electrical fixture failures based on historical seasonal trends."
    )

    # =========================================================================
    # CHAPTER 10: REFERENCES
    # =========================================================================
    add_chapter_title("10. References")
    add_bullet_item("1. FastAPI Framework Documentation", "Tiangolo, S. (2024). FastAPI: High-performance modern Python web framework. Available at: https://fastapi.tiangolo.com/")
    add_bullet_item("2. SQLite 3 Database Engine", "Hipp, D. R. (2024). SQLite: An In-Process Relational Database Engine. Available at: https://www.sqlite.org/docs.html")
    add_bullet_item("3. Ollama Local LLM Runner", "Ollama Team (2024). Get up and running with large language models locally. Available at: https://ollama.com/")
    add_bullet_item("4. Database System Concepts (7th Ed.)", "Silberschatz, A., Korth, H. F., & Sudarshan, S. (2020). Database System Concepts. McGraw-Hill Education, New York.")
    add_bullet_item("5. React 18 Library Documentation", "Meta Open Source (2024). React: A JavaScript library for building user interfaces. Available at: https://react.dev/")
    add_bullet_item("6. Vite Next Generation Frontend Tooling", "You, E. (2024). Vite: Next Generation Frontend Tooling. Available at: https://vitejs.dev/")
    add_bullet_item("7. Tailwind CSS Documentation", "Wathan, A. (2024). Tailwind CSS: A utility-first CSS framework. Available at: https://tailwindcss.com/")
    add_bullet_item("8. Python Cryptographic Libraries (Passlib & PyJWT)", "Curchod, E. et al. (2024). Password hashing and JSON Web Tokens in Python. Available at: https://passlib.readthedocs.io/")

    # Save to target locations
    output_main = "DCDSL PROJECT REPORT format.docx"
    output_dcds = os.path.join("docs", "DCDS_PROJECT_REPORT.docx")
    output_dcdsl = os.path.join("docs", "DCDSL_PROJECT_REPORT.docx")

    doc.save(output_main)
    doc.save(output_dcds)
    doc.save(output_dcdsl)
    print(f"Successfully saved '{output_main}', '{output_dcds}', and '{output_dcdsl}'!")
    print(f"Final paragraph count: {len(doc.paragraphs)}")

if __name__ == "__main__":
    build_report()
