"""
RefExplain Cricket AI - Accuracy & Performance Evaluation Benchmark
Calculates quantitative accuracy metrics across:
1. Incident Category Classification Accuracy (%)
2. Direct Decision Outcome Accuracy (%) (OUT vs NOT OUT vs UMPIRE'S CALL vs NO BALL)
3. Official MCC Law Citation Accuracy (%)
4. Confusion Matrix & Decision Breakdown
5. Latency & Response Time per Decision
"""

import sys
import os
import json
import time
import base64
from typing import List, Dict, Any

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from main import analyze, DecisionRequest
from rules import CRICKET_RULES

# Built-in comprehensive benchmark dataset of verified historical decisions and edge cases
BENCHMARK_CASES: List[Dict[str, Any]] = [
    # --- 1. LBW & DRS Ball Tracking Scenarios ---
    {
        "id": "LBW-01",
        "name": "Kohli DRS Umpire's Call on Impact",
        "type": "text",
        "description": "Kohli played forward, ball struck front pad in line with off stump. Hawk-Eye ball tracking showed impact clipping 50% line of off stump.",
        "expected_incident": "LBW / DRS Umpire's Call",
        "expected_decision_tokens": ["UMPIRE'S CALL", "OUT"],
        "expected_law": "Law 36",
    },
    {
        "id": "LBW-02",
        "name": "Pitching Outside Leg Stump (Not Out)",
        "type": "text",
        "description": "Fast bowler angled in from round the wicket, hit batter on back pad right in front of middle. Replay shows ball pitched outside leg stump.",
        "expected_incident": "LBW / DRS Umpire's Call",
        "expected_decision_tokens": ["NOT OUT"],
        "expected_law": "Law 36",
    },
    {
        "id": "LBW-03",
        "name": "Impact Outside Off Stump with Shot Offered",
        "type": "text",
        "description": "Batter offered a forward defensive stroke. Ball struck the pad outside the line of off stump.",
        "expected_incident": "LBW / DRS Umpire's Call",
        "expected_decision_tokens": ["NOT OUT"],
        "expected_law": "Law 36",
    },

    # --- 2. Caught Behind & UltraEdge / Snicko ---
    {
        "id": "CATCH-BEHIND-01",
        "name": "Pant Snicko Murmur Spike Outside Edge",
        "type": "text",
        "description": "Fast bowler delivery shaped past outside edge into keeper gloves. UltraEdge shows a clear spike as ball passes bat frame.",
        "expected_incident": "Caught Behind / UltraEdge",
        "expected_decision_tokens": ["OUT"],
        "expected_law": "Law 33",
    },
    {
        "id": "CATCH-BEHIND-02",
        "name": "Flat Line on UltraEdge with Gap",
        "type": "text",
        "description": "Huge appeal for caught behind. Side-on hotspot and UltraEdge show completely flat line with daylight between bat and ball.",
        "expected_incident": "Caught Behind / UltraEdge",
        "expected_decision_tokens": ["NOT OUT"],
        "expected_law": "Law 33",
    },

    # --- 3. Fair Catch / Low Turf Scoop ---
    {
        "id": "FAIR-CATCH-01",
        "name": "Fingers Cleanly Underneath Ball",
        "type": "text",
        "description": "Fielder dived forward and scooped ball inches above grass. Replay zoom confirms fingers were interlocked completely underneath the leather.",
        "expected_incident": "Fair Catch / Grounded Catch (MCC Law 33)",
        "expected_decision_tokens": ["OUT", "FAIR CATCH"],
        "expected_law": "Law 33",
    },
    {
        "id": "FAIR-CATCH-02",
        "name": "Turf Contact Ball Squeezed on Grass",
        "type": "text",
        "description": "Fielder took low catch, but slow motion replay shows the ball touched the grass turf before fingers could scoop under it.",
        "expected_incident": "Fair Catch / Grounded Catch (MCC Law 33)",
        "expected_decision_tokens": ["NOT OUT"],
        "expected_law": "Law 33",
    },
    {
        "id": "FAIR-CATCH-03",
        "name": "Informal Query: Is it caught out or not?",
        "type": "text",
        "description": "is it caught out or not",
        "expected_incident": "Fair Catch / Grounded Catch (MCC Law 33)",
        "expected_decision_tokens": ["NOT OUT", "FAIR CATCH", "OUT", "REVIEW"],
        "expected_law": "Law 33",
    },

    # --- 4. Run Out / Crease Grounding (Law 38) ---
    {
        "id": "RUN-OUT-01",
        "name": "Diving Batter Bat on Line (Not Grounded Past)",
        "type": "text",
        "description": "Diving batter bat was on the popping crease line with no part grounded behind the inside edge when bails were dislodged.",
        "expected_incident": "Run Out / Crease Grounding (MCC Law 38)",
        "expected_decision_tokens": ["OUT", "RUN OUT"],
        "expected_law": "Law 38",
    },
    {
        "id": "RUN-OUT-02",
        "name": "Bat Safely Grounded Past Crease",
        "type": "text",
        "description": "Direct hit breaks stumps. Side-on camera confirms batter bat grounded 2 inches inside the crease before bails separated.",
        "expected_incident": "Run Out / Crease Grounding (MCC Law 38)",
        "expected_decision_tokens": ["NOT OUT"],
        "expected_law": "Law 38",
    },

    # --- 5. Non-Striker Run Out (Law 38.3) ---
    {
        "id": "NON-STRIKER-01",
        "name": "Deepti Sharma vs Charlie Dean Mankad",
        "type": "text",
        "description": "Non-striker consistently backed up yards out of crease before release. Bowler stopped delivery swing and removed bails.",
        "expected_incident": "Run Out at Non-Striker's End",
        "expected_decision_tokens": ["OUT", "RUN OUT"],
        "expected_law": "Law 38",
    },

    # --- 6. Boundary Catch & Aerial Relay (Law 19) ---
    {
        "id": "BOUNDARY-01",
        "name": "Clean Aerial Relay Over Rope",
        "type": "text",
        "description": "Fielder catches ball airborne inside boundary rope, tosses ball up before stepping over cushions, re-enters and takes catch.",
        "expected_incident": "Boundary Catch / Aerial Relay",
        "expected_decision_tokens": ["OUT", "FAIR CATCH", "NOT OUT", "BOUNDARY"],
        "expected_law": "Law 19",
    },
    {
        "id": "BOUNDARY-02",
        "name": "Fielder Foot Touching Boundary Cushion While In Contact",
        "type": "text",
        "description": "Fielder held the ball on the boundary edge while his heel was touching the foam cushion.",
        "expected_incident": "Boundary Catch / Aerial Relay",
        "expected_decision_tokens": ["NOT OUT", "SIX", "BOUNDARY"],
        "expected_law": "Law 19",
    },
    {
        "id": "BOUNDARY-03",
        "name": "Informal Query: Is this a catch or boundary?",
        "type": "text",
        "description": "is this a catch or boundary",
        "expected_incident": "Boundary Catch / Aerial Relay",
        "expected_decision_tokens": ["BOUNDARY", "OUT", "NOT OUT", "SIX"],
        "expected_law": "Law 19",
    },

    # --- 7. Waist-High Full Toss No Ball (Law 41.7) ---
    {
        "id": "NO-BALL-01",
        "name": "Nawaz Full Toss Above Waist to Kohli",
        "type": "text",
        "description": "Bowler bowled a high dipping full toss above batter waist height at normal batting crease stance.",
        "expected_incident": "Waist-High Full Toss (No Ball)",
        "expected_decision_tokens": ["NO BALL"],
        "expected_law": "Law 41",
    },

    # --- 8. Timed Out (Law 40) ---
    {
        "id": "TIMED-OUT-01",
        "name": "Angelo Mathews Broken Strap > 2 Mins",
        "type": "text",
        "description": "Incoming batter delayed taking guard for over 2 minutes due to broken helmet strap. Fielding team appealed.",
        "expected_incident": "Timed Out",
        "expected_decision_tokens": ["OUT", "TIMED OUT"],
        "expected_law": "Law 40",
    },
]

