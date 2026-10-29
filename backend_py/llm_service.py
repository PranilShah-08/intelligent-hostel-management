"""
Local LLM Priority and Urgency Analysis Service.
Supports:
1. Local Ollama API (http://localhost:11434) with models like llama3.2, mistral, phi3, qwen, deepseek, etc.
2. Built-in Embedded Local Priority Heuristic Engine (zero-latency, 100% offline fallback).
"""

import httpx
import json
import logging
import re
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"

# Keyword dictionary with weights and hazard profiles
EMERGENCY_SIGNALS = {
    "life_safety": {
        "weight": 45,
        "keywords": ["spark", "fire", "smoke", "burning", "electric shock", "shock", "live wire", "short circuit",
                     "gas", "explosion", "flame", "bleeding", "unconscious", "medical", "collapse", "ceiling falling"],
        "category": "Electrical",
        "action": "Trigger emergency alarm, cut relevant breakers/valves, and dispatch first-response technicians immediately."
    },
    "security_threat": {
        "weight": 35,
        "keywords": ["intruder", "theft", "stolen", "break-in", "broken lock", "lock broken", "latch broken", 
                     "harassment", "trespassing", "door won't lock", "cannot lock", "unlocked main door"],
        "category": "Safety & Security",
        "action": "Deploy on-duty security guard to location and arrange emergency locksmith service."
    },
    "flooding_hazard": {
        "weight": 30,
        "keywords": ["flood", "pipe burst", "burst pipe", "overflowing sewage", "water leaking onto switch", 
                     "water entering room", "gushing water", "drowning", "submerged"],
        "category": "Plumbing",
        "action": "Shut off main water inlet valve for the affected block and dispatch urgent plumbing crew."
    },
    "health_sanitation": {
        "weight": 20,
        "keywords": ["sewage", "foul smell", "stagnant water", "maggots", "rats", "rodent", "snake", 
                     "bedbugs", "infestation", "contaminated water", "black water"],
        "category": "Cleanliness & Hygiene",
        "action": "Quarantine affected area, deploy pest control/deep cleaning and issue hygiene alerts."
    },
    "basic_amenity": {
        "weight": 12,
        "keywords": ["no water", "no electricity", "power cut", "blackout", "geyser not working", 
                     "tap broken", "flush not working", "clogged toilet"],
        "category": "Plumbing",
        "action": "Check floor supply lines, assign daytime facility technician."
    },
    "network_infrastructure": {
        "weight": 8,
        "keywords": ["wifi down", "no internet", "lan port", "slow wifi", "router not working", "network down"],
        "category": "Internet & Network",
        "action": "Reboot floor access point / router; report to campus network administrator if outage persists."
    },
    "minor_furniture": {
        "weight": 5,
        "keywords": ["table squeak", "chair broken", "desk scratch", "wardrobe latch", "window curtain", 
                     "fan noise", "bulb fused", "light bulb", "paint peeling"],
        "category": "Carpentry & Furniture",
        "action": "Log into routine maintenance queue for batch resolution during scheduled rounds."
    }
}


