/**
 * Client-Side Mock Backend & Interceptor
 * 
 * Enables full end-to-end functionality (student grievance lodging, live AI priority scoring,
 * warden triage dashboard, status management, image previews) when hosted on GitHub Pages
 * or whenever a local backend server is unreachable.
 */

const DB_KEY = "hostel_pulse_db_v1";

const DEFAULT_BLOCKS = [
  { block_id: 1, block_name: "A Block" },
  { block_id: 2, block_name: "B Block" },
  { block_id: 3, block_name: "C Block" },
  { block_id: 4, block_name: "D Block" },
  { block_id: 5, block_name: "PG Block" },
];

const INITIAL_COMPLAINTS = [
  {
    id: 101,
    name: "Sparks coming from electrical switchboard",
    title: "Sparks coming from electrical switchboard",
    description: "Heavy sparking and strong burning smell from the main 230V socket near study desk. High risk of electrical short circuit.",
    category: "Electrical",
    room: "B-304",
    block_id: 2,
    block_name: "B Block",
    status: "In Progress",
    priority: "CRITICAL",
    urgency_score: 96,
    ai_explanation: "Active electrical arcing hazard detected. Severe fire risk requiring immediate power isolation and emergency technician response.",
    suggested_action: "Isolate circuit breaker, notify floor warden, dispatch licensed electrician immediately.",
    estimated_resolution_time: "< 2 hours",
    ai_model: "qwen2.5:3b (Edge AI)",
    created_at: new Date(Date.now() - 3600000 * 3).toISOString(),
    student_name: "Pranil Shah",
    student_phone: "9123456780",
    student_email: "student@hostel.edu",
    media_url: "",
    warden_notes: "Electrician Mr. Ramesh dispatched with replacement MCB."
  },
  {
    id: 102,
    name: "Ceiling water pipe burst in corridor",
    title: "Ceiling water pipe burst in corridor",
    description: "Main overhead supply pipeline burst near staircase on 3rd floor. Continuous flooding spreading toward rooms 301-305.",
    category: "Plumbing",
    room: "Corridor 3F",
    block_id: 1,
    block_name: "A Block",
    status: "Pending",
    priority: "CRITICAL",
    urgency_score: 91,
    ai_explanation: "Substantial active flooding threatens structural integrity and electrical conduits along the corridor.",
    suggested_action: "Shut off riser valve A-3, summon emergency plumbing crew.",
    estimated_resolution_time: "< 3 hours",
    ai_model: "qwen2.5:3b (Edge AI)",
    created_at: new Date(Date.now() - 3600000 * 5).toISOString(),
    student_name: "Aarav Sharma",
    student_phone: "9876543211",
    student_email: "aarav@hostel.edu",
    media_url: "",
    warden_notes: null
  },
  {
    id: 103,
    name: "Room door lock deadbolt jammed",
    title: "Room door lock deadbolt jammed",
    description: "Key cylinder is stuck and deadbolt does not retract smoothly. Student cannot securely lock room when leaving for classes.",
    category: "Carpentry",
    room: "A-105",
    block_id: 1,
    block_name: "A Block",
    status: "In Progress",
    priority: "HIGH",
    urgency_score: 76,
    ai_explanation: "Physical security vulnerability leaving student belongings unsecured during lecture hours.",
    suggested_action: "Dispatch carpenter/locksmith for cylinder replacement or lubrication.",
    estimated_resolution_time: "4 - 8 hours",
    ai_model: "qwen2.5:3b (Edge AI)",
    created_at: new Date(Date.now() - 3600000 * 8).toISOString(),
    student_name: "Aditya Nair",
    student_phone: "9945678123",
    student_email: "aditya@hostel.edu",
    media_url: "",
    warden_notes: "Carpenter notified, visiting at 2:00 PM."
  },
  {
    id: 104,
    name: "Bathroom geyser not heating water",
    title: "Bathroom geyser not heating water",
    description: "25L geyser power light illuminates but water remains cold even after 30 minutes of heating.",
    category: "Electrical",
    room: "D-402",
    block_id: 4,
    block_name: "D Block",
    status: "Pending",
    priority: "MEDIUM",
    urgency_score: 54,
    ai_explanation: "Thermostat or heating element failure. Amenity disruption without immediate life-safety risk.",
    suggested_action: "Standard maintenance order queued for heating element replacement.",
    estimated_resolution_time: "12 - 24 hours",
    ai_model: "qwen2.5:3b (Edge AI)",
    created_at: new Date(Date.now() - 3600000 * 14).toISOString(),
    student_name: "Karan Singh",
    student_phone: "9712345678",
    student_email: "karan@hostel.edu",
    media_url: "",
    warden_notes: null
  },
  {
    id: 105,
    name: "WiFi router blinking red on 2nd floor",
    title: "WiFi router blinking red on 2nd floor",
    description: "Hostel WiFi access point AP-B2-04 is unreachable, students unable to complete project submissions.",
    category: "Network",
    room: "Room 208",
    block_id: 2,
    block_name: "B Block",
    status: "Resolved",
    priority: "MEDIUM",
    urgency_score: 52,
    ai_explanation: "LAN switch/AP connection dropped; network infrastructure incident.",
    suggested_action: "IT helpdesk restart PoE port switch B2.",
    estimated_resolution_time: "Resolved",
    ai_model: "qwen2.5:3b (Edge AI)",
    created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
    student_name: "Rohit Verma",
    student_phone: "9823123456",
    student_email: "rohit@hostel.edu",
    media_url: "",
    warden_notes: "Router power cycled and fiber patched by campus IT."
  },
  {
    id: 106,
    name: "Ceiling fan speed regulator noisy",
    title: "Ceiling fan speed regulator noisy",
    description: "Ceiling fan regulator emits faint buzz and fan vibrates slightly on speed setting 3.",
    category: "Electrical",
    room: "C-112",
    block_id: 3,
    block_name: "C Block",
    status: "Pending",
    priority: "LOW",
    urgency_score: 28,
    ai_explanation: "Minor mechanical wear in regulator resistor. Low urgency routine repair.",
    suggested_action: "Scheduled in weekly electrical check batch.",
    estimated_resolution_time: "24 - 48 hours",
    ai_model: "qwen2.5:3b (Edge AI)",
    created_at: new Date(Date.now() - 3600000 * 30).toISOString(),
    student_name: "Sneha Patel",
    student_phone: "9811223344",
    student_email: "sneha@hostel.edu",
    media_url: "",
    warden_notes: null
  }
];