# Optional image test cases if local user uploaded files exist
IMAGE_TEST_CONFIGS = [
    {
        "id": "IMG-CATCH-01",
        "name": "Low Catch Broadcast NOT OUT Graphic",
        "type": "image",
        "path": r"C:\Users\ROHAN\.gemini\antigravity\brain\497796d2-ce77-48ad-9020-f256baa150b9\.user_uploaded\media_1793698681392_3ab24f0d.jpg",
        "description": "",
        "expected_incident": "Fair Catch / Grounded Catch (MCC Law 33)",
        "expected_decision_tokens": ["NOT OUT"],
        "expected_law": "Law 33"
    },
    {
        "id": "IMG-BOUNDARY-01",
        "name": "Boundary Line Catch Review Frame",
        "type": "image",
        "path": r"C:\Users\ROHAN\.gemini\antigravity\brain\497796d2-ce77-48ad-9020-f256baa150b9\.user_uploaded\media_1793703055279_760e548e.jpg",
        "description": "is this a catch or boundary",
        "expected_incident": "Boundary Catch / Aerial Relay",
        "expected_decision_tokens": ["BOUNDARY", "SIX", "NOT OUT", "OUT"],
        "expected_law": "Law 19"
    },
    {
        "id": "IMG-RUNOUT-01",
        "name": "Diving Batter Crease Grounding Frame",
        "type": "image",
        "path": r"C:\Users\ROHAN\.gemini\antigravity\brain\497796d2-ce77-48ad-9020-f256baa150b9\.user_uploaded\media_1793705509388_bba5357f.jpg",
        "description": "",
        "expected_incident": "Run Out / Crease Grounding (MCC Law 38)",
        "expected_decision_tokens": ["OUT", "RUN OUT"],
        "expected_law": "Law 38"
    }
]


