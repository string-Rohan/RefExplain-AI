"""
RefExplain AI - AI Engine
Integrates with Google Gemini API (gemini-2.5-flash) to evaluate controversial football and cricket decisions.
Provides structured section parsing and graceful fallback for demonstration across both sports.
"""

import os
import re
import base64
from typing import Dict, Any, Tuple, Optional
from rules import CRICKET_RULES, ALL_RULES, get_rule, SPORTS, classify_incident
from dynamic_engine import synthesize_dynamic_explanation

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

# Pre-curated fallback explanations for common demo scenarios in Cricket
FALLBACK_EXPLANATIONS = {
    # --- CRICKET FALLBACKS ---
    "Fair Catch / Grounded Catch (MCC Law 33)": {
        "text": (
            "1. WHAT HAPPENED\n"
            "A fielder dived forward attempting a low scoop catch close to the grass surface. "
            "The on-field umpires or third TV umpire reviewed whether the ball was gathered cleanly with fingers "
            "underneath, or whether the ball contacted the grass/turf before the fielder gained complete control.\n\n"
            "2. APPLICABLE RULE\n"
            "MCC Law 33 (Caught) & Law 33.2 (Fair Catch / Ball Grounding Protocols): A striker is out Caught only if "
            "the ball is caught fairly before touching the ground. If the ball touches the ground or grass blades while "
            "sliding before the fielder obtains complete control over both the ball and their own movement, it is NOT a "
            "fair catch and the batter is NOT OUT. If the fielder's fingers are completely underneath the ball cushioning "
            "it from turf contact, the catch is fair (OUT).\n\n"
            "3. WHY THE UMPIRE MAY HAVE MADE THIS DECISION\n"
            "The third umpire reviewed synchronized super slow-motion zoom replays (front-on and reverse angles). "
            "If video frames show the leather of the ball touching blades of grass or if fingers split apart during the slide "
            "without conclusive proof that fingers remained fully underneath, the benefit of the doubt requires a NOT OUT ruling.\n\n"
            "4. WHAT EVIDENCE SHOULD BE CHECKED\n"
            "- Ultra-slow-motion zoom frames at the lowest point of the fielder's scoop.\n"
            "- Finger positioning: Were the fingers cup-shaped underneath the ball or split open on the grass?\n"
            "- Grass blade deflection: Did grass blades bend or trap under the ball's seam?\n"
            "- Ball wobble / impact: Did the ball dislodge or contact the turf when the fielder's elbows hit the ground?\n\n"
            "5. AI ASSESSMENT\n"
            "Appears correct"
        ),
        "assessment": "Appears correct"
    },
    "LBW / DRS Umpire's Call": {
        "text": (
            "1. WHAT HAPPENED\n"
            "The bowling team appealed for LBW after the ball struck the batter's pad. "
            "A DRS review was requested to inspect pitching, impact, and projected wicket contact.\n\n"
            "2. APPLICABLE RULE\n"
            "MCC Law 36 (Leg Before Wicket) & ICC DRS Appendix D: Delivery must pitch in line or outside off "
            "(never outside leg). If a shot is played, impact must be in line with wickets. Ball tracking must project "
            "the ball hitting the stumps with at least 50% ball volume to overturn an on-field not out.\n\n"
            "3. WHY THE UMPIRE MAY HAVE MADE THIS DECISION\n"
            "The on-field umpire judged either that the batter made impact outside off stump while offering a stroke, "
            "or that the trajectory was bouncing over or shaving the stumps (Umpire's Call margin).\n\n"
            "4. WHAT EVIDENCE SHOULD BE CHECKED\n"
            "- UltraEdge to confirm zero bat contact before pad.\n"
            "- Pitch mat to confirm ball did not pitch outside leg stump line.\n"
            "- Hawk-Eye / Ball Tracking impact point relative to the outer edge of off and leg stumps.\n"
            "- Ball tracking projection height at the stumps.\n\n"
            "5. AI ASSESSMENT\n"
            "Inconclusive"
        ),
        "assessment": "Inconclusive"
    },
    "Caught Behind / UltraEdge": {
        "text": (
            "1. WHAT HAPPENED\n"
            "The fielding team appealed for a catch behind by the wicketkeeper or slip fielder, "
            "alleging the ball glanced the bat's outside edge before being gathered.\n\n"
            "2. APPLICABLE RULE\n"
            "MCC Law 33 (Caught): The ball must make contact with the bat (or the glove holding the bat) "
            "and be held cleanly by the fielder before touching the pitch surface.\n\n"
            "3. WHY THE UMPIRE MAY HAVE MADE THIS DECISION\n"
            "The umpire listened for a distinct deflection acoustic or observed a deviation in the ball's seam axis "
            "as it passed the bat blade.\n\n"
            "4. WHAT EVIDENCE SHOULD BE CHECKED\n"
            "- Synchronized UltraEdge (RTS) waveform spike aligned with the frame the ball passes the bat edge.\n"
            "- Frame gap between bat and ball (to rule out bat clipping the pad or turf).\n"
            "- Split-screen zoom to verify keeper's fingers were completely under the ball when caught.\n\n"
            "5. AI ASSESSMENT\n"
            "Appears correct"
        ),
        "assessment": "Appears correct"
    },
    "Run Out at Non-Striker's End": {
        "text": (
            "1. WHAT HAPPENED\n"
            "The bowler broke the stumps at the non-striker's end before releasing the ball because the non-striker "
            "had backed up out of their crease.\n\n"
            "2. APPLICABLE RULE\n"
            "MCC Law 38.3 (Run Out of the non-striker): A bowler is fully permitted to run out the non-striker if they "
            "leave their ground before the instant the bowler would normally have been expected to release the ball.\n\n"
            "3. WHY THE UMPIRE MAY HAVE MADE THIS DECISION\n"
            "The umpire verified on replay that the bowler had not completed their bowling arm swing past the normal release point "
            "when the bails were dislodged, and the non-striker had no part of their person or bat grounded behind the crease.\n\n"
            "4. WHAT EVIDENCE SHOULD BE CHECKED\n"
            "- Side-on camera: Non-striker's bat/foot position relative to the popping crease line.\n"
            "- Delivery stride release point: Was the bowler's arm past vertical / normal release point when bails were broken?\n\n"
            "5. AI ASSESSMENT\n"
            "Appears correct"
        ),
        "assessment": "Appears correct"
    },
    "Waist-High Full Toss (No Ball)": {
        "text": (
            "1. WHAT HAPPENED\n"
            "A fast or spin delivery did not pitch before reaching the batter and passed around or above the waist height, "
            "sparking debate over whether it was an illegal dangerous full toss (No Ball).\n\n"
            "2. APPLICABLE RULE\n"
            "MCC Law 41.7 & ICC Playing Conditions: Any ball that passes, or would have passed, on the full above the waist height "
            "of the striker standing upright at the popping crease is deemed unfair and shall be called a No Ball.\n\n"
            "3. WHY THE UMPIRE MAY HAVE MADE THIS DECISION\n"
            "The square-leg umpire assessed the ball's trajectory as dipping or judged that the batter was crouched/bent-kneed "
            "or stood well outside the crease, making the projected height at the crease legal.\n\n"
            "4. WHAT EVIDENCE SHOULD BE CHECKED\n"
            "- Hawk-Eye waist-height trajectory tracking at the popping crease line.\n"
            "- Striker's pre-recorded upright standing waist height measurement.\n"
            "- Whether the delivery was dipping or maintaining an upward flight angle.\n\n"
            "5. AI ASSESSMENT\n"
            "Inconclusive"
        ),
        "assessment": "Inconclusive"
    },
    "Boundary Catch / Aerial Relay": {
        "text": (
            "1. WHAT HAPPENED\n"
            "A boundary rider intercepted a lofted shot near the boundary rope, popped the ball into the air while airborne, "
            "stepped over the boundary rope, and re-caught it or relayed to a teammate.\n\n"
            "2. APPLICABLE RULE\n"
            "MCC Law 19 (Boundaries) & Law 33.2: First contact must be made inside the boundary. Any fielder jumping from beyond "
            "the boundary must re-ground themselves inside the playing field before touching the ball again.\n\n"
            "3. WHY THE UMPIRE MAY HAVE MADE THIS DECISION\n"
            "The TV umpire verified that the fielder released the ball before any part of their body touched the boundary cushion, "
            "and was legally grounded inside when completing the catch.\n\n"
            "4. WHAT EVIDENCE SHOULD BE CHECKED\n"
            "- Boundary camera angles: Any foot or hand contact with the rope or turf beyond while in contact with the ball.\n"
            "- Re-grounding frame: Did the fielder plant their feet inside the rope before touching the ball the second time?\n\n"
            "5. AI ASSESSMENT\n"
            "Appears correct"
        ),
        "assessment": "Appears correct"
    },
    "Timed Out": {
        "text": (
            "1. WHAT HAPPENED\n"
            "An incoming batter arrived at the wicket but faced delay (e.g. equipment issue), and the fielding side appealed "
            "for a dismissal under the Timed Out regulation.\n\n"
            "2. APPLICABLE RULE\n"
            "MCC Law 40 & ICC World Cup Playing Condition 40.1.1: The incoming batter must be ready to receive the ball within "
            "2 minutes of the previous dismissal (3 minutes under standard MCC rules). Fielding captain must lodge a formal appeal.\n\n"
            "3. WHY THE UMPIRE MAY HAVE MADE THIS DECISION\n"
            "The umpires consulted the broadcast match clock and confirmed that 2 minutes had elapsed without the batter being ready "
            "to take guard, and the fielding captain maintained the dismissal appeal.\n\n"
            "4. WHAT EVIDENCE SHOULD BE CHECKED\n"
            "- Broadcast official timestamp from moment previous wicket fell to when incoming batter was ready.\n"
            "- Whether equipment failure was reported to and sanctioned by the umpires before time elapsed.\n"
            "- Confirmation of the fielding captain's official appeal.\n\n"
            "5. AI ASSESSMENT\n"
            "Appears correct"
        ),
        "assessment": "Appears correct"
    }
}

