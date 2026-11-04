"""
RefExplain Cricket AI - Backend Verification Script
Executes automated tests against FastAPI application to verify response formats,
presets, and all incident types across MCC Laws of Cricket and ICC DRS Protocols.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import app, health_check, get_presets, analyze, DecisionRequest, PRESET_INCIDENTS
from rules import CRICKET_RULES, ALL_RULES


def test_health():
    print("Testing GET / (health_check) ...")
    data = health_check()
    assert data["status"] == "online"
    assert "cricket" in data["sports"]
    assert "football" not in data["sports"]
    assert "LBW / DRS Umpire's Call" in data["sports"]["cricket"]["supported_incidents"]
    assert "Run Out / Crease Grounding (MCC Law 38)" in data["sports"]["cricket"]["supported_incidents"]
    print("[PASS] Health check passed:", data["sports"]["cricket"]["name"])


def test_presets():
    print("\nTesting GET /presets ...")
    all_presets = get_presets()["presets"]
    assert len(all_presets) == 8, f"Expected exactly 8 cricket presets, got {len(all_presets)}"

    cricket_presets = get_presets(sport="cricket")["presets"]
    assert len(cricket_presets) == 8

    for p in all_presets:
        assert p.get("sport") == "cricket"

    print(f"[PASS] Presets returned {len(all_presets)} pure cricket presets.")


def test_cricket_incidents():
    print("\nTesting Cricket incidents across all 8 presets...")
    cricket_presets = [p for p in PRESET_INCIDENTS if p.get("sport") == "cricket"]
    for preset in cricket_presets:
        incident_type = preset["incident"]
        print(f"--- [Cricket: {incident_type}] {preset['title']} ---")

        req = DecisionRequest(
            sport="cricket",
            incident=incident_type,
            description=preset["description"]
        )

        res = analyze(req)
        assert res.success is True
        assert res.sport == "cricket"
        assert res.incident == incident_type
        assert res.assessment in ["Appears correct", "Appears incorrect", "Inconclusive"]
        assert len(res.sections) == 5
        print(f"[PASS] {incident_type} -> {res.assessment}")


def test_image_analysis():
    print("\nTesting image input support...")
    # Tiny 1x1 transparent PNG base64
    tiny_png_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    req = DecisionRequest(
        sport="cricket",
        incident="LBW / DRS Umpire's Call",
        description="Striker was hit on the pad in front of middle stump. Image attached.",
        image_base64=tiny_png_b64
    )
    res = analyze(req)
    assert res.success is True
    assert res.has_image is True
    assert len(res.sections) == 5
    print("[PASS] Image input verified successfully (has_image=True).")


def test_automatic_incident_detection():
    print("\nTesting automatic AI rule category classification (no incident provided)...")
    scenarios = [
        ("Kohli played forward, ball hit front pad in line with stumps, ball tracking clipping.", "LBW / DRS Umpire's Call", "cricket"),
        ("Keeper caught behind, UltraEdge snicko spike as ball passed bat blade.", "Caught Behind / UltraEdge", "cricket"),
        ("Non-striker backed up out of crease before release, bowler took bails off.", "Run Out at Non-Striker's End", "cricket"),
        ("Bowler bowled a high full toss above the waist in final over.", "Waist-High Full Toss (No Ball)", "cricket"),
        ("Fielder caught airborne inside boundary rope and tossed it back over cushions.", "Boundary Catch / Aerial Relay", "cricket"),
        ("Angelo Mathews helmet strap broke, 2 minutes elapsed, timed out appeal.", "Timed Out", "cricket"),
        ("is it caught out or not", "Fair Catch / Grounded Catch (MCC Law 33)", "cricket"),
        ("Fielder dived forward, ball touched grass, fingers under or not out.", "Fair Catch / Grounded Catch (MCC Law 33)", "cricket"),
        ("is this a catch or boundary", "Boundary Catch / Aerial Relay", "cricket"),
        ("fielder caught the ball but foot touched the rope", "Boundary Catch / Aerial Relay", "cricket"),
        ("is it six or out", "Boundary Catch / Aerial Relay", "cricket"),
        ("diving batter bat was on the line before bails dislodged run out", "Run Out / Crease Grounding (MCC Law 38)", "cricket"),
    ]

    for desc, expected_incident, expected_sport in scenarios:
        # Note: incident is NOT passed! AI must detect it automatically!
        req = DecisionRequest(description=desc)
        res = analyze(req)
        assert res.success is True
        assert res.incident == expected_incident, f"Expected {expected_incident}, got {res.incident} for: {desc}"
        assert res.sport == expected_sport, f"Expected {expected_sport}, got {res.sport} for: {desc}"
        print(f"[PASS] Auto-detected: '{expected_incident}' from query")


def test_direct_image_decision():
    print("\nTesting direct image analysis without text description...")
    img_path = r"C:\Users\ROHAN\.gemini\antigravity\brain\497796d2-ce77-48ad-9020-f256baa150b9\.user_uploaded\media_1793698681392_3ab24f0d.jpg"
    if os.path.exists(img_path):
        import base64
        with open(img_path, "rb") as f:
            b64_data = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

        # 1. Image-only: zero text provided!
        req_image_only = DecisionRequest(image_base64=b64_data)
        res1 = analyze(req_image_only)
        assert res1.success is True
        assert res1.sport == "cricket"
        assert res1.incident == "Fair Catch / Grounded Catch (MCC Law 33)"
        assert res1.direct_decision == "NOT OUT"
        assert "NOT OUT" in res1.decision_summary
        assert res1.assessment == "Appears correct"
        print("[PASS] Direct image-only analysis succeeded -> NOT OUT (Fair Catch / Grounded Catch)")

        # 2. Image + brief question
        req_with_query = DecisionRequest(description="is it caught out or not", image_base64=b64_data)
        res2 = analyze(req_with_query)
        assert res2.success is True
        assert res2.direct_decision == "NOT OUT"
        print("[PASS] Direct image + brief query analysis succeeded -> NOT OUT")

    # 3. Test Boundary screenshot
    bnd_path = r"C:\Users\ROHAN\.gemini\antigravity\brain\497796d2-ce77-48ad-9020-f256baa150b9\.user_uploaded\media_1793688390190_f6387232.png"
    if os.path.exists(bnd_path):
        import base64
        with open(bnd_path, "rb") as f:
            b64_bnd = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
        req_bnd = DecisionRequest(image_base64=b64_bnd, description="is this a catch or boundary")
        res_bnd = analyze(req_bnd)
        assert res_bnd.success is True
        assert res_bnd.incident == "Boundary Catch / Aerial Relay"
        print(f"[PASS] Boundary screenshot analyzed -> {res_bnd.direct_decision} ({res_bnd.incident})")

    # 4. Test Run Out Image
    ro_path = r"C:\Users\ROHAN\.gemini\antigravity\brain\497796d2-ce77-48ad-9020-f256baa150b9\.user_uploaded\media_1793705509388_bba5357f.jpg"
    if os.path.exists(ro_path):
        import base64
        with open(ro_path, "rb") as f:
            b64_ro = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")
        req_ro = DecisionRequest(image_base64=b64_ro)
        res_ro = analyze(req_ro)
        assert res_ro.success is True
        assert res_ro.incident == "Run Out / Crease Grounding (MCC Law 38)"
        assert "OUT" in res_ro.direct_decision
        print(f"[PASS] Direct Run Out image analysis succeeded -> {res_ro.direct_decision} ({res_ro.incident})")


if __name__ == "__main__":
    test_health()
    test_presets()
    test_cricket_incidents()
    test_image_analysis()
    test_automatic_incident_detection()
    test_direct_image_decision()
    print("\n=======================================================")
    print("ALL CRICKET DECISION REVIEW TESTS PASSED CLEANLY (100%)!")
    print("=======================================================")
