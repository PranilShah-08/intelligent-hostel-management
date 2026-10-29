#!/usr/bin/env python3
"""
Launcher script for the Python FastAPI backend.
Runs on http://localhost:3000 to seamlessly power the frontend.
Listens on dual-stack IPv4/IPv6 so both 127.0.0.1, [::1], and localhost work seamlessly.
"""
import sys
import os
import socket
import uvicorn

if __name__ == "__main__":
    # Ensure current directory is in sys.path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
        
    print("🚀 Starting Intelligent Hostel Complaint Management System Backend (FastAPI)...")
    print("📍 URL: http://localhost:3000 (also http://127.0.0.1:3000)")
    print("📖 Interactive OpenAPI Docs: http://localhost:3000/docs")
    print("🧠 Local LLM Priority Engine: Ready")
    
    # Create dual-stack socket (IPv4 + IPv6) so macOS resolves localhost to both ::1 and 127.0.0.1 without ECONNREFUSED
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        sock.bind(("", 3000))
        sock.listen(128)
        config = uvicorn.Config("backend_py.main:app", fd=sock.fileno(), log_level="info")
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        print(f"Dual-stack bind notice ({e}), falling back to 0.0.0.0...")
        uvicorn.run("backend_py.main:app", host="0.0.0.0", port=3000)
