"""
FastAPI Backend for Intelligent Hostel Complaint Management System.
Features:
- Full JWT authentication & Role-Based Access Control (Student, Warden, Admin)
- Dual Local LLM Priority Engine (Ollama + Embedded Local NLP Classifier)
- Real-time AI urgency triage on complaint submission
- Batch AI re-prioritization for Wardens
- Full compatibility with existing frontend endpoints + extended intelligence APIs
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import uuid
import shutil

from fastapi import FastAPI, HTTPException, Header, Depends, Query, status, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import jwt

from .database import (
    init_db, get_db, hash_password, verify_password
)
from .llm_service import (
    prioritize_complaint, check_ollama_status, local_embedded_classifier
)

# Configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "hostel_secret_key_2026")
JWT_ALGORITHM = "HS256"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = FastAPI(
    title="Intelligent Hostel Complaint Management System API",
    description="Python FastAPI backend with Local LLM Priority Sorting",
    version="2.0.0"
)

# Enable CORS for frontend Vite dev server & production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for photo and video streaming
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.on_event("startup")
def on_startup():
    """Initialize SQLite database and seed realistic demo data."""
    init_db()
    print("✅ Database initialized successfully.")
    print("✅ Local LLM priority engine ready.")


# ============================================================================
# Pydantic Schemas
# ============================================================================

class UserRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    type: str  # 'student' or 'warden'
    block_id: Optional[int] = 1
    usn: Optional[str] = None
    room: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class ComplaintCreateRequest(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: str
    room: str
    block_id: Optional[int] = None
    preferred_model: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class ComplaintUpdateRequest(BaseModel):
    status: Optional[str] = None  # PENDING, IN_PROGRESS, RESOLVED, REJECTED
    is_completed: Optional[bool] = None
    warden_notes: Optional[str] = None


class PriorityPreviewRequest(BaseModel):
    title: str
    description: str
    room: Optional[str] = ""
    block_id: Optional[int] = None


# ============================================================================
# Auth Helpers
# ============================================================================

def create_jwt_token(user_id: int, user_type: str) -> str:
    payload = {
        "user": {
            "user_id": user_id,
            "type": user_type
        },
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Strip 'Bearer ' if present
    token = authorization.replace("Bearer ", "").strip()
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================================================
# Root and Health Endpoints
# ============================================================================

@app.get("/")
@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "Intelligent Hostel Complaint Management System API",
        "version": "2.0.0",
        "ai_engine": "Local LLM Priority Triage (Ollama llama3.2 / regex fallback)",
        "media_uploads_enabled": True
    }


# ============================================================================
# Media Evidence Upload Endpoint (Photos & Videos)
# ============================================================================

@app.post("/api/upload")
async def upload_media(
    file: UploadFile = File(...),
    auth: Dict[str, Any] = Depends(decode_jwt_token)
):
    """
    Upload photo or video evidence for complaints.
    Supports JPEG, PNG, WEBP, GIF, HEIC, MP4, MOV, WEBM, M4V, AVI.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = os.path.splitext(file.filename)[1].lower()
    image_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic"}
    video_exts = {".mp4", ".mov", ".webm", ".m4v", ".avi"}

    if ext in image_exts:
        media_type = "image"
    elif ext in video_exts:
        media_type = "video"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Please upload an image (.jpg, .png, .webp) or video (.mp4, .mov, .webm)."
        )

    # Generate unique safe file name
    unique_prefix = uuid.uuid4().hex[:12]
    clean_name = f"{unique_prefix}_{file.filename.replace(' ', '_')}"
    target_path = os.path.join(UPLOADS_DIR, clean_name)

    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    file_size = os.path.getsize(target_path)
    relative_url = f"/uploads/{clean_name}"

    return {
        "url": f"http://localhost:3000{relative_url}",
        "relative_url": relative_url,
        "filename": file.filename,
        "media_type": media_type,
        "size_bytes": file_size
    }


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/register")
@app.post("/api/register")
def register(req: UserRegisterRequest):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE email = ?;", (req.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pw = hash_password(req.password)
    cursor.execute(
        "INSERT INTO users (full_name, email, phone, password, type) VALUES (?, ?, ?, ?, ?);",
        (req.full_name, req.email, req.phone, hashed_pw, req.type)
    )
    user_id = cursor.lastrowid

    if req.type == "student":
        cursor.execute(
            "INSERT INTO student (student_id, block_id, usn, room) VALUES (?, ?, ?, ?);",
            (user_id, req.block_id or 1, req.usn or "NA", req.room or "NA")
        )
    elif req.type == "warden":
        cursor.execute(
            "INSERT INTO warden (warden_id, block_id) VALUES (?, ?);",
            (user_id, req.block_id or 1)
        )

    conn.commit()
    conn.close()

    token = create_jwt_token(user_id, req.type)
    return {"jwtToken": token, "user": {"user_id": user_id, "type": req.type, "full_name": req.full_name}}


