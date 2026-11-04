"""
RefExplain AI - FastAPI Backend & Standalone Web App (Cricket Edition)
Provides live API endpoints and an interactive web interface for cricket umpire decision explanations and DRS reviews.
"""

import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from ai_engine import analyze_decision
from rules import CRICKET_RULES, ALL_RULES, SPORTS, get_supported_incidents, classify_incident
from visual_analyzer import decode_image_bytes, analyze_match_frame

STATIC_INDEX = os.path.join(os.path.dirname(__file__), "static", "index.html")

app = FastAPI(
    title="RefExplain AI - Cricket Decision Review Assistant",
    description="Intelligent cricket decision explanation service for live umpire decisions and ICC DRS reviews.",
    version="1.3.0"
)

# Enable CORS for Chrome Extensions and external web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class DecisionRequest(BaseModel):
    sport: Optional[str] = Field(default=None, description="Sport: 'football' or 'cricket' (auto-detected if omitted)")
    incident: Optional[str] = Field(default=None, description="Optional incident type. Auto-detected by AI from description/images if omitted")
    description: Optional[str] = Field(default="", description="Description of the incident or question (optional when uploading image)")
    image_base64: Optional[str] = Field(default=None, description="Optional base64-encoded match screenshot or broadcast frame")
    api_key: Optional[str] = Field(default=None, description="Optional Google Gemini API key for live generative vision AI")


class DecisionResponse(BaseModel):
    success: bool
    sport: str
    incident: str
    direct_decision: Optional[str] = Field(default="INCONCLUSIVE", description="Direct official call: OUT, NOT OUT, OFFSIDE, RED CARD, etc.")
    decision_summary: Optional[str] = Field(default="", description="One-sentence direct verdict summary")
    explanation: str
    assessment: str
    sections: Dict[str, str]
    has_image: bool = False
    engine_used: Optional[str] = Field(default="local_cv_fallback", description="Engine that processed the decision: Gemini Multimodal Vision or Local Heuristic Engine")
    warning_notice: Optional[str] = Field(default=None, description="Optional diagnostic warning notice")


# Curated presets for 1-click cricket testing & live demoing
PRESET_INCIDENTS = [
    {
        "id": "kohli-lbw-umpires-call",
        "sport": "cricket",
        "title": "Virat Kohli LBW Umpire's Call on Impact (Ind vs Aus)",
        "incident": "LBW / DRS Umpire's Call",
        "description": "Kohli played forward to a ball spinning sharply back in. The ball struck him on the front pad in line with off stump. The on-field umpire ruled Out. Kohli reviewed via DRS; ball tracking showed impact clipping the 50% line of off stump, so Umpire's Call stood."
    },
    {
        "id": "mathews-timed-out",
        "sport": "cricket",
        "title": "Angelo Mathews Timed Out vs Bangladesh (World Cup 2023)",
        "incident": "Timed Out",
        "description": "Mathews walked in to bat after Samarawickrama's dismissal. His helmet strap broke before taking guard. While waiting for a replacement helmet, Shakib Al Hasan appealed for 'Timed Out'. Umpires upheld the appeal as more than 2 minutes elapsed."
    },
    {
        "id": "deepti-mankad-dean",
        "sport": "cricket",
        "title": "Deepti Sharma Non-Striker Run Out vs Charlie Dean (Lord's 2022)",
        "incident": "Run Out at Non-Striker's End",
        "description": "England needed 17 runs to win with 1 wicket remaining. Non-striker Charlie Dean consistently backed up yards out of her crease. Deepti entered her delivery stride and took the bails off before completing the delivery swing. Dean was given out run out."
    },
    {
        "id": "nawaz-mcg-noball",
        "sport": "cricket",
        "title": "MCG 2022: Nawaz Waist-High Full Toss to Kohli",
        "incident": "Waist-High Full Toss (No Ball)",
        "description": "With India needing 13 off 3 balls, Mohammad Nawaz bowled a high full toss. Kohli pulled it over square leg for six and immediately signaled for a waist-height no-ball. The square-leg umpire signaled a No Ball, granting a free hit."
    },
    {
        "id": "pant-ultraedge-caught-behind",
        "sport": "cricket",
        "title": "Rishabh Pant UltraEdge Snicko Spike Dispute vs England",
        "incident": "Caught Behind / UltraEdge",
        "description": "Fast bowler bowled a delivery shaping past the outside edge. The keeper caught it and appealed. The on-field umpire gave Not Out. On DRS review, UltraEdge displayed a small murmur spike just as the ball was 2 inches past the bat blade. Umpire overturned to Out."
    },
    {
        "id": "boundary-relay-catch",
        "sport": "cricket",
        "title": "Boundary Rope Aerial Relay Catch",
        "incident": "Boundary Catch / Aerial Relay",
        "description": "Fielder leaps inside the boundary rope, catches ball airborne, tosses it into the air before his momentum takes him over the rope. He steps back inside the boundary cushions and completes the catch cleanly."
    },
    {
        "id": "low-catch-grounded",
        "sport": "cricket",
        "title": "Low Catch Grounding & Turf Contact Review",
        "incident": "Fair Catch / Grounded Catch (MCC Law 33)",
        "description": "Fielder dived forward to take a low catch inches above the turf. On-field umpires referred upstairs to verify whether fingers were cleanly underneath the ball or if the leather touched grass blades before control was secured."
    },
    {
        "id": "run-out-crease-grounding",
        "sport": "cricket",
        "title": "Run Out: Diving Batter Crease Grounding Check",
        "incident": "Run Out / Crease Grounding (MCC Law 38)",
        "description": "A diving batter stretches with outstretched bat towards the popping crease while the wicketkeeper breaks the wickets. The third umpire inspects side-on super-slow-mo frames to determine whether the bat grounded behind the crease before the bails separated."
    }
]