// Heuristic AI Triage Calculator
export function calculateAIPriority(title = "", description = "") {
  const text = `${title} ${description}`.toLowerCase();
  
  // Urgent / Critical safety hazards
  if (/spark|burning|smoke|fire|short circuit|shock|electric shock|collapse|flood|burst|gas leak|explosion/i.test(text)) {
    return {
      priority: "CRITICAL",
      urgency_score: Math.floor(88 + Math.random() * 11),
      explanation: "Active safety or structural hazard detected. Potential life-safety or severe property risk requiring immediate priority dispatch.",
      suggested_action: "Emergency dispatch: isolate affected utility supply and alert building supervisor.",
      estimated_resolution_time: "< 2 hours",
      model: "qwen2.5:3b (Edge AI)"
    };
  }
  
  // High operational impact
  if (/pipe|water leak|overflow|door lock|deadbolt|no power|power cut|blackout|sewage|broken window|theft/i.test(text)) {
    return {
      priority: "HIGH",
      urgency_score: Math.floor(70 + Math.random() * 16),
      explanation: "Substantial operational disruption or security vulnerability affecting hostel residents.",
      suggested_action: "Priority technician assignment within 4 hours; notify floor warden.",
      estimated_resolution_time: "4 - 8 hours",
      model: "qwen2.5:3b (Edge AI)"
    };
  }
  
  // Medium amenity impact
  if (/wifi|internet|network|geyser|hot water|fan|light|tube light|tap|cockroach|pest|insect|flush|cooler/i.test(text)) {
    return {
      priority: "MEDIUM",
      urgency_score: Math.floor(45 + Math.random() * 20),
      explanation: "Standard amenity malfunction affecting individual resident comfort or study environment.",
      suggested_action: "Schedule routine maintenance queue within 24 hours.",
      estimated_resolution_time: "12 - 24 hours",
      model: "qwen2.5:3b (Edge AI)"
    };
  }
  
  // Low routine maintenance
  return {
    priority: "LOW",
    urgency_score: Math.floor(20 + Math.random() * 20),
    explanation: "Minor cosmetic or non-critical maintenance request with no immediate impact on safety.",
    suggested_action: "Consolidate into general hostel maintenance batch.",
    estimated_resolution_time: "24 - 48 hours",
    model: "qwen2.5:3b (Edge AI)"
  };
}