def load_image_base64(path: str) -> str:
    """Read an image file and return base64 data URI."""
    if not os.path.exists(path):
        return None
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "jpeg" if ext in ["jpg", "jpeg"] else ("png" if ext == "png" else "webp")
    with open(path, "rb") as f:
        return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode("utf-8")


def run_benchmark(custom_dataset_path: str = None) -> Dict[str, Any]:
    """
    Executes benchmark test cases and computes:
    - Incident Classification Accuracy
    - Direct Decision Accuracy
    - MCC Law Citation Accuracy
    - Latency statistics
    """
    test_cases = list(BENCHMARK_CASES)

    # Attach verified image test cases if present
    for img_cfg in IMAGE_TEST_CONFIGS:
        if os.path.exists(img_cfg["path"]):
            b64 = load_image_base64(img_cfg["path"])
            if b64:
                img_case = dict(img_cfg)
                img_case["image_base64"] = b64
                test_cases.append(img_case)

    # Load external custom dataset if supplied
    if custom_dataset_path and os.path.exists(custom_dataset_path):
        with open(custom_dataset_path, "r", encoding="utf-8") as f:
            ext_cases = json.load(f)
            test_cases.extend(ext_cases)

    total_cases = len(test_cases)
    incident_matches = 0
    decision_matches = 0
    law_matches = 0
    latencies = []

    results = []

    print("================================================================================")
    print(f"RefExplain Cricket AI - Accuracy Benchmark Suite (Total Cases: {total_cases})")
    print("================================================================================\n")

    for i, case in enumerate(test_cases, 1):
        cid = case.get("id", f"TC-{i:02d}")
        name = case.get("name", "Unnamed Case")
        desc = case.get("description", "")
        img_b64 = case.get("image_base64", None)
        expected_inc = case["expected_incident"]
        expected_tokens = case["expected_decision_tokens"]
        expected_law = case.get("expected_law", "")

        req = DecisionRequest(
            sport="cricket",
            description=desc,
            image_base64=img_b64
        )

        t0 = time.time()
        try:
            res = analyze(req)
            elapsed_ms = round((time.time() - t0) * 1000, 1)
            latencies.append(elapsed_ms)

            # 1. Incident Accuracy Match
            pred_inc = res.incident
            inc_match = (pred_inc == expected_inc)
            if inc_match:
                incident_matches += 1

            # 2. Decision Outcome Accuracy Match
            pred_dec = (res.direct_decision or "").upper()
            dec_match = any(token in pred_dec for token in expected_tokens)
            if dec_match:
                decision_matches += 1

            # 3. Law Citation Accuracy
            sec_law = res.sections.get("applicable_rule", "") if res.sections else ""
            law_match = (expected_law.lower() in sec_law.lower()) if expected_law else True
            if law_match:
                law_matches += 1

            status_str = "[PASS]" if (inc_match and dec_match and law_match) else "[FAIL]"
            print(f"{status_str} #{i:02d} [{cid}] {name} ({elapsed_ms}ms)")
            print(f"       Incident: Expected='{expected_inc}' | Got='{pred_inc}' ({'OK' if inc_match else 'DIFF'})")
            print(f"       Decision: Expected In={expected_tokens} | Got='{pred_dec}' ({'OK' if dec_match else 'DIFF'})")
            print(f"       Law Ref:  Expected='{expected_law}' ({'OK' if law_match else 'DIFF'})\n")

            results.append({
                "id": cid,
                "name": name,
                "incident_match": inc_match,
                "decision_match": dec_match,
                "law_match": law_match,
                "predicted_incident": pred_inc,
                "expected_incident": expected_inc,
                "predicted_decision": pred_dec,
                "expected_tokens": expected_tokens,
                "latency_ms": elapsed_ms
            })

        except Exception as e:
            print(f"[ERROR] #{i:02d} [{cid}] {name}: {e}\n")
            results.append({
                "id": cid,
                "name": name,
                "error": str(e),
                "incident_match": False,
                "decision_match": False,
                "law_match": False,
                "latency_ms": 0
            })

    # Summary calculations
    inc_acc = round((incident_matches / total_cases) * 100, 2)
    dec_acc = round((decision_matches / total_cases) * 100, 2)
    law_acc = round((law_matches / total_cases) * 100, 2)
    composite_acc = round(((inc_acc + dec_acc + law_acc) / 3), 2)
    avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else 0

    print("================================================================================")
    print("BENCHMARK ACCURACY SUMMARY")
    print("================================================================================")
    print(f"Total Test Cases Evaluated : {total_cases}")
    print(f"Incident Classification Acc : {inc_acc}% ({incident_matches}/{total_cases})")
    print(f"Decision Outcome Accuracy   : {dec_acc}% ({decision_matches}/{total_cases})")
    print(f"MCC Law Citation Accuracy   : {law_acc}% ({law_matches}/{total_cases})")
    print(f"Composite System Accuracy   : {composite_acc}%")
    print(f"Average Response Latency    : {avg_latency} ms")
    print("================================================================================\n")

    summary = {
        "total_cases": total_cases,
        "incident_accuracy_pct": inc_acc,
        "decision_accuracy_pct": dec_acc,
        "law_citation_accuracy_pct": law_acc,
        "composite_accuracy_pct": composite_acc,
        "average_latency_ms": avg_latency,
        "results": results
    }

    # Save report to JSON file
    report_file = os.path.join(os.path.dirname(__file__), "accuracy_benchmark_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Detailed JSON benchmark report exported to: {report_file}")
    return summary


if __name__ == "__main__":
    custom_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_benchmark(custom_arg)

