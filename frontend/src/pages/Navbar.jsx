import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const [userType, setUserType] = useState(null);
  const [aiEngine, setAiEngine] = useState("AI Engine Ready");
  const [switching, setSwitching] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("jwtToken");
    if (!token) return;

    fetch("http://localhost:3000/userType", {
      headers: { Authorization: token },
    })
      .then((res) => res.json())
      .then((data) => {
        setUserType(data.userType);
      })
      .catch((err) => console.error("UserType fetch error:", err));

    // Fetch AI status
    fetch("http://localhost:3000/api/ai/status")
      .then((res) => res.json())
      .then((data) => {
        if (data.available && data.active_model) {
          setAiEngine(`Ollama: ${data.active_model}`);
        } else {
          setAiEngine("Local Priority Engine");
        }
      })
      .catch(() => setAiEngine("Local Priority Engine"));
  }, []);

  const logout = () => {
    localStorage.removeItem("jwtToken");
    navigate("/login");
  };

  const quickSwitch = async (email, password) => {
    setSwitching(true);
    try {
      const res = await fetch("http://localhost:3000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (data.jwtToken) {
        localStorage.setItem("jwtToken", data.jwtToken);
        window.location.reload();
      }
    } catch (e) {
      console.error("Quick switch error:", e);
    } finally {
      setSwitching(false);
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-white border-b border-slate-200 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand / Logo */}
        <Link to="/" className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base text-slate-900 tracking-tight">HostelPulse</span>
              <span className="text-[10px] font-mono font-semibold uppercase px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                AI Triage
              </span>
            </div>
            <span className="text-xs text-slate-500 hidden sm:block">Campus Complaint Management</span>
          </div>
        </Link>

        {/* Right side controls */}
        <div className="flex items-center gap-3">
          
          {/* AI Status Badge */}
          <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200 text-xs text-slate-600">
            <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
            <span className="font-mono text-[11px] font-medium">{aiEngine}</span>
          </div>

          {/* Role Status Tag */}
          {userType && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 text-xs text-slate-700">
              <span className="text-slate-500">Role:</span>
              <span className="font-semibold capitalize text-slate-900">{userType}</span>
            </div>
          )}

          {/* Quick Role Switchers */}
          <div className="hidden md:flex items-center gap-1 bg-slate-100 p-1 rounded-lg">
            <button
              onClick={() => quickSwitch("warden@hostel.edu", "warden123")}
              disabled={switching}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                userType === "warden"
                  ? "bg-white text-blue-700 shadow-2xs font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
              title="Switch to Warden view"
            >
              Warden
            </button>
            <button
              onClick={() => quickSwitch("student@hostel.edu", "student123")}
              disabled={switching}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                userType === "student"
                  ? "bg-white text-blue-700 shadow-2xs font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
              title="Switch to Student view"
            >
              Student
            </button>
          </div>

          {/* My Profile */}
          <Link
            to="/account"
            className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            title="My Profile"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </Link>

          {/* Logout */}
          <button
            onClick={logout}
            className="py-1.5 px-3 rounded-lg text-xs font-medium text-slate-700 hover:text-red-700 hover:bg-red-50 border border-slate-200 transition-colors"
          >
            Sign Out
          </button>
        </div>

      </div>
    </header>
  );
}

export default Navbar;
