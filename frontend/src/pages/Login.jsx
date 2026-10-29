import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const performLogin = async (loginEmail, loginPass) => {
    setErrorMsg("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:3000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: loginEmail, password: loginPass }),
      });
      const data = await response.json();

      if (response.ok && data.jwtToken) {
        localStorage.setItem("jwtToken", data.jwtToken);
        navigate("/");
      } else {
        setErrorMsg(data.detail || data || "Invalid email or password.");
      }
    } catch (err) {
      console.error(err);
      setErrorMsg("Unable to connect to backend server.");
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    await performLogin(email, password);
  };

  const quickSignIn = async (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    await performLogin(demoEmail, demoPass);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        {/* Institutional Logo Icon */}
        <div className="inline-flex h-12 w-12 rounded-xl bg-blue-600 text-white items-center justify-center shadow-sm mb-3">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Hostel Complaint Management
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Sign in to lodge maintenance requests or manage hostel operations
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-sm border border-slate-200 rounded-2xl sm:px-10">
          
          {/* Quick Access Account Selector */}
          <div className="mb-6 p-3.5 bg-blue-50/60 border border-blue-200/80 rounded-xl">
            <div className="text-[11px] font-bold text-blue-900 uppercase tracking-wider text-center mb-2.5 flex items-center justify-center gap-1.5">
              <span>⚡</span> 1-Click Instant Demo Access:
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => quickSignIn("warden@hostel.edu", "warden123")}
                disabled={loading}
                className="py-2 px-3 text-xs font-semibold rounded-lg border border-blue-300 bg-white hover:bg-blue-50 text-blue-700 text-center transition-colors shadow-2xs flex items-center justify-center gap-1"
              >
                👔 Chief Warden
              </button>
              <button
                type="button"
                onClick={() => quickSignIn("student@hostel.edu", "student123")}
                disabled={loading}
                className="py-2 px-3 text-xs font-semibold rounded-lg border border-blue-300 bg-white hover:bg-blue-50 text-blue-700 text-center transition-colors shadow-2xs flex items-center justify-center gap-1"
              >
                🎓 Student (Pranil Shah)
              </button>
            </div>
            <div className="text-[10px] text-blue-600/90 text-center mt-2">
              Click either role above to test the live portal instantly
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg text-center">
              {errorMsg}
            </div>
          )}

          {/* Form */}
          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="warden@hostel.edu or student@hostel.edu"
                className="w-full px-3.5 py-2 text-sm bg-white border border-slate-300 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-2xs"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2 text-sm bg-white border border-slate-300 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-2xs"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg shadow-2xs transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {loading ? "Authenticating..." : "Sign In to Account"}
              </button>
            </div>
          </form>

          {/* Institutional note & registration link */}
          <div className="mt-6 pt-5 border-t border-slate-100 text-center space-y-2">
            <p className="text-xs text-slate-500">
              Need a new account?{" "}
              <Link to="/signup" className="font-semibold text-blue-600 hover:text-blue-500">
                Register as Student
              </Link>
            </p>
            <p className="text-[11px] text-slate-400">
              Intelligent Hostel Management System • Symbiosis Institute of Technology
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}

export default Login;