// Ensure DB is initialized
function getDB() {
  let dbStr = localStorage.getItem(DB_KEY);
  if (!dbStr) {
    const initialDB = {
      complaints: INITIAL_COMPLAINTS,
      blocks: DEFAULT_BLOCKS,
    };
    localStorage.setItem(DB_KEY, JSON.stringify(initialDB));
    return initialDB;
  }
  try {
    return JSON.parse(dbStr);
  } catch {
    return { complaints: INITIAL_COMPLAINTS, blocks: DEFAULT_BLOCKS };
  }
}

function saveDB(data) {
  localStorage.setItem(DB_KEY, JSON.stringify(data));
}

// Setup fetch interceptor
export function setupMockInterceptor() {
  if (typeof window === "undefined") return;

  const originalFetch = window.fetch.bind(window);
  window.__originalFetch = originalFetch;

  const isGitHubPages = window.location.hostname.includes("github.io");
  const isOfflineHosting = window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1";

  window.fetch = async function (resource, options = {}) {
    const url = typeof resource === "string" ? resource : resource.url;

    // Check if this is an API call meant for our backend
    const isBackendCall = url.includes("localhost:3000") || url.startsWith("/api/") || url.startsWith("/complaints") || url.startsWith("/userDetails") || url.startsWith("/userType") || url.startsWith("/login") || url.startsWith("/register");

    if (!isBackendCall) {
      return originalFetch(resource, options);
    }

    // If hosted on GitHub Pages or external domain without a local backend, handle directly with mock
    if (isGitHubPages || isOfflineHosting) {
      return handleMockRequest(url, options);
    }

    // If local, try real fetch; fallback to mock on connection refused / network error
    try {
      const response = await originalFetch(resource, options);
      return response;
    } catch (err) {
      console.warn("Backend fetch failed, falling back to client-side mock engine:", url);
      return handleMockRequest(url, options);
    }
  };
}

