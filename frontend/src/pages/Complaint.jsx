import React, { useState, useEffect, useRef } from "react";
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

const ComplaintForm = () => {
  const { headers } = useAuth();
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  // Form inputs
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [room, setRoom] = useState("");
  const [blockList, setBlockList] = useState([]);
  const [selectedBlockId, setSelectedBlockId] = useState("");
  const [activeTab, setActiveTab] = useState("file"); // 'file' | 'track'

  // Photo / Video attachment state
  const [selectedFile, setSelectedFile] = useState(null);
  const [mediaPreview, setMediaPreview] = useState(null); // { url, type: 'image' | 'video', name, size }
  const [lightboxMedia, setLightboxMedia] = useState(null);
  const fileInputRef = useRef(null);

  // Live AI Preview state
  const [aiPreview, setAiPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const debounceTimer = useRef(null);

  // Fetch student complaints
  const fetchComplaints = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://localhost:3000/complaints", { headers });
      if (res.ok) {
        const data = await res.json();
        setComplaints(data);
      }
    } catch (err) {
      console.error("Fetch complaints error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();

    // Fetch real blocks from database
    fetch("http://localhost:3000/api/blocks")
      .then((res) => res.json())
      .then((data) => {
        setBlockList(data);
        if (data.length > 0) setSelectedBlockId(data[0].block_id);
      })
      .catch((err) => console.error("Blocks fetch error:", err));

    // Fetch resident's actual assigned room and block
    fetch("http://localhost:3000/userDetails/me", { headers })
      .then((res) => res.json())
      .then((data) => {
        if (data && data.length > 0) {
          if (data[0].room && data[0].room !== "NA") setRoom(data[0].room);
          if (data[0].block_id) setSelectedBlockId(data[0].block_id);
        }
      })
      .catch((err) => console.error("User details fetch error:", err));
  }, []);

  // Debounced Live AI Priority Preview
  useEffect(() => {
    if (!description.trim() || description.length < 8) {
      setAiPreview(null);
      return;
    }

    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    debounceTimer.current = setTimeout(async () => {
      try {
        setPreviewLoading(true);
        const res = await fetch("http://localhost:3000/api/ai/preview-priority", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: name || description.slice(0, 30),
            description: description,
            room: room || "General",
            block_id: parseInt(selectedBlockId) || 1,
          }),
        });
        if (res.ok) {
          const data = await res.json();
          setAiPreview(data);
        }
      } catch (err) {
        console.error("AI preview error:", err);
      } finally {
        setPreviewLoading(false);
      }
    }, 450);

    return () => clearTimeout(debounceTimer.current);
  }, [name, description, room, selectedBlockId]);

  // Handle Photo / Video Selection
  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const isImage = file.type.startsWith("image/");
    const isVideo = file.type.startsWith("video/");

    if (!isImage && !isVideo) {
      alert("Please select a supported image (.jpg, .png, .webp) or video (.mp4, .mov, .webm) file.");
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      alert("File size exceeds 50MB limit. Please upload a smaller video or photo.");
      return;
    }

    const previewUrl = URL.createObjectURL(file);
    const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
    const sizeKB = Math.round(file.size / 1024);
    const formattedSize = file.size > 1024 * 1024 ? `${sizeMB} MB` : `${sizeKB} KB`;

    setSelectedFile(file);
    setMediaPreview({
      url: previewUrl,
      type: isVideo ? "video" : "image",
      name: file.name,
      size: formattedSize,
    });
  };

  const removeSelectedFile = () => {
    if (mediaPreview?.url) {
      URL.revokeObjectURL(mediaPreview.url);
    }
    setSelectedFile(null);
    setMediaPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return alert("Please provide a complaint subject/title.");
    if (!room.trim()) return alert("Please specify your Room number.");
    if (!description.trim()) return alert("Please describe your complaint.");

    try {
      setSubmitting(true);
      setUploadStatus("Processing request...");

      let uploadedMediaUrl = null;
      let uploadedMediaType = null;

      // Upload file first if attached
      if (selectedFile) {
        setUploadStatus(`Uploading ${mediaPreview.type === 'video' ? 'video' : 'photo'} evidence...`);
        const formData = new FormData();
        formData.append("file", selectedFile);

        const uploadRes = await fetch("http://localhost:3000/api/upload", {
          method: "POST",
          headers: {
            Authorization: headers.Authorization || headers.authorization,
          },
          body: formData,
        });

        if (!uploadRes.ok) {
          throw new Error("Failed to upload media evidence");
        }

        const uploadData = await uploadRes.json();
        uploadedMediaUrl = uploadData.relative_url;
        uploadedMediaType = uploadData.media_type;
      }

      setUploadStatus("Running AI triage & submitting grievance...");
      const body = {
        name,
        description,
        room,
        block_id: parseInt(selectedBlockId) || 1,
        media_url: uploadedMediaUrl,
        media_type: uploadedMediaType,
      };

      const res = await fetch("http://localhost:3000/complaints", {
        method: "POST",
        headers,
        body: JSON.stringify(body),
      });

      if (res.ok) {
        setName("");
        setDescription("");
        removeSelectedFile();
        setAiPreview(null);
        setActiveTab("track");
        fetchComplaints();
      } else {
        alert("Failed to submit complaint. Please try again.");
      }
    } catch (err) {
      console.error("Submission error:", err);
      alert("Submission error: " + (err.message || "Failed to submit complaint"));
    } finally {
      setSubmitting(false);
      setUploadStatus("");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 pb-16 pt-6">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        
        {/* Header & Tabs */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                Resident Grievance Portal
              </h1>
              <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                Verified Resident
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              File service requests with photo/video evidence and real-time AI triage assessment
            </p>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
            <button
              onClick={() => setActiveTab("file")}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "file"
                  ? "bg-white text-blue-700 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Lodge Complaint
            </button>
            <button
              onClick={() => setActiveTab("track")}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "track"
                  ? "bg-white text-blue-700 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              My Complaints ({complaints.length})
            </button>
          </div>
        </div>

        {/* Tab 1: File Complaint Form */}
        {activeTab === "file" && (
          <div className="my-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Form Column */}
            <div className="lg:col-span-7 bg-white rounded-2xl p-6 sm:p-7 border border-slate-200 shadow-xs">
              <h2 className="text-base font-bold text-slate-900 mb-4">
                New Maintenance Request
              </h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Subject / Title
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Water leaking into light fixture"
                    className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Room Number
                    </label>
                    <input
                      type="text"
                      value={room}
                      onChange={(e) => setRoom(e.target.value)}
                      placeholder="e.g. 204 or 3rd Floor Corridor"
                      className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Hostel Wing / Block
                    </label>
                    <select
                      value={selectedBlockId}
                      onChange={(e) => setSelectedBlockId(e.target.value)}
                      className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                    >
                      {blockList.map((b) => (
                        <option key={b.block_id} value={b.block_id}>
                          {b.block_name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Detailed Grievance Description
                  </label>
                  <textarea
                    rows={4}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe the issue accurately (sparks, water leaks, broken locks, odors, etc.). The local AI will evaluate urgency in real time..."
                    className="w-full bg-white border border-slate-300 rounded-lg p-3.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                    required
                  />
                </div>

                {/* Photo or Video Attachment Dropzone */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-xs font-semibold text-slate-700">
                      Photo or Video Evidence (Optional)
                    </label>
                    <span className="text-[11px] text-slate-400 font-mono">
                      JPG, PNG, MP4, MOV (Max 50MB)
                    </span>
                  </div>

                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    accept="image/*,video/*"
                    className="hidden"
                    id="media-evidence-upload"
                  />

                  {!mediaPreview ? (
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      className="border-2 border-dashed border-slate-300 hover:border-blue-500 hover:bg-blue-50/30 transition-all rounded-xl p-5 text-center cursor-pointer bg-slate-50"
                    >
                      <div className="flex items-center justify-center gap-2 text-slate-500">
                        <span className="text-xl">📷</span>
                        <span className="text-slate-400">/</span>
                        <span className="text-xl">🎥</span>
                      </div>
                      <p className="text-xs font-medium text-slate-700 mt-1.5">
                        Click to attach photo or video evidence
                      </p>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Helps technicians identify exact parts needed before dispatching
                      </p>
                    </div>
                  ) : (
                    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase ${
                            mediaPreview.type === "video"
                              ? "bg-purple-100 text-purple-700 border border-purple-200"
                              : "bg-blue-100 text-blue-700 border border-blue-200"
                          }`}>
                            {mediaPreview.type === "video" ? "Video" : "Photo"}
                          </span>
                          <span className="font-medium text-slate-800 truncate max-w-[200px] sm:max-w-[260px]">
                            {mediaPreview.name}
                          </span>
                          <span className="text-slate-400 font-mono text-[10px]">
                            ({mediaPreview.size})
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={removeSelectedFile}
                          className="px-2 py-1 rounded text-xs font-medium text-red-600 hover:bg-red-50"
                        >
                          Remove
                        </button>
                      </div>

                      {/* Interactive Media Preview Box */}
                      <div className="rounded-lg overflow-hidden bg-slate-100 border border-slate-200 flex items-center justify-center max-h-48">
                        {mediaPreview.type === "image" ? (
                          <img
                            src={mediaPreview.url}
                            alt="Evidence preview"
                            className="max-h-48 w-full object-contain rounded-lg"
                          />
                        ) : (
                          <video
                            controls
                            src={mediaPreview.url}
                            className="max-h-48 w-full bg-black rounded-lg object-contain"
                          />
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors disabled:opacity-50 mt-2"
                >
                  {submitting ? (uploadStatus || "Submitting...") : "Submit Maintenance Request"}
                </button>
              </form>
            </div>

            {/* AI Real-time Triage Preview Column */}
            <div className="lg:col-span-5 space-y-4">
              <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <span className="text-blue-600">🧠</span>
                    <h3 className="font-bold text-sm text-slate-900">Live AI Priority Triage</h3>
                  </div>
                  {previewLoading && (
                    <span className="text-[11px] font-mono text-blue-600 animate-pulse">Evaluating...</span>
                  )}
                </div>

                {aiPreview ? (
                  <div className="space-y-3">
                    {/* Urgency Pill & Score */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-500">Evaluated Priority:</span>
                      <span className={`px-2.5 py-0.5 rounded-full font-mono font-bold text-xs border ${
                        aiPreview.priority === "CRITICAL"
                          ? "bg-red-50 text-red-700 border-red-200"
                          : aiPreview.priority === "HIGH"
                          ? "bg-amber-50 text-amber-700 border-amber-200"
                          : "bg-blue-50 text-blue-700 border-blue-200"
                      }`}>
                        {aiPreview.priority} ({aiPreview.priority_score}/100)
                      </span>
                    </div>

                    {/* Category */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-500">Classification:</span>
                      <span className="font-medium text-xs text-slate-800">{aiPreview.category}</span>
                    </div>

                    {/* SLA */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-500">Target Response SLA:</span>
                      <span className="font-mono text-xs font-semibold text-slate-900">
                        &lt; {aiPreview.sla_hours} Hours
                      </span>
                    </div>

                    {/* AI Urgency Reason */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-1">
                      <strong className="text-slate-500 block font-mono text-[10px] uppercase">
                        AI Urgency Analysis:
                      </strong>
                      <p className="leading-relaxed">{aiPreview.urgency_reason}</p>
                    </div>

                    {/* Suggested Action */}
                    {aiPreview.suggested_action && (
                      <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900 space-y-1">
                        <strong className="text-amber-700 block font-mono text-[10px] uppercase">
                          Recommended Action:
                        </strong>
                        <p>{aiPreview.suggested_action}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="py-8 text-center text-slate-400 text-xs">
                    <p>Type your complaint description to see the real-time AI severity score, category, and SLA calculation.</p>
                  </div>
                )}
              </div>

              {/* Tips Card */}
              <div className="bg-white rounded-xl p-4 border border-slate-200 text-xs text-slate-500 space-y-1.5">
                <strong className="text-slate-700 block">💡 Tips for Fast Resolution:</strong>
                <p>• Mention exact room numbers and electrical / plumbing symptoms.</p>
                <p>• Attach clear photos or video clips of broken equipment or leaks.</p>
                <p>• High-severity safety emergencies are prioritized automatically for wardens.</p>
              </div>
            </div>

          </div>
        )}

        {/* Tab 2: Track My Complaints */}
        {activeTab === "track" && (
          <div className="my-8 space-y-4">
            {loading ? (
              <div className="py-20 text-center text-slate-400 font-mono text-xs">
                Loading complaints...
              </div>
            ) : complaints.length === 0 ? (
              <div className="py-16 text-center bg-white rounded-2xl border border-slate-200">
                <span className="text-3xl">📋</span>
                <h3 className="text-base font-semibold text-slate-900 mt-2">No complaints filed yet</h3>
                <p className="text-xs text-slate-500 mt-1">Click "Lodge Complaint" above to register a maintenance request.</p>
              </div>
            ) : (
              complaints.map((comp) => {
                const isResolved = comp.is_completed || comp.status === "RESOLVED";
                const mediaUrl = comp.media_url
                  ? (comp.media_url.startsWith("http") || comp.media_url.startsWith("data:"))
                    ? comp.media_url
                    : `http://localhost:3000${comp.media_url}`
                  : null;

                return (
                  <div
                    key={comp.id}
                    className="rounded-2xl p-5 sm:p-6 bg-white border border-slate-200 shadow-xs space-y-4"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold border ${
                          comp.priority === "CRITICAL"
                            ? "bg-red-50 text-red-700 border-red-200"
                            : comp.priority === "HIGH"
                            ? "bg-amber-50 text-amber-700 border-amber-200"
                            : "bg-blue-50 text-blue-700 border-blue-200"
                        }`}>
                          {comp.priority || "MEDIUM"} ({comp.priority_score || 50}/100)
                        </span>
                        <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                          {comp.category || "General"}
                        </span>
                        <span className="text-xs text-slate-500 font-mono">
                          Room {comp.room}
                        </span>

                        {mediaUrl && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                            {comp.media_type === "video" ? "🎥 Video Evidence" : "📸 Photo Evidence"}
                          </span>
                        )}
                      </div>

                      <span className="text-xs font-mono text-slate-400">
                        Logged: {formatTimestamp(comp.created_at)}
                      </span>
                    </div>

                    <div>
                      <h3 className="text-base font-bold text-slate-900 tracking-tight">
                        {comp.name}
                      </h3>
                      <p className="text-xs sm:text-sm text-slate-600 mt-1">
                        {comp.description}
                      </p>
                    </div>

                    {/* Attached Photo or Video Evidence Preview */}
                    {mediaUrl && (
                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                        <div className="flex items-center justify-between text-[11px] font-mono text-slate-500">
                          <span className="flex items-center gap-1.5 font-semibold text-slate-700">
                            <span>{comp.media_type === "video" ? "🎥" : "📸"}</span>
                            <span>Attached Physical Breakdown Evidence</span>
                          </span>
                          <a
                            href={mediaUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="text-blue-600 hover:text-blue-700 underline"
                          >
                            Open Full Resolution ↗
                          </a>
                        </div>

                        {comp.media_type === "video" ? (
                          <video
                            controls
                            src={mediaUrl}
                            className="w-full max-h-64 rounded-lg bg-black object-contain border border-slate-200"
                          />
                        ) : (
                          <div
                            onClick={() => setLightboxMedia({ url: mediaUrl, type: "image", name: comp.name })}
                            className="cursor-pointer group relative overflow-hidden rounded-lg max-h-56 bg-slate-100 border border-slate-200 flex items-center justify-center"
                          >
                            <img
                              src={mediaUrl}
                              alt="Evidence attachment"
                              className="max-h-56 w-auto object-contain rounded-lg"
                            />
                            <div className="absolute inset-0 bg-slate-900/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs font-semibold text-white">
                              Click to Enlarge
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Timeline Progress Bar */}
                    <div className="pt-2 border-t border-slate-100">
                      <div className="grid grid-cols-4 gap-2 text-center text-[11px] font-mono">
                        <div className="p-2 rounded bg-blue-50 border border-blue-200 text-blue-700 font-semibold">
                          1. Submitted ✓
                        </div>
                        <div className="p-2 rounded bg-blue-50 border border-blue-200 text-blue-700 font-semibold">
                          2. AI Triaged ✓
                        </div>
                        <div className={`p-2 rounded border ${
                          comp.status === "IN_PROGRESS" || isResolved
                            ? "bg-indigo-50 border-indigo-200 text-indigo-700 font-semibold"
                            : "bg-slate-50 border-slate-200 text-slate-400"
                        }`}>
                          3. Dispatched {comp.status === "IN_PROGRESS" || isResolved ? "✓" : "..."}
                        </div>
                        <div className={`p-2 rounded border ${
                          isResolved
                            ? "bg-emerald-50 border-emerald-200 text-emerald-700 font-semibold"
                            : "bg-slate-50 border-slate-200 text-slate-400"
                        }`}>
                          4. Resolved {isResolved ? "✓" : "..."}
                        </div>
                      </div>
                    </div>

                    {/* Warden Notes Feedback */}
                    {comp.warden_notes && (
                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700">
                        <strong className="text-slate-900 block font-mono text-[10px] uppercase">
                          Warden Resolution Feedback:
                        </strong>
                        <p className="mt-1">{comp.warden_notes}</p>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        )}

      </div>

      {/* Lightbox Modal for Full Resolution Media */}
      {lightboxMedia && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setLightboxMedia(null)}
        >
          <div
            className="bg-white border border-slate-200 rounded-2xl max-w-3xl w-full p-4 overflow-hidden shadow-xl space-y-3"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-2 border-b border-slate-100 text-xs font-mono">
              <span className="text-slate-800 truncate font-semibold">
                Evidence: {lightboxMedia.name}
              </span>
              <button
                onClick={() => setLightboxMedia(null)}
                className="text-slate-500 hover:text-slate-800 text-base px-2 py-0.5 rounded hover:bg-slate-100"
              >
                ✕
              </button>
            </div>
            <div className="flex items-center justify-center max-h-[70vh] overflow-auto">
              <img
                src={lightboxMedia.url}
                alt={lightboxMedia.name}
                className="max-h-[65vh] w-auto object-contain rounded-lg"
              />
            </div>
            <div className="flex justify-end pt-2 border-t border-slate-100">
              <a
                href={lightboxMedia.url}
                target="_blank"
                rel="noreferrer"
                download
                className="px-4 py-1.5 rounded-lg text-xs font-medium bg-blue-600 hover:bg-blue-700 text-white"
              >
                Open Original ↗
              </a>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default ComplaintForm;
