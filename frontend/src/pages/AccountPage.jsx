import React, { useState, useEffect } from "react";
import Navbar from "./Navbar";
import { useAuth } from "../utils/Auth";
import { Link, useNavigate } from "react-router-dom";

function AccountPage() {
  const navigate = useNavigate();
  const { headers } = useAuth();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const detailsRes = await fetch("http://localhost:3000/userDetails/me", { headers });
        if (detailsRes.ok) {
          const detailsData = await detailsRes.json();
          if (detailsData && detailsData.length > 0) {
            setUserData(detailsData[0]);
          }
        }
      } catch (err) {
        console.error("Profile fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-10">
        <div className="mb-6 flex items-center justify-between">
          <Link
            to="/"
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1.5"
          >
            ← Back to Dashboard
          </Link>
          <span className="text-xs text-slate-400">Authenticated Session</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-xs space-y-6">
          <div className="flex items-center gap-4 pb-6 border-b border-slate-100">
            <div className="h-14 w-14 rounded-full bg-blue-600 text-white flex items-center justify-center text-xl font-bold">
              {userData?.full_name ? userData.full_name[0].toUpperCase() : "U"}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-slate-900">
                  {userData?.full_name || "Hostel Resident"}
                </h1>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize border ${
                  userData?.type === "warden"
                    ? "bg-amber-50 text-amber-700 border-amber-200"
                    : "bg-emerald-50 text-emerald-700 border-emerald-200"
                }`}>
                  {userData?.type || "Resident"}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">{userData?.email}</p>
            </div>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-400 font-mono text-xs">
              Loading profile details...
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-slate-500 uppercase font-mono text-[10px] font-semibold">Contact Phone</span>
                <p className="font-semibold text-slate-900 text-sm">{userData?.phone || "Not provided"}</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-slate-500 uppercase font-mono text-[10px] font-semibold">Hostel Wing / Block</span>
                <p className="font-semibold text-slate-900 text-sm">{userData?.block_name || "Unassigned"}</p>
              </div>

              {userData?.type === "student" && (
                <>
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    <span className="text-slate-500 uppercase font-mono text-[10px] font-semibold">Room Number</span>
                    <p className="font-semibold text-slate-900 text-sm">{userData?.room || "Not assigned"}</p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    <span className="text-slate-500 uppercase font-mono text-[10px] font-semibold">Roll / USN Number</span>
                    <p className="font-semibold text-slate-900 text-sm font-mono">{userData?.usn || "Not specified"}</p>
                  </div>
                </>
              )}
            </div>
          )}

          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-400">Hostel Complaint Management System</span>
            <button
              onClick={() => {
                localStorage.removeItem("jwtToken");
                navigate("/login");
              }}
              className="px-4 py-2 rounded-lg text-xs font-medium text-red-600 hover:bg-red-50 border border-red-200 transition-colors"
            >
              Sign Out
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}

export default AccountPage;