def health_check() -> Dict[str, Any]:
    """Base health check payload."""
    return {
        "status": "online",
        "service": "RefExplain AI (Cricket Edition)",
        "version": "1.3.0",
        "sports": {
            "cricket": {
                "name": "Cricket",
                "governing_body": "MCC Laws of Cricket & ICC DRS Playing Conditions",
                "supported_incidents": list(CRICKET_RULES.keys())
            }
        },
        "supported_incidents": list(ALL_RULES.keys())
    }


@app.get("/", tags=["Web App & Health"])
def root_endpoint(request: Request = None):
    """
    Serves the interactive web app when visited in a web browser,
    or returns health status when accessed programmatically.
    """
    if request:
        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header and os.path.exists(STATIC_INDEX):
            return FileResponse(STATIC_INDEX, media_type="text/html")
    return health_check()


@app.get("/app", tags=["Web App"])
@app.get("/web", tags=["Web App"])
def web_app():
    """Serves the standalone browser application for zero-install evaluation."""
    if os.path.exists(STATIC_INDEX):
        return FileResponse(STATIC_INDEX, media_type="text/html")
    return {"message": "RefExplain Web App: static/index.html not found"}


@app.get("/health", tags=["Health"])
def health_endpoint():
    """Dedicated API health check endpoint."""
    return health_check()


@app.get("/presets", tags=["Presets"])
def get_presets(sport: Optional[str] = None):
    """Returns curated presets for quick 1-click scenario demonstrations."""
    if sport and isinstance(sport, str):
        filtered = [p for p in PRESET_INCIDENTS if p.get("sport", "").lower() == sport.lower()]
        return {"sport": sport, "presets": filtered}
    return {"presets": PRESET_INCIDENTS}


@app.get("/benchmark", tags=["Evaluation"])
def get_benchmark():
    """
    Runs the automated accuracy benchmark suite across verified ground truth cases
    and returns quantitative accuracy percentages and latency metrics.
    """
    from evaluate_accuracy import run_benchmark
    return run_benchmark()


@app.post("/analyze", response_model=DecisionResponse, tags=["Analysis"])
def analyze(request: DecisionRequest):
    """
    Analyzes a user-described controversial decision using the AI Engine & official sports rules.
    Automatically identifies the applicable rule category and sport if omitted, or extracts directly from image.
    """
    sport = (request.sport or "").lower().strip() or None
    incident = (request.incident or "").strip() or None
    description = (request.description or "").strip()
    image_base64 = request.image_base64

    if not description and not image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide an incident description or upload a match screenshot."
        )

    if request.api_key and request.api_key.strip():
        os.environ["GEMINI_API_KEY"] = request.api_key.strip()

    # 1. PRIORITY 1: User's explicit text inquiry/description
    # If user provided a meaningful description, classify the incident from their text first!
    if not incident or incident not in ALL_RULES:
        if description and len(description.strip()) >= 4 and not description.lower().startswith("direct visual match"):
            detected_incident, detected_sport = classify_incident(description, sport)
            if detected_incident:
                incident = detected_incident
                if not sport:
                    sport = detected_sport

    # 2. PRIORITY 2: Direct visual frame inspection if an image is attached
    visual_info = None
    if image_base64:
        raw_bytes, _ = decode_image_bytes(image_base64)
        if raw_bytes:
            visual_info = analyze_match_frame(raw_bytes, sport_hint=sport)

    # If incident is still not identified (user provided no text or vague query), adopt visual detection
    if not incident or incident not in ALL_RULES:
        if visual_info and visual_info.get("incident"):
            incident = visual_info.get("incident")
            if not sport:
                sport = visual_info.get("sport")
            if not description:
                description = f"Direct visual match frame analysis: {visual_info.get('decision_summary', 'Broadcast replay frame inspected.')}"

    # 3. PRIORITY 3: Fallback classification if still unresolved
    if not incident or incident not in ALL_RULES:
        detected_incident, detected_sport = classify_incident(description, sport)
        incident = detected_incident
        if not sport:
            sport = detected_sport

    # Cricket-only mode
    sport = "cricket"

    user_api_key = (request.api_key or "").strip() or os.getenv("GEMINI_API_KEY", "").strip()

    try:
        res = analyze_decision(
            incident=incident,
            description=description,
            sport=sport,
            image_data=image_base64,
            visual_info=visual_info,
            api_key=user_api_key
        )
        raw_explanation = res[0]
        sections = res[1]
        assessment = res[2]
        direct_decision = res[3]
        decision_summary = res[4]
        final_sport = res[5] if len(res) > 5 else sport
        final_incident = res[6] if len(res) > 6 else incident
        engine_used = res[7] if len(res) > 7 else "Local Heuristic Engine (Offline Fallback)"
        warning_notice = res[8] if len(res) > 8 else None

        return DecisionResponse(
            success=True,
            sport=final_sport,
            incident=final_incident,
            direct_decision=direct_decision,
            decision_summary=decision_summary,
            explanation=raw_explanation,
            assessment=assessment,
            sections=sections,
            has_image=bool(image_base64),
            engine_used=engine_used,
            warning_notice=warning_notice
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to analyze decision: {str(e)}"
        )
