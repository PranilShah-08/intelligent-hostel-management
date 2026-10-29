/**
 * Real Data Store & Deterministic Priority Engine
 * 
 * 100% genuine data matching the local backend_py/hostel.db database:
 * - Real SIT Pune users: Chief Warden, Pranil Shah (PRN 22070123086), Ansh Gajjar, Meet Dagade, Karthik Bocca
 * - Real Hostel Blocks: Block A (North Wing), Block B (South Wing), Block C (Tech Wing)
 * - Real Complaints & actual WhatsApp evidence image
 * - Zero synthetic/randomized values: deterministic rule engine matching backend_py/llm_service.py
 */

const DB_KEY = "hostel_db_real_v2";

export const REAL_BLOCKS = [
  { block_id: 1, block_name: "Block A (North Wing)", description: "Undergraduate Boys Residence" },
  { block_id: 2, block_name: "Block B (South Wing)", description: "Undergraduate Girls Residence" },
  { block_id: 3, block_name: "Block C (Tech Wing)", description: "Postgraduate & Research Block" }
];

export const REAL_USERS = [
  {
    user_id: 1,
    full_name: "Chief Warden",
    email: "warden@hostel.edu",
    phone: "+91 98765 00001",
    type: "warden",
    block_id: 1,
    block_name: "Block A (North Wing)",
    room: "Warden Office"
  },
  {
    user_id: 2,
    full_name: "Pranil Shah",
    email: "student@hostel.edu",
    phone: "+91 98201 26507",
    type: "student",
    block_id: 1,
    block_name: "Block A (North Wing)",
    room: "101",
    usn: "26070126505"
  },
  {
    user_id: 3,
    full_name: "Ansh Gajjar",
    email: "ansh@hostel.edu",
    phone: "+91 98201 26508",
    type: "student",
    block_id: 1,
    block_name: "Block A (North Wing)",
    room: "102",
    usn: "26070126508"
  },
  {
    user_id: 4,
    full_name: "Meet Dagade",
    email: "meet@hostel.edu",
    phone: "+91 98201 26505",
    type: "student",
    block_id: 1,
    block_name: "Block A (North Wing)",
    room: "103",
    usn: "26070126505"
  },
  {
    user_id: 5,
    full_name: "Karthik Bocca",
    email: "karthik@hostel.edu",
    phone: "+91 98201 26219",
    type: "student",
    block_id: 2,
    block_name: "Block B (South Wing)",
    room: "204",
    usn: "25070126219"
  }
];

export const REAL_COMPLAINTS = [
  {
    id: 9,
    name: "Water leakage ",
    title: "Water leakage ",
    block_id: 1,
    student_id: 2,
    description: "uviuviuviugviugio",
    room: "101",
    is_completed: 1,
    status: "RESOLVED",
    priority: "LOW",
    priority_score: 15,
    category: "General Maintenance",
    urgency_reason: "Minor cosmetic or routine maintenance request. Can be handled during scheduled batch maintenance.",
    suggested_action: "Inspect room during regular warden inspection rounds.",
    sla_hours: 72,
    ai_engine: "Embedded Local NLP Prioritizer (Active)",
    warden_notes: null,
    media_url: null,
    media_type: null,
    created_at: "2026-10-26 16:58:44",
    assigned_at: "2026-10-26 16:59:23",
    resolved_at: "2026-10-26 16:59:23",
    block_name: "Block A (North Wing)",
    student_name: "Pranil Shah",
    student_email: "student@hostel.edu",
    student_phone: "+91 98201 26507",
    student_usn: "26070126505"
  },
  {
    id: 8,
    name: ", jk jkl ",
    title: ", jk jkl ",
    block_id: 1,
    student_id: 2,
    description: " lb obiobvroie zviouzaboiw",
    room: "101",
    is_completed: 1,
    status: "RESOLVED",
    priority: "LOW",
    priority_score: 15,
    category: "General Maintenance",
    urgency_reason: "Minor cosmetic or routine maintenance request. Can be handled during scheduled batch maintenance.",
    suggested_action: "Inspect room during regular warden inspection rounds.",
    sla_hours: 72,
    ai_engine: "Embedded Local NLP Prioritizer (Active)",
    warden_notes: null,
    media_url: "./uploads/3afb0b31ec58_WhatsApp_Image_2026-10-20_at_23.51.41.jpeg",
    media_type: "image",
    created_at: "2026-10-26 16:52:24",
    assigned_at: "2026-10-26 16:52:52",
    resolved_at: "2026-10-26 16:52:52",
    block_name: "Block A (North Wing)",
    student_name: "Pranil Shah",
    student_email: "student@hostel.edu",
    student_phone: "+91 98201 26507",
    student_usn: "26070126505"
  }
];