async function handleMockRequest(url, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const db = getDB();
  const token = localStorage.getItem("jwtToken") || (options.headers && options.headers.Authorization) || "";
  const isWarden = token.toLowerCase().includes("warden");

  // Helper response builder
  const jsonResponse = (data, status = 200) => {
    return new Response(JSON.stringify(data), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  };

  // 1. POST /login
  if (url.includes("/login") && method === "POST") {
    let body = {};
    try {
      body = typeof options.body === "string" ? JSON.parse(options.body) : {};
    } catch {}

    const email = (body.email || "").toLowerCase();
    const isWardenEmail = email.includes("warden");
    const roleToken = isWardenEmail ? "mock-jwt-warden-session-token" : "mock-jwt-student-session-token";
    return jsonResponse({
      jwtToken: roleToken,
      user: {
        email: body.email,
        role: isWardenEmail ? "warden" : "student",
      },
    });
  }

  // 2. POST /register
  if (url.includes("/register") && method === "POST") {
    let body = {};
    try {
      body = typeof options.body === "string" ? JSON.parse(options.body) : {};
    } catch {}

    const role = (body.role || "student").toLowerCase();
    const roleToken = role.includes("warden") ? "mock-jwt-warden-session-token" : "mock-jwt-student-session-token";
    return jsonResponse({
      jwtToken: roleToken,
      message: "Registration successful! Welcome to HostelPulse.",
    });
  }

  // 3. GET /userType
  if (url.includes("/userType") && method === "GET") {
    return jsonResponse({
      userType: isWarden ? "warden" : "student",
    });
  }

  // 4. GET /userDetails/me
  if (url.includes("/userDetails/me") && method === "GET") {
    if (isWarden) {
      return jsonResponse([
        {
          user_id: 1,
          name: "Dr. K. S. Sharma",
          full_name: "Dr. K. S. Sharma",
          email: "warden@hostel.edu",
          phone: "9876543210",
          role: "warden",
          block_id: 1,
          block_name: "A Block",
          room: "Warden Office",
        },
      ]);
    }
    return jsonResponse([
      {
        user_id: 2,
        name: "Pranil Shah",
        full_name: "Pranil Shah",
        email: "student@hostel.edu",
        phone: "9123456780",
        role: "student",
        block_id: 2,
        block_name: "B Block",
        room: "B-304",
      },
    ]);
  }

  // 5. GET /api/blocks
  if (url.includes("/api/blocks") && method === "GET") {
    return jsonResponse(db.blocks || DEFAULT_BLOCKS);
  }

  // 6. GET /api/ai/status
  if (url.includes("/api/ai/status") && method === "GET") {
    return jsonResponse({
      available: true,
      active_model: "qwen2.5:3b (Edge AI)",
      device: "Browser Edge-ML Triage",
      status: "online",
      triage_active: true,
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
    // If formData has a file, read it to base64 Data URL
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
          return jsonResponse({ media_url: base64 });
        }
      }
    } catch (e) {
      console.warn("Mock upload file reading error:", e);
    }
    return jsonResponse({
      media_url: "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=600&q=80",
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
    const blockId = parseInt(payload.block_id) || 2;
    const blockObj = db.blocks.find((b) => b.block_id === blockId) || { block_name: "B Block" };

    const newComp = {
      id: Date.now(),
      name: title,
      title: title,
      description: desc,
      category: payload.category || "General",
      room: payload.room || "B-304",
      block_id: blockId,
      block_name: blockObj.block_name,
      status: "PENDING",
      priority: aiRes.priority,
      urgency_score: aiRes.urgency_score,
      ai_explanation: aiRes.explanation,
      suggested_action: aiRes.suggested_action,
      estimated_resolution_time: aiRes.estimated_resolution_time,
      ai_model: aiRes.model,
      created_at: new Date().toISOString(),
      student_name: isWarden ? "Resident Request" : "Pranil Shah",
      student_phone: "9123456780",
      student_email: "student@hostel.edu",
      media_url: payload.media_url || "",
      warden_notes: null,
    };

    db.complaints = [newComp, ...db.complaints];
    saveDB(db);

    return jsonResponse({
      message: "Complaint lodged successfully with AI priority scoring!",
      complaint_id: newComp.id,
      ai_priority: newComp.priority,
    });
  }

  // 10. GET /complaints
  if (url.includes("/complaints") && !url.match(/\/complaints\/\d+/) && method === "GET") {
    let result = [...db.complaints];

    // Parse query params
    const qIndex = url.indexOf("?");
    if (qIndex !== -1) {
      const searchParams = new URLSearchParams(url.slice(qIndex));
      const status = searchParams.get("status");
      const priority = searchParams.get("priority");
      const category = searchParams.get("category");
      const search = searchParams.get("search");
      const sortByPriority = searchParams.get("sort_by_priority");

      if (status && status !== "ALL") {
        result = result.filter((c) => (c.status || "").toUpperCase() === status.toUpperCase());
      }
      if (priority && priority !== "ALL") {
        result = result.filter((c) => (c.priority || "").toUpperCase() === priority.toUpperCase());
      }
      if (category && category !== "ALL") {
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
        result.sort((a, b) => (b.urgency_score || 0) - (a.urgency_score || 0));
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
      if (body.status) db.complaints[index].status = body.status;
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
    return jsonResponse({ message: "Complaint record deleted successfully" });
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
        urgency_score: res.urgency_score,
        ai_explanation: res.explanation,
        suggested_action: res.suggested_action,
        ai_model: res.model,
      };
    });
    saveDB(db);
    return jsonResponse({
      message: `Batch AI triage complete: ${updatedCount} complaints re-scored successfully.`,
      prioritized_count: updatedCount,
    });
  }

  // Default fallback for any other route
  return jsonResponse({ ok: true, mock: true });
}