# Alias mappings for rule variations
FALLBACK_EXPLANATIONS["Fair Catch / Caught Out (MCC Law 33)"] = FALLBACK_EXPLANATIONS["Fair Catch / Grounded Catch (MCC Law 33)"]
FALLBACK_EXPLANATIONS["Fair Catch"] = FALLBACK_EXPLANATIONS["Fair Catch / Grounded Catch (MCC Law 33)"]
FALLBACK_EXPLANATIONS["Grounded Catch"] = FALLBACK_EXPLANATIONS["Fair Catch / Grounded Catch (MCC Law 33)"]
FALLBACK_EXPLANATIONS["Caught"] = FALLBACK_EXPLANATIONS["Fair Catch / Grounded Catch (MCC Law 33)"]

# Default direct decisions and plain-language summaries
DEFAULT_DIRECT_DECISIONS = {
    "Fair Catch / Grounded Catch (MCC Law 33)": {
        "decision": "NOT OUT",
        "summary": "The ball contacted the grass blades before complete control was established; Not Out under MCC Law 33.2."
    },
    "LBW / DRS Umpire's Call": {
        "decision": "UMPIRE'S CALL",
        "summary": "DRS ball tracking projected marginal contact on the stump margin; on-field umpire's call is upheld."
    },
    "Caught Behind / UltraEdge": {
        "decision": "OUT CAUGHT BEHIND",
        "summary": "UltraEdge acoustic waveform confirmed ball contact with the bat edge before being caught."
    },
    "Run Out / Crease Grounding (MCC Law 38)": {
        "decision": "RUN OUT REVIEW (MCC LAW 38)",
        "summary": "TV umpire run-out review: camera inspects whether any part of the bat or person was grounded behind the popping crease when the bails were dislodged."
    },
    "Run Out at Non-Striker's End": {
        "decision": "OUT RUN OUT",
        "summary": "Non-striker was out of their crease before the bowler's normal delivery release point; legally out under MCC Law 38.3."
    },
    "Waist-High Full Toss (No Ball)": {
        "decision": "NO BALL",
        "summary": "Delivery passed on the full above the batter's upright waist height at the crease; called No Ball plus Free Hit under MCC Law 41.7."
    },
    "Boundary Catch / Aerial Relay": {
        "decision": "BOUNDARY REVIEW (MCC LAW 19)",
        "summary": "Boundary review under MCC Law 19 & Law 33.2: camera angles inspect whether the fielder touched the boundary cushion or rope while in contact with the ball (Six/Boundary if touched, Out Caught if cleanly completed inside)."
    },
    "Timed Out": {
        "decision": "TIMED OUT",
        "summary": "Incoming batter failed to be in position to receive the ball within 2 minutes of the previous dismissal under MCC Law 40."
    }
}