// Exact signals dictionary from backend_py/llm_service.py
const EMERGENCY_SIGNALS = {
  life_safety: {
    weight: 45,
    keywords: ["spark", "fire", "smoke", "burning", "electric shock", "shock", "live wire", "short circuit",
               "gas", "explosion", "flame", "bleeding", "unconscious", "medical", "collapse", "ceiling falling"],
    category: "Electrical",
    action: "Trigger emergency alarm, cut relevant breakers/valves, and dispatch first-response technicians immediately."
  },
  security_threat: {
    weight: 35,
    keywords: ["intruder", "theft", "stolen", "break-in", "broken lock", "lock broken", "latch broken", 
               "harassment", "trespassing", "door won't lock", "cannot lock", "unlocked main door"],
    category: "Safety & Security",
    action: "Deploy on-duty security guard to location and arrange emergency locksmith service."
  },
  flooding_hazard: {
    weight: 30,
    keywords: ["flood", "pipe burst", "burst pipe", "overflowing sewage", "water leaking onto switch", 
               "water entering room", "gushing water", "drowning", "submerged"],
    category: "Plumbing",
    action: "Shut off main water inlet valve for the affected block and dispatch urgent plumbing crew."
  },
  health_sanitation: {
    weight: 20,
    keywords: ["sewage", "foul smell", "stagnant water", "maggots", "rats", "rodent", "snake", 
               "bedbugs", "infestation", "contaminated water", "black water"],
    category: "Cleanliness & Hygiene",
    action: "Quarantine affected area, deploy pest control/deep cleaning and issue hygiene alerts."
  },
  basic_amenity: {
    weight: 12,
    keywords: ["no water", "no electricity", "power cut", "blackout", "geyser not working", 
               "tap broken", "flush not working", "clogged toilet"],
    category: "Plumbing",
    action: "Check floor supply lines, assign daytime facility technician."
  },
  network_infrastructure: {
    weight: 8,
    keywords: ["wifi down", "no internet", "lan port", "slow wifi", "router not working", "network down"],
    category: "Internet & Network",
    action: "Reboot floor access point / router; report to campus network administrator if outage persists."
  },
  minor_furniture: {
    weight: 5,
    keywords: ["table squeak", "chair broken", "desk scratch", "wardrobe latch", "window curtain", 
               "fan noise", "bulb fused", "light bulb", "paint peeling"],
    category: "Carpentry & Furniture",
    action: "Log into routine maintenance queue for batch resolution during scheduled rounds."
  }
};

/**
 * Deterministic Local NLP Classifier (exact port from backend_py/llm_service.py)
 * Zero random numbers; strictly reproducible scores.
 */
export function calculateAIPriority(title = "", description = "") {
  const text = `${title} ${description}`.toLowerCase();
  let score = 15;
  const matchedSignals = [];
  let primaryCategory = "General Maintenance";
  let suggestedAction = "Inspect room during regular warden inspection rounds.";

  for (const [signalName, signalData] of Object.entries(EMERGENCY_SIGNALS)) {
    const found = [];
    for (const kw of signalData.keywords) {
      if (text.includes(kw)) {
        found.push(kw);
      }
    }
    if (found.length > 0) {
      score += signalData.weight;
      matchedSignals.push(`${signalName} (${found.slice(0, 2).join(", ")})`);
      if (primaryCategory === "General Maintenance" || signalData.weight > 15) {
        primaryCategory = signalData.category;
        suggestedAction = signalData.action;
      }
    }
  }

  const hasWater = ["water", "leak", "pipe", "tap", "shower", "drip"].some(w => text.includes(w));
  const hasElectric = ["wire", "switch", "electric", "spark", "plug", "socket", "power"].some(e => text.includes(e));
  if (hasWater && hasElectric) {
    score += 35;
    matchedSignals.push("COMPOUND HAZARD: Water + Electricity Risk");
    primaryCategory = "Electrical";
    suggestedAction = "CRITICAL: Isolate electrical supply before touching any water. Immediate emergency dispatch.";
  }

  if (["washroom", "bathroom", "corridor", "staircase"].some(c => text.includes(c))) {
    score += 8;
  }

  const finalScore = Math.min(Math.max(score, 10), 99);

  let priority = "LOW";
  let slaHours = 72;
  let reasoning = "Minor cosmetic or routine maintenance request. Can be handled during scheduled batch maintenance.";

  if (finalScore >= 80) {
    priority = "CRITICAL";
    slaHours = 2;
    reasoning = `Severe emergency/safety threat detected (${matchedSignals.join(", ") || "High-impact incident"}). Threatens resident safety or structural integrity.`;
  } else if (finalScore >= 60) {
    priority = "HIGH";
    slaHours = 8;
    reasoning = `Significant disruption or security/health risk (${matchedSignals.join(", ") || "Urgent disruption"}). Requires expedited resolution within current shift.`;
  } else if (finalScore >= 35) {
    priority = "MEDIUM";
    slaHours = 24;
    reasoning = "Standard living amenity failure. Non-life-threatening but impacts student daily comfort.";
  }

  return {
    priority,
    priority_score: finalScore,
    urgency_score: finalScore,
    category: primaryCategory,
    urgency_reason: reasoning,
    explanation: reasoning,
    suggested_action: suggestedAction,
    sla_hours: slaHours,
    estimated_resolution_time: `${slaHours} hours`,
    ai_engine: "Embedded Local NLP Prioritizer (Active)",
    model: "Embedded Local NLP Prioritizer (Active)"
  };
}