def local_embedded_classifier(title: str, description: str, room: str = "", block: str = "") -> Dict[str, Any]:
    """
    High-accuracy local rule/NLP urgency engine.
    Always available instantly without requiring external GPU or downloads.
    """
    text = f"{title} {description}".lower()
    score = 15  # Base urgency baseline
    matched_signals: List[str] = []
    primary_category = "General Maintenance"
    suggested_action = "Inspect room during regular warden inspection rounds."
    
    # Assess signals
    for signal_name, signal_data in EMERGENCY_SIGNALS.items():
        found = []
        for kw in signal_data["keywords"]:
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            if pattern.search(text):
                found.append(kw)
        if found:
            score += signal_data["weight"]
            matched_signals.append(f"{signal_name} ({', '.join(found[:2])})")
            if primary_category == "General Maintenance" or signal_data["weight"] > 15:
                primary_category = signal_data["category"]
                suggested_action = signal_data["action"]

    # Compound hazard multiplier (e.g. water + electricity)
    has_water = any(w in text for w in ["water", "leak", "pipe", "tap", "shower", "drip"])
    has_electric = any(e in text for e in ["wire", "switch", "electric", "spark", "plug", "socket", "power"])
    if has_water and has_electric:
        score += 35
        matched_signals.append("COMPOUND HAZARD: Water + Electricity Risk")
        primary_category = "Electrical"
        suggested_action = "CRITICAL: Isolate electrical supply before touching any water. Immediate emergency dispatch."

    # Room/Corridor context
    if "washroom" in text or "bathroom" in text or "corridor" in text or "staircase" in text:
        score += 8  # Common areas affect more residents

    # Clamp score
    final_score = min(max(score, 10), 99)

    # Determine priority tier and SLA
    if final_score >= 80:
        priority = "CRITICAL"
        sla_hours = 2
        reasoning = f"Severe emergency/safety threat detected ({', '.join(matched_signals) if matched_signals else 'High-impact incident'}). Threatens resident safety or structural integrity."
    elif final_score >= 60:
        priority = "HIGH"
        sla_hours = 8
        reasoning = f"Significant disruption or security/health risk ({', '.join(matched_signals) if matched_signals else 'Urgent disruption'}). Requires expedited resolution within current shift."
    elif final_score >= 35:
        priority = "MEDIUM"
        sla_hours = 24
        reasoning = f"Standard living amenity failure. Non-life-threatening but impacts student daily comfort."
    else:
        priority = "LOW"
        sla_hours = 72
        reasoning = f"Minor cosmetic or routine maintenance request. Can be handled during scheduled batch maintenance."

    return {
        "priority": priority,
        "priority_score": final_score,
        "category": primary_category,
        "urgency_reason": reasoning,
        "suggested_action": suggested_action,
        "sla_hours": sla_hours,
        "ai_engine": "Embedded Local NLP Prioritizer (Active)"
    }


async def check_ollama_status() -> Dict[str, Any]:
    """Check if local Ollama daemon is reachable and list installed models."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", [])]
                return {
                    "available": True,
                    "models": models,
                    "active_model": models[0] if models else None,
                    "url": OLLAMA_BASE_URL,
                    "message": f"Ollama is running with {len(models)} model(s) installed." if models else "Ollama is running (no models pulled yet; embedded local engine active)."
                }
    except Exception as e:
        logger.debug(f"Ollama status check: {e}")
    
    return {
        "available": False,
        "models": [],
        "active_model": None,
        "url": OLLAMA_BASE_URL,
        "message": "Ollama service not running. Using high-speed embedded local priority classifier."
    }


async def analyze_with_ollama(title: str, description: str, room: str = "", block: str = "", model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Attempt analysis via local Ollama LLM."""
    status = await check_ollama_status()
    if not status["available"] or not status["models"]:
        return None

    selected_model = model_name or status["active_model"] or DEFAULT_MODEL
    
    prompt = f"""You are an intelligent hostel administration AI for a university campus.
Analyze this student grievance and output a valid JSON object ONLY.

Complaint Title: {title}
Complaint Description: {description}
Room Number: {room}
Hostel Block: {block}

Evaluate the severity, risk to human life, property damage, hygiene, or security breaches.
Output strictly JSON matching this structure:
{{
  "priority": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "priority_score": integer between 1 and 100,
  "category": "Electrical" | "Plumbing" | "Safety & Security" | "Cleanliness & Hygiene" | "Internet & Network" | "Carpentry & Furniture" | "General",
  "urgency_reason": "Clear explanation in 1-2 sentences of why this priority score was assigned",
  "suggested_action": "Concrete immediate step the hostel warden should execute",
  "sla_hours": integer hours target (e.g. 2 for Critical, 8 for High, 24 for Medium, 72 for Low)
}}
Do NOT output markdown code fences, do not output explanations outside the JSON. Return only the JSON object.
"""

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": selected_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            if resp.status_code == 200:
                result = resp.json().get("response", "")
                parsed = json.loads(result)
                parsed["ai_engine"] = f"Ollama Local LLM ({selected_model})"
                # Validate fields
                if "priority" in parsed and "priority_score" in parsed:
                    return parsed
    except Exception as err:
        logger.warning(f"Ollama inference error: {err}. Falling back to embedded local NLP.")

    return None


async def prioritize_complaint(title: str, description: str, room: str = "", block: str = "", preferred_model: Optional[str] = None) -> Dict[str, Any]:
    """
    Master triage function:
    1. Tries local Ollama LLM if available with models.
    2. Gracefully falls back to high-fidelity embedded local NLP classifier.
    Never fails or throws unhandled errors.
    """
    # Try Ollama first
    ollama_result = await analyze_with_ollama(title, description, room, block, preferred_model)
    if ollama_result:
        return ollama_result

    # Fallback to local embedded classifier
    return local_embedded_classifier(title, description, room, block)
