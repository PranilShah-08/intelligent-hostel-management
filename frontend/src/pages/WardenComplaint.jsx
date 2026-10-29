import React, { useState, useEffect } from "react";
import { useAuth } from "../utils/Auth";

const formatTimestamp = (timestamp) => {
  if (!timestamp) return "N/A";
  const date = new Date(timestamp);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

const getPriorityStyle = (priority, score) => {
  if (priority === "CRITICAL" || score >= 80) {
    return {
      bg: "bg-white",
      border: "border-slate-200 border-l-4 border-l-red-600",
      text: "text-red-700",
      badge: "bg-red-50 text-red-700 border-red-200",
      meter: "bg-red-600",
    };
  }
  if (priority === "HIGH" || score >= 60) {
    return {
      bg: "bg-white",
      border: "border-slate-200 border-l-4 border-l-amber-500",
      text: "text-amber-700",
      badge: "bg-amber-50 text-amber-700 border-amber-200",
      meter: "bg-amber-500",
    };
  }
  if (priority === "MEDIUM" || score >= 35) {
    return {
      bg: "bg-white",
      border: "border-slate-200 border-l-4 border-l-blue-500",
      text: "text-blue-700",
      badge: "bg-blue-50 text-blue-700 border-blue-200",
      meter: "bg-blue-500",
    };
  }
  return {
    bg: "bg-white",
    border: "border-slate-200 border-l-4 border-l-slate-400",
    text: "text-slate-600",
    badge: "bg-slate-100 text-slate-700 border-slate-200",
    meter: "bg-slate-400",
  };
};

const getCategoryIcon = (category) => {
  switch (category) {
    case "Electrical":
      return "⚡";
    case "Plumbing":
      return "🚰";
    case "Safety & Security":
      return "🛡️";
    case "Cleanliness & Hygiene":
      return "🧹";
    case "Internet & Network":
      return "📡";
    case "Carpentry & Furniture":
      return "🪑";
    default:
      return "🔧";
  }
};

const WardenComplaints = () => {
  const { headers } = useAuth();
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortByPriority, setSortByPriority] = useState(true);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  
  // AI Settings & Batch state
  const [aiStatus, setAiStatus] = useState(null);
  const [isBatchRunning, setIsBatchRunning] = useState(false);
  const [batchMsg, setBatchMsg] = useState("");
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [wardenNoteInput, setWardenNoteInput] = useState("");

  const fetchComplaints = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (sortByPriority) params.append("sort_by_priority", "true");
      if (statusFilter !== "ALL") params.append("status", statusFilter);
      if (priorityFilter !== "ALL") params.append("priority", priorityFilter);
      if (categoryFilter !== "ALL") params.append("category", categoryFilter);
      if (searchQuery.trim()) params.append("search", searchQuery.trim());

      const res = await fetch(`http://localhost:3000/complaints?${params.toString()}`, {
        headers,
      });
      if (res.ok) {
        const data = await res.json();
        setComplaints(data);
      }
    } catch (err) {
      console.error("Error fetching complaints:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAiStatus = async () => {
    try {
      const res = await fetch("http://localhost:3000/api/ai/status");
      if (res.ok) {
        const data = await res.json();
        setAiStatus(data);
      }
    } catch (err) {
      console.error("AI status error:", err);
    }
  };

  useEffect(() => {
    fetchComplaints();
    fetchAiStatus();
  }, [sortByPriority, statusFilter, priorityFilter, categoryFilter]);

  const handleStatusChange = async (id, newStatus, notes = null) => {
    try {
      const res = await fetch(`http://localhost:3000/complaints/${id}`, {
        method: "PUT",
        headers,
        body: JSON.stringify({ status: newStatus, warden_notes: notes }),
      });
      if (res.ok) {
        fetchComplaints();
        if (selectedComplaint && selectedComplaint.id === id) {
          setSelectedComplaint(null);
        }
      }
    } catch (err) {
      console.error("Status update error:", err);
    }
  };

  const deleteComplaint = async (id) => {
    if (!window.confirm("Are you sure you want to delete this complaint record?")) return;
    try {
      const res = await fetch(`http://localhost:3000/complaints/${id}`, {
        method: "DELETE",
        headers,
      });
      if (res.ok) {
        setComplaints(complaints.filter((c) => c.id !== id));
      }
    } catch (err) {
      console.error("Delete error:", err);
    }
  };

  const runBatchAiTriage = async () => {
    try {
      setIsBatchRunning(true);
      setBatchMsg("Running AI triage across complaints...");
      const res = await fetch("http://localhost:3000/api/ai/batch-prioritize", {
        method: "POST",
        headers,
      });
      const data = await res.json();
      setBatchMsg(data.message || "Triage complete!");
      fetchComplaints();
      setTimeout(() => setBatchMsg(""), 4000);
    } catch (err) {
      console.error("Batch triage error:", err);
      setBatchMsg("Triage failed.");
    } finally {
      setIsBatchRunning(false);
    }
  };

  // Metrics
  const criticalCount = complaints.filter((c) => c.priority === "CRITICAL" && !c.is_completed).length;
  const highCount = complaints.filter((c) => c.priority === "HIGH" && !c.is_completed).length;
  const inProgressCount = complaints.filter((c) => c.status === "IN_PROGRESS").length;
  const resolvedCount = complaints.filter((c) => c.is_completed || c.status === "RESOLVED").length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 pb-16 pt-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Command Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Warden Operations Center
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                AI Priority Queue
              </span>
            </div>
            <p className="text-sm text-slate-500 mt-1">
              Automated grievance triage, risk severity classification, and technician dispatch
            </p>
          </div>

          {/* Action Toolbar */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Sort by Priority Toggle */}
            <button
              onClick={() => setSortByPriority(!sortByPriority)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold border transition-all ${
                sortByPriority
                  ? "bg-blue-600 text-white border-blue-600 shadow-xs"
                  : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
              </svg>
              <span>{sortByPriority ? "AI Urgency Ranking: ON" : "AI Urgency Ranking: OFF"}</span>
            </button>

            {/* Run Batch AI Triage */}
            <button
              onClick={runBatchAiTriage}
              disabled={isBatchRunning}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 shadow-2xs transition-colors disabled:opacity-50"
            >
              <svg className={`w-4 h-4 text-blue-600 ${isBatchRunning ? "animate-spin" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>{isBatchRunning ? "Triaging..." : "Batch Re-Evaluate"}</span>
            </button>

            {/* Local LLM Settings Modal Trigger */}
            <button
              onClick={() => setShowSettingsModal(true)}
              className="p-2 rounded-lg bg-white border border-slate-300 text-slate-600 hover:text-slate-900 hover:bg-slate-50 shadow-2xs transition-colors"
              title="AI Engine Settings"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Batch Notification */}
        {batchMsg && (
          <div className="my-4 p-3 rounded-lg bg-blue-50 border border-blue-200 text-blue-800 text-xs font-medium">
            {batchMsg}
          </div>
        )}

        {/* Real Metrics Cards */}
        <div className="my-6 grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-2xs">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Complaints</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{complaints.length}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Active & resolved in query</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-2xs">
            <div className="text-xs font-semibold text-red-600 uppercase tracking-wider">Critical Hazards</div>
            <div className="text-2xl font-bold text-red-700 mt-1">{criticalCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">&lt; 2-4h response target</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-2xs">
            <div className="text-xs font-semibold text-indigo-600 uppercase tracking-wider">In Progress</div>
            <div className="text-2xl font-bold text-indigo-700 mt-1">{inProgressCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Technicians dispatched</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-2xs">
            <div className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Resolved</div>
            <div className="text-2xl font-bold text-emerald-700 mt-1">{resolvedCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Closed tickets</div>
          </div>
        </div>

        {/* Filter Toolbar */}
        <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-2xs mb-6 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            
            {/* Status Filter Chips */}
            <div className="flex items-center gap-1.5 overflow-x-auto">
              <span className="text-xs font-semibold text-slate-500 mr-1">Status:</span>
              {["ALL", "PENDING", "IN_PROGRESS", "RESOLVED"].map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    statusFilter === st
                      ? "bg-slate-900 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {st.replace("_", " ")}
                </button>
              ))}
            </div>

            {/* Priority Filter */}
            <div className="flex items-center gap-1.5 overflow-x-auto">
              <span className="text-xs font-semibold text-slate-500 mr-1">Severity:</span>
              {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((pr) => (
                <button
                  key={pr}
                  onClick={() => setPriorityFilter(pr)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                    priorityFilter === pr
                      ? "bg-blue-600 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {pr}
                </button>
              ))}
            </div>

          </div>

          {/* Search Box */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchComplaints()}
              placeholder="Search complaints by title, room, or description (press Enter)..."
              className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
            />
            <svg className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Complaints Feed */}
        {loading ? (
          <div className="py-20 text-center text-slate-400 font-mono text-xs">
            Loading complaints...
          </div>
        ) : complaints.length === 0 ? (
          <div className="py-16 text-center bg-white rounded-2xl border border-slate-200 shadow-2xs">
            <span className="text-3xl">📋</span>
            <h3 className="text-base font-semibold text-slate-900 mt-2">Zero active complaints</h3>
            <p className="text-xs text-slate-500 mt-1">No grievances matching your current filters. New reports will appear here in real time.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {complaints.map((comp) => {
              const priorityStyle = getPriorityStyle(comp.priority, comp.priority_score || 50);
              const isResolved = comp.is_completed || comp.status === "RESOLVED";

              return (
                <div
                  key={comp.id}
                  className={`rounded-xl p-5 border shadow-2xs transition-all ${priorityStyle.border} ${
                    isResolved ? "opacity-75 bg-slate-50/50" : "bg-white"
                  }`}
                >
                  <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                    
                    {/* Left: Core Information */}
                    <div className="flex-1 space-y-2">
                      <div className="flex flex-wrap items-center gap-2">
                        {/* Priority Badge */}
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold border ${priorityStyle.badge}`}>
                          {comp.priority || "MEDIUM"} ({comp.priority_score || 50}/100)
                        </span>

                        {/* Category */}
                        <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-700 flex items-center gap-1">
                          <span>{getCategoryIcon(comp.category)}</span>
                          <span>{comp.category || "General"}</span>
                        </span>

                        {/* Status Tag */}
                        <span className={`px-2 py-0.5 rounded text-[11px] font-semibold uppercase ${
                          comp.status === "RESOLVED" || comp.is_completed
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : comp.status === "IN_PROGRESS"
                            ? "bg-indigo-50 text-indigo-700 border border-indigo-200"
                            : "bg-amber-50 text-amber-700 border border-amber-200"
                        }`}>
                          {comp.status || "PENDING"}
                        </span>

                        {/* Target SLA */}
                        <span className="text-[11px] font-mono text-slate-500">
                          SLA: <strong className="text-slate-800">{comp.sla_hours || 24}h</strong>
                        </span>

                        {/* Attached Evidence Badge */}
                        {comp.media_url && (
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedComplaint(comp);
                              setWardenNoteInput(comp.warden_notes || "");
                            }}
                            className="flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition-colors"
                            title="Click to view attached physical media evidence"
                          >
                            <span>{comp.media_type === "video" ? "🎥 Video" : "📸 Photo"}</span>
                            <span>Attached</span>
                          </button>
                        )}
                      </div>

                      {/* Complaint Title */}
                      <h3 className="text-base font-bold text-slate-900 tracking-tight">
                        {comp.name}
                      </h3>

                      {/* Description */}
                      <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                        {comp.description}
                      </p>

                      {/* AI Diagnostic Reasoning Box */}
                      {comp.urgency_reason && (
                        <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1 text-xs">
                          <div className="flex items-center gap-1.5 text-blue-700 font-semibold text-[11px]">
                            <span>🧠 AI Triage Diagnosis:</span>
                            <span className="text-slate-400 font-normal">({comp.ai_engine || "Local Priority Engine"})</span>
                          </div>
                          <p className="text-slate-700 leading-normal">
                            {comp.urgency_reason}
                          </p>
                          {comp.suggested_action && (
                            <div className="mt-1 pt-1 border-t border-slate-200 text-amber-800 font-medium">
                              👉 <strong>Recommended Action:</strong> {comp.suggested_action}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Resident and Location Details */}
                      <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
                        <span>
                          📍 Room: <strong className="text-slate-800">{comp.room || "N/A"}</strong> ({comp.block_name || "Hostel Block"})
                        </span>
                        <span>
                          👤 Resident: <strong className="text-slate-800">{comp.student_name || "Hostel Resident"}</strong>
                        </span>
                        <span className="font-mono text-[11px]">
                          🕒 Logged: {formatTimestamp(comp.created_at)}
                        </span>
                      </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex lg:flex-col items-center lg:items-end justify-between lg:justify-start gap-2 pt-2 lg:pt-0 border-t lg:border-t-0 border-slate-100">
                      
                      {/* Urgency Progress Bar */}
                      <div className="w-28 text-right hidden sm:block">
                        <div className="text-[10px] font-mono text-slate-500 mb-1">
                          Severity: <strong className="text-slate-900">{comp.priority_score || 50}%</strong>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${priorityStyle.meter}`}
                            style={{ width: `${comp.priority_score || 50}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex items-center gap-2 mt-2">
                        {!isResolved && (
                          <>
                            {comp.status !== "IN_PROGRESS" && (
                              <button
                                onClick={() => handleStatusChange(comp.id, "IN_PROGRESS")}
                                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 transition-colors"
                              >
                                Dispatch
                              </button>
                            )}
                            <button
                              onClick={() => handleStatusChange(comp.id, "RESOLVED")}
                              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 text-white hover:bg-emerald-700 shadow-2xs transition-colors"
                            >
                              Resolve
                            </button>
                          </>
                        )}

                        {isResolved && (
                          <button
                            onClick={() => handleStatusChange(comp.id, "PENDING")}
                            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200 transition-colors"
                          >
                            Reopen
                          </button>
                        )}

                        <button
                          onClick={() => {
                            setSelectedComplaint(comp);
                            setWardenNoteInput(comp.warden_notes || "");
                          }}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
                          title="Manage Ticket & Notes"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </button>

                        <button
                          onClick={() => deleteComplaint(comp.id)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                          title="Delete Ticket"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>

                    </div>

                  </div>
                </div>
              );
            })}
          </div>
        )}

      </div>

      {/* Local LLM Settings Modal */}
      {showSettingsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-2xs">
          <div className="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <span className="text-blue-600">🧠</span>
                <h3 className="font-bold text-base text-slate-900">AI Prioritization Engine</h3>
              </div>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="text-slate-400 hover:text-slate-700"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-600">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-700">Ollama Status:</span>
                  <span className={`px-2 py-0.5 rounded font-mono font-semibold text-[10px] ${
                    aiStatus?.available ? "bg-emerald-50 text-emerald-700" : "bg-slate-200 text-slate-700"
                  }`}>
                    {aiStatus?.available ? "Connected (Local)" : "Embedded NLP Fallback Active"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-700">Active Model:</span>
                  <span className="font-mono text-slate-800">{aiStatus?.active_model || "llama3.2"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-700">Endpoint:</span>
                  <span className="font-mono text-slate-500">http://localhost:11434</span>
                </div>
              </div>

              <p className="text-slate-500 leading-relaxed">
                The local LLM evaluates complaint descriptions for compound safety hazards (sparks near water, perimeter security breaches) and computes priority scores from 0 to 100.
              </p>
            </div>

            <div className="flex justify-end pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowSettingsModal(false)}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs shadow-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Complaint Telemetry & Notes Modal */}
      {selectedComplaint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-2xs">
          <div className="bg-white border border-slate-200 rounded-2xl max-w-lg w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-bold text-base text-slate-900">
                Complaint #{selectedComplaint.id} Details
              </h3>
              <button
                onClick={() => setSelectedComplaint(null)}
                className="text-slate-400 hover:text-slate-700"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="space-y-1">
                <span className="text-slate-500 font-semibold uppercase text-[10px]">Title & Description:</span>
                <p className="font-semibold text-slate-900 text-sm">{selectedComplaint.name}</p>
                <p className="text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200">
                  {selectedComplaint.description}
                </p>
              </div>

              {/* Physical Evidence Attachment (Photo / Video) */}
              {selectedComplaint.media_url && (
                <div className="space-y-1.5 p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-700">
                    <span className="flex items-center gap-1.5 font-semibold">
                      <span>{selectedComplaint.media_type === "video" ? "🎥" : "📸"}</span>
                      <span>Attached Breakdown Evidence</span>
                    </span>
                    <a
                      href={selectedComplaint.media_url.startsWith("http") || selectedComplaint.media_url.startsWith("data:") ? selectedComplaint.media_url : (window.location.hostname.includes("github.io") ? (selectedComplaint.media_url.startsWith("./") ? selectedComplaint.media_url : `.${selectedComplaint.media_url}`) : `http://localhost:3000${selectedComplaint.media_url}`)}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-600 hover:text-blue-700 underline text-[10px]"
                    >
                      Open Full Screen ↗
                    </a>
                  </div>
                  {selectedComplaint.media_type === "video" ? (
                    <video
                      controls
                      src={selectedComplaint.media_url.startsWith("http") || selectedComplaint.media_url.startsWith("data:") ? selectedComplaint.media_url : (window.location.hostname.includes("github.io") ? (selectedComplaint.media_url.startsWith("./") ? selectedComplaint.media_url : `.${selectedComplaint.media_url}`) : `http://localhost:3000${selectedComplaint.media_url}`)}
                      className="w-full max-h-52 rounded-lg bg-black object-contain border border-slate-200"
                    />
                  ) : (
                    <img
                      src={selectedComplaint.media_url.startsWith("http") || selectedComplaint.media_url.startsWith("data:") ? selectedComplaint.media_url : (window.location.hostname.includes("github.io") ? (selectedComplaint.media_url.startsWith("./") ? selectedComplaint.media_url : `.${selectedComplaint.media_url}`) : `http://localhost:3000${selectedComplaint.media_url}`)}
                      alt="Evidence"
                      className="w-full max-h-52 rounded-lg object-contain bg-white border border-slate-200 cursor-pointer"
                      onClick={() => window.open(selectedComplaint.media_url.startsWith("http") || selectedComplaint.media_url.startsWith("data:") ? selectedComplaint.media_url : (window.location.hostname.includes("github.io") ? (selectedComplaint.media_url.startsWith("./") ? selectedComplaint.media_url : `.${selectedComplaint.media_url}`) : `http://localhost:3000${selectedComplaint.media_url}`), "_blank")}
                    />
                  )}
                </div>
              )}

              <div className="grid grid-cols-2 gap-2 text-slate-700">
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                  <span className="text-slate-500 block text-[10px]">Resident Name:</span>
                  <strong>{selectedComplaint.student_name || "Hostel Resident"}</strong>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                  <span className="text-slate-500 block text-[10px]">Phone Contact:</span>
                  <strong>{selectedComplaint.student_phone || "Not provided"}</strong>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-slate-600 font-semibold uppercase text-[10px]">
                  Warden Resolution Notes:
                </label>
                <textarea
                  rows={3}
                  value={wardenNoteInput}
                  onChange={(e) => setWardenNoteInput(e.target.value)}
                  placeholder="Record assigned technician, parts ordered, or resolution details..."
                  className="w-full bg-white border border-slate-300 rounded-lg p-2.5 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-100">
              <button
                onClick={() => setSelectedComplaint(null)}
                className="px-3.5 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-medium"
              >
                Close
              </button>
              <button
                onClick={() => handleStatusChange(selectedComplaint.id, selectedComplaint.status || "IN_PROGRESS", wardenNoteInput)}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium shadow-xs"
              >
                Save Notes & Update
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default WardenComplaints;