function getDB() {
  let dbStr = localStorage.getItem(DB_KEY);
  if (!dbStr) {
    const initialDB = {
      complaints: REAL_COMPLAINTS,
      blocks: REAL_BLOCKS,
      users: REAL_USERS
    };
    localStorage.setItem(DB_KEY, JSON.stringify(initialDB));
    return initialDB;
  }
  try {
    return JSON.parse(dbStr);
  } catch {
    return { complaints: REAL_COMPLAINTS, blocks: REAL_BLOCKS, users: REAL_USERS };
  }
}

function saveDB(data) {
  localStorage.setItem(DB_KEY, JSON.stringify(data));
}

export function setupMockInterceptor() {
  if (typeof window === "undefined") return;

  const originalFetch = window.fetch.bind(window);
  window.__originalFetch = originalFetch;

  const isGitHubPages = window.location.hostname.includes("github.io");
  const isOfflineHosting = window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1";

  window.fetch = async function (resource, options = {}) {
    const url = typeof resource === "string" ? resource : resource.url;

    const isBackendCall = url.includes("localhost:3000") || 
      url.startsWith("/api/") || 
      url.startsWith("/complaints") || 
      url.startsWith("/userDetails") || 
      url.startsWith("/userType") || 
      url.startsWith("/login") || 
      url.startsWith("/register");

    if (!isBackendCall) {
      return originalFetch(resource, options);
    }

    // On GitHub Pages, handle directly with the genuine local store
    if (isGitHubPages || isOfflineHosting) {
      return handleMockRequest(url, options);
    }

    // On localhost, try real backend first; fallback on error
    try {
      const response = await originalFetch(resource, options);
      return response;
    } catch {
      return handleMockRequest(url, options);
    }
  };
}