@app.post("/login")
@app.post("/api/login")
def login(req: UserLoginRequest):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?;", (req.email,))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials. Please check your email and password.")

    token = create_jwt_token(user["user_id"], user["type"])
    return {
        "jwtToken": token,
        "user": {
            "user_id": user["user_id"],
            "type": user["type"],
            "full_name": user["full_name"],
            "email": user["email"]
        }
    }


@app.get("/userType")
@app.get("/api/userType")
def get_user_type(auth: Dict[str, Any] = Depends(decode_jwt_token)):
    user_info = auth.get("user", {})
    return {
        "userType": user_info.get("type"),
        "userId": user_info.get("user_id"),
        "user_id": user_info.get("user_id")
    }


@app.get("/userDetails/{user_id}")
@app.get("/api/userDetails/{user_id}")
def get_user_details(user_id: str, auth: Dict[str, Any] = Depends(decode_jwt_token)):
    conn = get_db()
    cursor = conn.cursor()

    caller = auth.get("user", {})
    if str(user_id).lower() in ("me", "0", "current"):
        target_id = caller.get("user_id")
    else:
        try:
            target_id = int(user_id) if caller.get("type") == "warden" else caller.get("user_id")
        except (ValueError, TypeError):
            target_id = caller.get("user_id")

    cursor.execute("SELECT user_id, full_name, email, phone, type FROM users WHERE user_id = ?;", (target_id,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = dict(user_row)
    if user_dict["type"] == "student":
        cursor.execute("""
            SELECT s.usn, s.room, b.block_id, b.block_name
            FROM student s
            LEFT JOIN block b ON s.block_id = b.block_id
            WHERE s.student_id = ?;
        """, (target_id,))
        student_row = cursor.fetchone()
        if student_row:
            user_dict.update(dict(student_row))
    elif user_dict["type"] == "warden":
        cursor.execute("""
            SELECT w.block_id, b.block_name
            FROM warden w
            LEFT JOIN block b ON w.block_id = b.block_id
            WHERE w.warden_id = ?;
        """, (target_id,))
        warden_row = cursor.fetchone()
        if warden_row:
            user_dict.update(dict(warden_row))

    conn.close()
    # Returns a list format matching legacy frontend expectations: [user_dict]
    return [user_dict]


@app.get("/student/{student_id}")
def get_student_by_id(student_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.full_name, u.email, u.phone, s.usn, s.room, b.block_name
        FROM users u
        JOIN student s ON u.user_id = s.student_id
        LEFT JOIN block b ON s.block_id = b.block_id
        WHERE u.user_id = ?;
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")
    return dict(row)


@app.get("/warden/{warden_id}")
def get_warden_by_id(warden_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.full_name, u.email, u.phone, b.block_name
        FROM users u
        JOIN warden w ON u.user_id = w.warden_id
        LEFT JOIN block b ON w.block_id = b.block_id
        WHERE u.user_id = ?;
    """, (warden_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Warden not found")
    return dict(row)


# ============================================================================
# Complaints & AI Priority Endpoints
# ============================================================================

@app.get("/complaints")
@app.get("/api/complaints")
def get_complaints(
    sort_by_priority: bool = Query(False, description="Sort complaints by AI Priority Score descending"),
    status: Optional[str] = Query(None, description="Filter by status (PENDING, IN_PROGRESS, RESOLVED)"),
    priority: Optional[str] = Query(None, description="Filter by priority tier (CRITICAL, HIGH, MEDIUM, LOW)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    block_id: Optional[int] = Query(None, description="Filter by hostel block"),
    search: Optional[str] = Query(None, description="Search keyword in title/description/room"),
    auth: Dict[str, Any] = Depends(decode_jwt_token)
):
    caller = auth.get("user", {})
    user_id = caller.get("user_id")
    user_type = caller.get("type")

    conn = get_db()
    cursor = conn.cursor()

    query_parts = [
        """SELECT c.*, b.block_name, u.full_name as student_name, u.phone as student_phone, s.usn as student_usn
           FROM complaint c
           LEFT JOIN block b ON c.block_id = b.block_id
           LEFT JOIN users u ON c.student_id = u.user_id
           LEFT JOIN student s ON c.student_id = s.student_id
           WHERE 1=1"""
    ]
    params: List[Any] = []

    if user_type == "student":
        # Students see only their own complaints
        query_parts.append("AND c.student_id = ?")
        params.append(user_id)
    elif user_type == "warden":
        # Wardens can apply filters
        if status and status.upper() != "ALL":
            if status.upper() == "RESOLVED":
                query_parts.append("AND (c.status = 'RESOLVED' OR c.is_completed = 1)")
            elif status.upper() == "PENDING":
                query_parts.append("AND (c.status = 'PENDING' AND (c.is_completed = 0 OR c.is_completed IS NULL))")
            elif status.upper() == "IN_PROGRESS":
                query_parts.append("AND c.status = 'IN_PROGRESS'")
        if priority and priority.upper() != "ALL":
            query_parts.append("AND c.priority = ?")
            params.append(priority.upper())
        if category and category.upper() != "ALL":
            query_parts.append("AND c.category = ?")
            params.append(category)
        if block_id:
            query_parts.append("AND c.block_id = ?")
            params.append(block_id)
        if search:
            query_parts.append("AND (c.name LIKE ? OR c.description LIKE ? OR c.room LIKE ?)")
            term = f"%{search}%"
            params.extend([term, term, term])

    # Sorting
    if sort_by_priority:
        # Sort by urgency score descending, unresolved first, then created_at
        query_parts.append("ORDER BY c.is_completed ASC, c.priority_score DESC, c.created_at DESC")
    else:
        query_parts.append("ORDER BY c.created_at DESC")

    full_query = " ".join(query_parts)
    cursor.execute(full_query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


@app.post("/complaints")
@app.post("/api/complaints")
async def create_complaint(
    req: ComplaintCreateRequest,
    auth: Dict[str, Any] = Depends(decode_jwt_token)
):
    caller = auth.get("user", {})
    user_id = caller.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    # Look up student's registered block
    cursor.execute("SELECT block_id, room FROM student WHERE student_id = ?;", (user_id,))
    student_info = cursor.fetchone()
    student_block_id = student_info["block_id"] if student_info else 1
    student_room = req.room or (student_info["room"] if student_info else "NA")

    # Fetch block name for contextual LLM prompt
    cursor.execute("SELECT block_name FROM block WHERE block_id = ?;", (student_block_id,))
    block_row = cursor.fetchone()
    block_name = block_row["block_name"] if block_row else "Campus Hostel"

    title = req.title or req.name or (req.description[:50] + "...")

    # Run Local LLM / Embedded Priority Analysis
    ai_result = await prioritize_complaint(
        title=title,
        description=req.description,
        room=student_room,
        block=block_name,
        preferred_model=req.preferred_model
    )

    cursor.execute("""
        INSERT INTO complaint (
            name, block_id, student_id, description, room, is_completed, status,
            priority, priority_score, category, urgency_reason, suggested_action,
            sla_hours, ai_engine, media_url, media_type, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        title,
        student_block_id,
        user_id,
        req.description,
        student_room,
        0,
        "PENDING",
        ai_result["priority"],
        ai_result["priority_score"],
        ai_result["category"],
        ai_result["urgency_reason"],
        ai_result["suggested_action"],
        ai_result["sla_hours"],
        ai_result["ai_engine"],
        req.media_url,
        req.media_type,
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ))

    complaint_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT * FROM complaint WHERE id = ?;", (complaint_id,))
    created_complaint = cursor.fetchone()
    conn.close()

    return dict(created_complaint)


@app.post("/complaints/{complaint_id}")
@app.put("/complaints/{complaint_id}")
@app.put("/api/complaints/{complaint_id}")
def update_complaint_status(
    complaint_id: int,
    req: Optional[ComplaintUpdateRequest] = None,
    auth: Dict[str, Any] = Depends(decode_jwt_token)
):
    caller = auth.get("user", {})
    if caller.get("type") != "warden":
        raise HTTPException(status_code=403, detail="Only hostel wardens can update complaint status")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaint WHERE id = ?;", (complaint_id,))
    comp = cursor.fetchone()
    if not comp:
        conn.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    # If payload provided, update accordingly
    if req and req.status:
        new_status = req.status.upper()
        is_completed = 1 if new_status == "RESOLVED" else 0
        resolved_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") if new_status == "RESOLVED" else None
        warden_notes = req.warden_notes or comp["warden_notes"]

        cursor.execute("""
            UPDATE complaint
            SET status = ?, is_completed = ?, resolved_at = ?, warden_notes = ?, assigned_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (new_status, is_completed, resolved_at, warden_notes, complaint_id))
    else:
        # Default legacy behavior: toggle completed status
        current_status = comp["is_completed"]
        new_completed = 0 if current_status else 1
        new_status = "RESOLVED" if new_completed else "IN_PROGRESS"
        resolved_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") if new_completed else None

        cursor.execute("""
            UPDATE complaint
            SET is_completed = ?, status = ?, resolved_at = ?, assigned_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (new_completed, new_status, resolved_at, complaint_id))

    conn.commit()
    cursor.execute("SELECT * FROM complaint WHERE id = ?;", (complaint_id,))
    updated = cursor.fetchone()
    conn.close()

    return dict(updated)


@app.delete("/complaints/{complaint_id}")
@app.delete("/api/complaints/{complaint_id}")
def delete_complaint(
    complaint_id: int,
    auth: Dict[str, Any] = Depends(decode_jwt_token)
):
    caller = auth.get("user", {})
    if caller.get("type") != "warden":
        raise HTTPException(status_code=403, detail="Only hostel wardens can delete complaints")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM complaint WHERE id = ?;", (complaint_id,))
    conn.commit()
    conn.close()
    return {"message": "Complaint deleted successfully", "id": complaint_id}


# ============================================================================
# Warden Intelligence & Batch AI Endpoints
# ============================================================================

@app.post("/api/ai/preview-priority")
async def preview_priority(req: PriorityPreviewRequest):
    """Real-time priority preview as student types their complaint."""
    return await prioritize_complaint(
        title=req.title,
        description=req.description,
        room=req.room or "",
        block=f"Block {req.block_id}" if req.block_id else ""
    )


@app.post("/api/ai/batch-prioritize")
async def batch_prioritize(
    preferred_model: Optional[str] = None,
    auth: Dict[str, Any] = Depends(decode_jwt_token)
):
    """Re-analyze and sort all active/pending complaints using Local LLM."""
    caller = auth.get("user", {})
    if caller.get("type") != "warden":
        raise HTTPException(status_code=403, detail="Only hostel wardens can run batch AI priority triage")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, room, block_id FROM complaint WHERE is_completed = 0;")
    complaints = cursor.fetchall()

    updated_count = 0
    for comp in complaints:
        ai_res = await prioritize_complaint(
            title=comp["name"] or "",
            description=comp["description"],
            room=comp["room"] or "",
            preferred_model=preferred_model
        )
        cursor.execute("""
            UPDATE complaint
            SET priority = ?, priority_score = ?, category = ?, urgency_reason = ?,
                suggested_action = ?, sla_hours = ?, ai_engine = ?
            WHERE id = ?;
        """, (
            ai_res["priority"],
            ai_res["priority_score"],
            ai_res["category"],
            ai_res["urgency_reason"],
            ai_res["suggested_action"],
            ai_res["sla_hours"],
            ai_res["ai_engine"],
            comp["id"]
        ))
        updated_count += 1

    conn.commit()
    conn.close()

    return {"message": f"Successfully re-evaluated {updated_count} complaints with Local LLM", "count": updated_count}


@app.get("/api/ai/status")
async def get_ai_status():
    """Return local LLM (Ollama) connectivity and model status."""
    return await check_ollama_status()


@app.get("/api/warden/analytics")
def get_warden_analytics(auth: Dict[str, Any] = Depends(decode_jwt_token)):
    """Summary metrics for the Warden Command Center."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaint;")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaint WHERE priority = 'CRITICAL' AND is_completed = 0;")
    critical = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaint WHERE priority = 'HIGH' AND is_completed = 0;")
    high = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaint WHERE is_completed = 0 AND (status = 'PENDING' OR status IS NULL);")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaint WHERE status = 'IN_PROGRESS';")
    in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaint WHERE is_completed = 1 OR status = 'RESOLVED';")
    resolved = cursor.fetchone()[0]

    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM complaint 
        GROUP BY category 
        ORDER BY count DESC;
    """)
    category_breakdown = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "total": total,
        "critical": critical,
        "high": high,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "category_breakdown": category_breakdown
    }


@app.get("/api/blocks")
def get_blocks():
    """List all available hostel blocks."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM block ORDER BY block_id ASC;")
    blocks = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return blocks