# Prioritized multimodal vision models for Gemini API (fast failover if a model is deprecated or rate-limited)
VISION_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
]


def call_gemini_vision_rest(
    image_bytes: Optional[bytes],
    mime_type: str,
    prompt: str,
    api_key: str
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Calls Gemini REST API using prioritized model fallback chain.
    Returns: (raw_text, successful_model_name, error_message_if_failed)
    """
    try:
        import urllib.request
        import urllib.error
        import json

        parts = [{"text": prompt}]
        if image_bytes:
            b64_img = base64.b64encode(image_bytes).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_img
                }
            })

        payload = {"contents": [{"parts": parts}]}
        req_data = json.dumps(payload).encode("utf-8")

        last_error = None
        for model in VISION_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {})
                        content_parts = content.get("parts", [])
                        if content_parts:
                            text = content_parts[0].get("text", "")
                            if text:
                                return text, model, None
            except urllib.error.HTTPError as e:
                err_body = ""
                try:
                    err_body = e.read().decode("utf-8")
                except Exception:
                    pass
                last_error = f"{model} HTTP {e.code}: {err_body[:120]}"
                print(f"[RefExplain AI] Gemini model '{model}' notice: {last_error}")
                if e.code == 400 and "API_KEY_INVALID" in err_body:
                    return None, None, "Invalid Gemini API Key provided."
                continue
            except Exception as e:
                last_error = f"{model} error: {e}"
                print(f"[RefExplain AI] Gemini model '{model}' error: {e}")
                continue

        return None, None, last_error
    except Exception as e:
        print(f"[RefExplain AI] Gemini REST call exception: {e}")
        return None, None, str(e)


def parse_explanation_sections(raw_text: str) -> Tuple[Dict[str, str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Parses the 5 standardized sections, sport, incident, and direct decision from raw AI text into structured fields.
    Accommodates both Football (Referee) and Cricket (Umpire) terminology.
    Returns: (sections_dict, direct_decision, decision_summary, detected_sport, detected_incident)
    """
    sections = {
        "what_happened": "",
        "applicable_rule": "",
        "referee_reasoning": "",
        "evidence_to_check": "",
        "assessment": "Inconclusive"
    }

    # Extract optional sport and incident from text header lines
    detected_sport = None
    detected_incident = None

    sport_match = re.search(r"^SPORT[:\s]*([^\n\r]+)", raw_text, re.IGNORECASE | re.MULTILINE)
    if sport_match:
        detected_sport = sport_match.group(1).strip()

    inc_match = re.search(r"^INCIDENT[:\s]*([^\n\r]+)", raw_text, re.IGNORECASE | re.MULTILINE)
    if inc_match:
        detected_incident = inc_match.group(1).strip()

    # Extract direct decision and summary from text
    direct_decision = None
    decision_summary = None

    d_match = re.search(r"DIRECT DECISION[:\s]*([^\n\r]+)", raw_text, re.IGNORECASE)
    if d_match:
        direct_decision = d_match.group(1).strip()

    s_match = re.search(r"DECISION SUMMARY[:\s]*([^\n\r]+)", raw_text, re.IGNORECASE)
    if s_match:
        decision_summary = s_match.group(1).strip()

    patterns = [
        (r"(?:1\.\s*WHAT HAPPENED[:\s]*)([\s\S]*?)(?=(?:2\.\s*APPLICABLE RULE|$))", "what_happened"),
        (r"(?:2\.\s*APPLICABLE RULE[:\s]*)([\s\S]*?)(?=(?:3\.\s*WHY THE (?:REFEREE|UMPIRE)|$))", "applicable_rule"),
        (r"(?:3\.\s*WHY THE (?:REFEREE|UMPIRE)(?: MAY HAVE MADE THIS DECISION)?[:\s]*)([\s\S]*?)(?=(?:4\.\s*WHAT EVIDENCE|$))", "referee_reasoning"),
        (r"(?:4\.\s*WHAT EVIDENCE SHOULD BE CHECKED[:\s]*)([\s\S]*?)(?=(?:5\.\s*AI ASSESSMENT|$))", "evidence_to_check"),
        (r"(?:5\.\s*AI ASSESSMENT[:\s]*)([\s\S]*?)$", "assessment")
    ]

    for pattern, key in patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()

    # Normalize assessment value
    assessment_raw = sections["assessment"].lower()
    if "appears correct" in assessment_raw:
        sections["assessment"] = "Appears correct"
    elif "appears incorrect" in assessment_raw:
        sections["assessment"] = "Appears incorrect"
    else:
        sections["assessment"] = "Inconclusive"

    return sections, direct_decision, decision_summary, detected_sport, detected_incident


def analyze_decision(
    incident: Optional[str] = None,
    description: str = "",
    sport: Optional[str] = None,
    image_data: Optional[str] = None,
    visual_info: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> Tuple[str, Dict[str, str], str, str, str, str, str, str, Optional[str]]:
    """
    Analyzes a sports decision (Football or Cricket) using Gemini Multimodal Vision API or local heuristic fallback.
    Automatically detects and refines incident rule category and direct decision from image and text.
    Returns:
        (raw_text, sections, assessment, direct_decision, decision_summary, final_sport, final_incident, engine_used, warning_notice)
    """
    if not incident or incident not in ALL_RULES:
        detected_incident, detected_sport = classify_incident(description, sport)
        incident = detected_incident
        if not sport:
            sport = detected_sport

    rule = get_rule(incident, sport)
    if not rule:
        supported = list(ALL_RULES.keys())
        raise ValueError(f"Unsupported incident type: '{incident}'. Supported incidents: {supported}")

    # Cricket authority context
    sport_name = "Cricket"
    official_authority = "MCC Laws of Cricket & ICC Standard Playing Conditions with DRS Protocols"
    decision_maker = "Umpire"

    # Default decisions
    default_meta = DEFAULT_DIRECT_DECISIONS.get(incident, {
        "decision": "INCONCLUSIVE",
        "summary": "Match incident evaluated against official rules."
    })
    direct_decision = default_meta["decision"]
    decision_summary = default_meta["summary"]

    if visual_info:
        if visual_info.get("direct_decision"):
            direct_decision = visual_info["direct_decision"]
        if visual_info.get("decision_summary"):
            decision_summary = visual_info["decision_summary"]

    # Process image data if provided (extract raw bytes & mime_type from base64)
    raw_image_bytes = None
    image_mime_type = "image/jpeg"
    if image_data:
        try:
            b64_str = image_data.strip()
            if "," in b64_str:
                header, b64_str = b64_str.split(",", 1)
                if "image/png" in header:
                    image_mime_type = "image/png"
                elif "image/webp" in header:
                    image_mime_type = "image/webp"
                elif "image/gif" in header:
                    image_mime_type = "image/gif"
            raw_image_bytes = base64.b64decode(b64_str)
        except Exception as err:
            print(f"[RefExplain AI] Error decoding image base64: {err}")
            raw_image_bytes = None

    active_key = (api_key or "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    warning_notice = None

    # If Gemini API key is configured, call Gemini Multimodal Vision API via REST
    if active_key and active_key not in ["your_gemini_api_key", "your_gemini_api_key_here"]:
        visual_instructions = ""
        if raw_image_bytes:
            visual_instructions = """
MATCH IMAGE EVIDENCE:
A broadcast screenshot / match frame of this cricket incident is attached. Inspect the visible player positions, contact points, ball trajectory, pitch lines, boundary cushion contact, run out crease grounding (bat tip position relative to popping crease line and wicket dislodgment), or low catch grounding (fingers underneath ball vs turf contact) shown in the image to verify against official MCC Laws and DRS protocols.

If the user's description is brief or asks an open question (e.g. 'out or not?', 'is this catch or boundary?', 'is he run out?'):
- Identify the exact cricket incident type:
  * 'Run Out / Crease Grounding (MCC Law 38)'
  * 'Fair Catch / Grounded Catch (MCC Law 33)'
  * 'Boundary Catch / Aerial Relay'
  * 'LBW / DRS Umpire's Call'
  * 'Caught Behind / UltraEdge'
  * 'Waist-High Full Toss (No Ball)'
  * 'Timed Out'
"""

        prompt = f"""
You are RefExplain AI, an authoritative, impartial cricket decision explanation assistant for live cricket viewers.

SPORT CONTEXT:
Cricket (Governed by {official_authority})

CURRENT INCIDENT CATEGORY HINT:
{incident}

FAN INQUIRY / DESCRIPTION:
{description or 'Review the visual match frame and determine the decision.'}
{visual_instructions}
OFFICIAL RULE REFERENCE:
{rule}

Explain the decision directly and clearly to an ordinary cricket fan watching a live match.

You MUST structure your response into EXACTLY these header lines and 5 numbered sections:

SPORT: Cricket
INCIDENT: <Exact Rule Category>
DIRECT DECISION: <OUT | NOT OUT | UMPIRE'S CALL | NO BALL | TIMED OUT | INCONCLUSIVE>
DECISION SUMMARY: <A single concise sentence stating the direct official call and key visual reason>

1. WHAT HAPPENED
(Summarize the event based strictly on the user's description and visible image evidence, without inventing facts.)

2. APPLICABLE RULE
(State the specific MCC Law and ICC DRS criteria that apply.)

3. WHY THE UMPIRE MAY HAVE MADE THIS DECISION
(Provide the on-field/TV umpire perspective, line of sight, or protocol considerations.)

4. WHAT EVIDENCE SHOULD BE CHECKED
(List specific replay angles, camera frames, ball-tracking/Hawk-Eye/UltraEdge, Zing bails dislodgment, or popping crease grounding markers to inspect.)

5. AI ASSESSMENT
(Must strictly be one of: "Appears correct", "Appears incorrect", or "Inconclusive" followed by a 1-sentence rationale.)

CRITICAL GUIDELINES:
- State the direct call immediately in the DIRECT DECISION and DECISION SUMMARY lines.
- Do not invent match facts not provided in the description or visible image.
- Clearly distinguish fan-provided claims from verified objective rules.
- If the description and image lack crucial angles or details, set AI ASSESSMENT to Inconclusive.
- Do not claim to be an official ICC or MCC authority.
- Keep the language engaging, clear, and concise.
"""
        raw_text, successful_model, vision_err = call_gemini_vision_rest(raw_image_bytes, image_mime_type, prompt, active_key)
        if raw_text:
            sections, parsed_decision, parsed_summary, detected_sport, detected_incident = parse_explanation_sections(raw_text)

            final_sport = sport or (detected_sport.lower() if detected_sport else sport_name.lower())
            final_incident = incident
            if detected_incident:
                norm_inc, norm_sport = classify_incident(detected_incident, sport=final_sport)
                if norm_inc:
                    final_incident = norm_inc
                    if norm_sport:
                        final_sport = norm_sport
            elif detected_sport and not sport:
                final_sport = detected_sport.lower()

            final_decision = parsed_decision or direct_decision
            final_summary = parsed_summary or decision_summary
            engine_used = f"Gemini Multimodal Vision ({successful_model})"
            return raw_text, sections, sections["assessment"], final_decision, final_summary, final_sport, final_incident, engine_used, None

        if vision_err:
            warning_notice = f"Gemini Vision notice: {vision_err}. Used local fallback engine."

    # Dynamic contextual synthesis tailored to the user's specific scenario, inquiry, and visual frame
    raw_exp, sec, assess, dec, summ = synthesize_dynamic_explanation(
        incident=incident,
        description=description,
        sport=sport_name.lower(),
        visual_info=visual_info,
        has_image=bool(raw_image_bytes)
    )
    engine_used = "Local Heuristic Engine (Offline Fallback)"
    return raw_exp, sec, assess, dec, summ, sport_name.lower(), incident, engine_used, warning_notice