async function handleMockRequest(url, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const db = getDB();
  const token = localStorage.getItem("jwtToken") || (options.headers && options.headers.Authorization) || "";
  const isWarden = token.toLowerCase().includes("warden");

  const jsonResponse = (data, status = 200) => {
    return new Response(JSON.stringify(data), {
      status,
      headers: { "Content-Type": "application/json" }
    });
  };

  // 1. POST /login
  if (url.includes("/login") && method === "POST") {
    let body = {};
    try {
      body = typeof options.body === "string" ? JSON.parse(options.body) : {};
    } catch {}

    const email = (body.email || "").toLowerCase();
    const matchedUser = db.users.find(u => u.email.toLowerCase() === email) || (email.includes("warden") ? db.users[0] : db.users[1]);

    const isWardenUser = matchedUser.type === "warden";
    const roleToken = isWardenUser ? "jwt-token-warden-chief" : `jwt-token-student-${matchedUser.user_id}`;

    return jsonResponse({
      jwtToken: roleToken,
      user: {
        user_id: matchedUser.user_id,
        type: matchedUser.type,
        full_name: matchedUser.full_name,
        email: matchedUser.email
      }
    });
  }

  // 2. POST /register
  if (url.includes("/register") && method === "POST") {
    let body = {};
    try {
      body = typeof options.body === "string" ? JSON.parse(options.body) : {};
    } catch {}

    const newUser = {
      user_id: db.users.length + 1,
      full_name: body.full_name || "New Resident",
      email: body.email,
      phone: body.phone || "+91 98000 00000",
      type: body.role || body.type || "student",
      block_id: parseInt(body.block_id) || 1,
      block_name: (db.blocks.find(b => b.block_id === parseInt(body.block_id)) || db.blocks[0]).block_name,
      room: body.room || "101",
      usn: body.usn || "26070126500"
    };

    db.users.push(newUser);
    saveDB(db);

    return jsonResponse({
      jwtToken: `jwt-token-student-${newUser.user_id}`,
      user: {
        user_id: newUser.user_id,
        type: newUser.type,
        full_name: newUser.full_name
      }
    });
  }

  // 3. GET /userType
  if (url.includes("/userType") && method === "GET") {
    return jsonResponse({
      userType: isWarden ? "warden" : "student",
      userId: isWarden ? 1 : 2,
      user_id: isWarden ? 1 : 2
    });
  }

  // 4. GET /userDetails/me
  if (url.includes("/userDetails/me") && method === "GET") {
    if (isWarden) {
      return jsonResponse([db.users[0]]);
    }
    // Return Pranil Shah (student_id 2)
    const studentUser = db.users.find(u => u.user_id === 2) || db.users[1];
    return jsonResponse([studentUser]);
  }

  // 5. GET /api/blocks
  if (url.includes("/api/blocks") && method === "GET") {
    return jsonResponse(db.blocks || REAL_BLOCKS);
  }

  // 6. GET /api/ai/status
  if (url.includes("/api/ai/status") && method === "GET") {
    return jsonResponse({
      available: true,
      active_model: "Embedded Local NLP Prioritizer (Active)",
      device: "Local Deterministic Rule Classifier",
      status: "online"
    });
  }

  // 7. POST /api/ai/preview-priority
  if (url.includes("/api/ai/preview-priority") && method === "POST") {
    let body = {};
    try {
      body = typeof options.body === "string" ? JSON.parse(options.body) : {};
    } catch {}

    const result = calculateAIPriority(body.title, body.description);
    return jsonResponse(result);
  }

  // 8. POST /api/upload
  if (url.includes("/api/upload") && method === "POST") {
    try {
      if (options.body instanceof FormData) {
        const file = options.body.get("file");
        if (file && typeof FileReader !== "undefined") {
          const base64 = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = () => resolve("");
            reader.readAsDataURL(file);
          });
          return jsonResponse({ media_url: base64, url: base64 });
        }
      }
    } catch (e) {
      console.warn("Upload reader error:", e);
    }
    return jsonResponse({
      media_url: "./uploads/3afb0b31ec58_WhatsApp_Image_2026-10-20_at_23.51.41.jpeg"
    });
  }

  // 9. POST /complaints
  if (url.includes("/complaints") && !url.match(/\/complaints\/\d+/) && method === "POST") {
    let payload = {};
    if (options.body instanceof FormData) {
      for (const [k, v] of options.body.entries()) {
        payload[k] = v;
      }
    } else {
      try {
        payload = typeof options.body === "string" ? JSON.parse(options.body) : {};
      } catch {}
    }

    const title = payload.name || payload.title || "Hostel Maintenance Request";
    const desc = payload.description || "";
    const aiRes = calculateAIPriority(title, desc);
    const blockId = parseInt(payload.block_id) || 1;
    const blockObj = db.blocks.find((b) => b.block_id === blockId) || db.blocks[0];

    const currentStudent = db.users.find(u => u.user_id === 2) || db.users[1];

    const newComp = {
      id: db.complaints.length > 0 ? Math.max(...db.complaints.map(c => c.id)) + 1 : 10,
      name: title,
      title: title,
      student_id: currentStudent.user_id,
      description: desc,
      category: aiRes.category || payload.category || "General Maintenance",
      room: payload.room || currentStudent.room || "101",
      block_id: blockId,
      block_name: blockObj.block_name,
      is_completed: 0,
      status: "PENDING",
      priority: aiRes.priority,
      priority_score: aiRes.priority_score,
      urgency_score: aiRes.priority_score,
      urgency_reason: aiRes.urgency_reason,
      ai_explanation: aiRes.urgency_reason,
      suggested_action: aiRes.suggested_action,
      sla_hours: aiRes.sla_hours,
      ai_engine: "Embedded Local NLP Prioritizer (Active)",
      created_at: new Date().toISOString().replace("T", " ").substring(0, 19),
      student_name: currentStudent.full_name,
      student_phone: currentStudent.phone,
      student_email: currentStudent.email,
      student_usn: currentStudent.usn,
      media_url: payload.media_url || null,
      media_type: payload.media_type || (payload.media_url ? "image" : null),
      warden_notes: null
    };

    db.complaints = [newComp, ...db.complaints];
    saveDB(db);

    return jsonResponse({
      message: "Complaint registered successfully with AI priority triage.",
      complaint_id: newComp.id,
      priority: newComp.priority,
      priority_score: newComp.priority_score
    });
  }

  // 10. GET /complaints
  if (url.includes("/complaints") && !url.match(/\/complaints\/\d+/) && method === "GET") {
    let result = [...db.complaints];

    const qIndex = url.indexOf("?");
    if (qIndex !== -1) {
      const searchParams = new URLSearchParams(url.slice(qIndex));
      const status = searchParams.get("status");
      const priority = searchParams.get("priority");
      const category = searchParams.get("category");
      const search = searchParams.get("search");
      const sortByPriority = searchParams.get("sort_by_priority");

      if (status && status.toUpperCase() !== "ALL") {
        if (status.toUpperCase() === "RESOLVED") {
          result = result.filter(c => c.status === "RESOLVED" || c.is_completed === 1);
        } else if (status.toUpperCase() === "PENDING") {
          result = result.filter(c => c.status === "PENDING" && !c.is_completed);
        } else if (status.toUpperCase() === "IN_PROGRESS") {
          result = result.filter(c => c.status === "IN_PROGRESS");
        }
      }
      if (priority && priority.toUpperCase() !== "ALL") {
        result = result.filter((c) => (c.priority || "").toUpperCase() === priority.toUpperCase());
      }
      if (category && category.toUpperCase() !== "ALL") {
        result = result.filter((c) => (c.category || "").toUpperCase() === category.toUpperCase());
      }
      if (search) {
        const s = search.toLowerCase();
        result = result.filter(
          (c) =>
            (c.title || c.name || "").toLowerCase().includes(s) ||
            (c.description || "").toLowerCase().includes(s) ||
            (c.room || "").toLowerCase().includes(s) ||
            (c.student_name || "").toLowerCase().includes(s)
        );
      }
      if (sortByPriority === "true") {
        result.sort((a, b) => (b.priority_score || b.urgency_score || 0) - (a.priority_score || a.urgency_score || 0));
      }
    }

    return jsonResponse(result);
  }

  // 11. PUT /complaints/:id
  const putMatch = url.match(/\/complaints\/(\d+)/);
  if (putMatch && method === "PUT") {
    const id = parseInt(putMatch[1]);
    let body = {};
    try {
      body = typeof options.body === "string" ? JSON.parse(options.body) : {};
    } catch {}

    const index = db.complaints.findIndex((c) => c.id === id);
    if (index !== -1) {
      if (body.status) {
        db.complaints[index].status = body.status;
        if (body.status === "RESOLVED") {
          db.complaints[index].is_completed = 1;
          db.complaints[index].resolved_at = new Date().toISOString().replace("T", " ").substring(0, 19);
        }
      }
      if (body.warden_notes !== undefined) db.complaints[index].warden_notes = body.warden_notes;
      if (body.priority) db.complaints[index].priority = body.priority;
      saveDB(db);
      return jsonResponse({ message: "Complaint updated successfully", complaint: db.complaints[index] });
    }
    return jsonResponse({ error: "Complaint not found" }, 404);
  }

  // 12. DELETE /complaints/:id
  const delMatch = url.match(/\/complaints\/(\d+)/);
  if (delMatch && method === "DELETE") {
    const id = parseInt(delMatch[1]);
    db.complaints = db.complaints.filter((c) => c.id !== id);
    saveDB(db);
    return jsonResponse({ message: "Complaint deleted successfully" });
  }

  // 13. POST /api/ai/batch-prioritize
  if (url.includes("/api/ai/batch-prioritize") && method === "POST") {
    let updatedCount = 0;
    db.complaints = db.complaints.map((c) => {
      const res = calculateAIPriority(c.title || c.name, c.description);
      updatedCount++;
      return {
        ...c,
        priority: res.priority,
        priority_score: res.priority_score,
        urgency_score: res.priority_score,
        urgency_reason: res.urgency_reason,
        ai_explanation: res.urgency_reason,
        suggested_action: res.suggested_action,
        sla_hours: res.sla_hours,
        ai_engine: res.ai_engine
      };
    });
    saveDB(db);
    return jsonResponse({
      message: `Batch AI triage complete: ${updatedCount} complaints re-scored using Local NLP Prioritizer.`,
      prioritized_count: updatedCount
    });
  }

  return jsonResponse({ ok: true });
}
