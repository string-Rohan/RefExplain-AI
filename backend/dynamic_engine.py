"""
RefExplain AI - Dynamic Incident Explanation Synthesizer
Generates contextual, situation-specific, and non-static explanations
tailored to the user's specific match scenario, questions, and visual frame evidence.
"""

from typing import Dict, Any, Optional, Tuple


def synthesize_dynamic_explanation(
    incident: str,
    description: str,
    sport: str,
    visual_info: Optional[Dict[str, Any]] = None,
    has_image: bool = False
) -> Tuple[str, Dict[str, str], str, str, str]:
    """
    Dynamically generates a 5-section legal analysis, direct decision, and summary
    tailored to the specific scenario details, questions, and visual markers.
    Returns: (raw_text, sections_dict, assessment, direct_decision, decision_summary)
    """
    user_text = description.strip() if description else ""
    text_lower = user_text.lower()
    decision_maker = "Umpire"
    authority = "MCC Laws of Cricket & ICC Standard Playing Conditions"

    # Detect user intent: Is it an open question, dispute claim, or factual recap?
    is_question = any(q in text_lower for q in ["is it", "is this", "or not", "or", "?", "whether", "was it", "should it"])

    # Extract visual notes
    visual_evidence_note = ""
    if visual_info and visual_info.get("evidence_detected"):
        visual_evidence_note = f"\n[Visual Evidence Detected: {visual_info['evidence_detected']}]"
    elif has_image:
        visual_evidence_note = "\n[Visual Evidence Detected: Match broadcast screenshot inspected for positioning and contact points]"

    sections = {}
    direct_decision = "REVIEW"
    decision_summary = "Match incident evaluated against official rules."
    assessment = "Inconclusive"

    # =========================================================================
    # 1. BOUNDARY CATCH / AERIAL RELAY (MCC Law 19 & Law 33.2)
    # =========================================================================
    if incident == "Boundary Catch / Aerial Relay":
        touches_rope = any(w in text_lower for w in ["touched", "brush", "brushed", "touch", "stepped", "hit the rope", "on the rope", "foot on rope", "rope contact", "cushion"])
        is_aerial = any(w in text_lower for w in ["aerial", "relay", "jumped", "tossed", "flicked", "threw", "airborne"])

        if touches_rope and not is_question:
            direct_decision = "SIX / BOUNDARY (NOT OUT)"
            decision_summary = "Fielder made contact with the boundary cushion/rope while holding the ball; scored as a Boundary (Six) under MCC Law 19.5."
            assessment = "Appears correct"
            what_happened = (
                f"A fielder completed a catch in the deep near the boundary perimeter, but according to the match situation "
                f"(\"{user_text}\"), the fielder's foot, shoe, or body made contact with the boundary cushion or rope while holding the ball."
            )
            assessment_text = (
                "Appears correct - Boundary Awarded (Six/Four)\n"
                "Under MCC Law 19.5.1, any contact between a fielder and the boundary cushion while holding the ball constitutes "
                "being grounded beyond the boundary. The ball becomes immediately Dead and is scored as a Boundary (Six if caught on the full)."
            )
        elif is_aerial:
            direct_decision = "OUT CAUGHT (AIRBORNE RELAY)"
            decision_summary = "Fielder legally released the ball airborne before touching the cushion and re-grounded inside before completing the catch."
            assessment = "Appears correct"
            what_happened = (
                f"A boundary rider intercepted a lofted shot near the boundary rope (\"{user_text}\"). "
                f"The fielder popped the ball airborne into the field of play before momentum carried them over the rope, "
                f"then re-established grounding inside before completing the catch."
            )
            assessment_text = (
                "Appears correct - Fair Catch via Aerial Relay\n"
                "Under MCC Law 19.5.2 & Law 33.2, an airborne fielder who previously landed outside the rope is permitted to catch "
                "the ball provided they release the ball before crossing the boundary and re-ground themselves completely inside "
                "the field of play before touching the ball again."
            )
        else:
            direct_decision = "BOUNDARY REVIEW (MCC LAW 19)"
            decision_summary = (
                "Boundary review: If the fielder touched the boundary cushion/rope while holding the ball it is a SIX; "
                "if clean daylight separated the foot from the rope it is OUT CAUGHT."
            )
            assessment = "Inconclusive"
            what_happened = (
                f"The incident review asks to evaluate whether a fielding effort on the boundary (\"{user_text}\") "
                f"resulted in a fair catch or a boundary (Six/Four). The fielder attempted to pouch the ball while momentum "
                f"carried them towards the boundary cushion."
            )
            assessment_text = (
                "Inconclusive - Decision Hinges on Boundary Sponge Contact\n"
                "If broadcast replays show the fielder's boot or clothing brushed or depressed the boundary cushion before "
                "releasing the ball, it is a SIX; if clean daylight separated the boot from the cushion throughout the catch, "
                "it is OUT CAUGHT under MCC Law 19."
            )

        applicable_rule = (
            "MCC Law 19 (Boundaries) & Law 33.2 (Fair Catch):\n"
            "1. Law 19.5 (Fielder Grounded Beyond Boundary): A fielder is deemed grounded beyond the boundary if any part of "
            "their person or clothing touches the boundary cushion, rope, or ground beyond while in contact with the ball. "
            "Contact with the boundary while holding the ball immediately renders the ball Dead and awards a boundary.\n"
            "2. Law 33.2 (Fair Catch Criteria): To be Out Caught, the fielder must not touch the boundary while in contact "
            "with the ball, and must obtain complete control over both the ball and their own movement."
        )

        why_decision = (
            "The TV third umpire inspects synchronized super-slow-motion and ground-level boundary cameras (often 500 fps) "
            "focusing on the exact seam between the green turf and the boundary foam cushion. The umpire looks for two critical "
            "micro-moments: (a) the exact frame the ball first contacts the fielder's hands, and (b) whether any part of the shoe "
            "or clothing depresses the boundary sponge or moves the advertising cushion while the ball is still held. Any deflection "
            "or compression of the boundary rope sponge while the ball is held triggers an immediate Boundary ruling."
        )

        evidence_to_check = (
            "- Ground-level boundary camera aligned directly down the cushion line (looking for clear daylight between shoe and sponge).\n"
            "- Cushion deflection: Did the advertising foam sponge vibrate, depress, or shift when the fielder landed?\n"
            "- Ball release frame: Did the fielder release the ball into the air before their shoe or knee touched the rope?\n"
            "- Re-grounding frame: Did both feet plant back inside the field of play before touching the ball the second time?"
        )

    # =========================================================================
    # 2. FAIR CATCH / GROUNDED CATCH (MCC Law 33 & Law 33.2)
    # =========================================================================
    elif incident == "Fair Catch / Grounded Catch (MCC Law 33)":
        touches_grass = any(w in text_lower for w in ["grass", "turf", "ground", "grounded", "bounced", "grass blades", "spilled", "dropped"])
        fingers_under = any(w in text_lower for w in ["fingers under", "fingers underneath", "under the ball", "clean catch", "cupped"])
        has_not_out_graphic = visual_info and visual_info.get("direct_decision") == "NOT OUT"

        if touches_grass or has_not_out_graphic:
            direct_decision = "NOT OUT"
            decision_summary = "Video replays confirm the ball contacted the grass blades before complete control was established; NOT OUT under MCC Law 33.2."
            assessment = "Appears correct"
            what_happened = (
                f"A fielder dived forward attempting a low scoop catch close to the grass surface (\"{user_text}\"). "
                f"The third umpire evaluated whether the ball touched the pitch surface or grass blades before the fielder had full control."
            )
            assessment_text = (
                "Appears correct - Not Out (Turf Contact Confirmed)\n"
                "Under MCC Law 33.2, if the ball touches the turf or grass blades before the fielder obtains complete control "
                "over both the ball and their own movement, the catch is not fair and the batter is NOT OUT."
            )
        elif fingers_under:
            direct_decision = "OUT CAUGHT"
            decision_summary = "Fielder's fingers were completely cupped underneath the ball cushioning it from grass contact; Out under MCC Law 33."
            assessment = "Appears correct"
            what_happened = (
                f"A low scoop catch was taken near the turf (\"{user_text}\"). "
                f"Replays inspect whether the fielder's fingers remained cleanly cupped underneath the ball preventing turf contact."
            )
            assessment_text = (
                "Appears correct - Out Caught (Fingers Cleanly Underneath)\n"
                "Under MCC Law 33.2, if the fielder's fingers are completely under the ball, cushioning it and preventing the leather "
                "from touching the grass blades, the catch is legally completed."
            )
        else:
            direct_decision = "CATCH REVIEW"
            decision_summary = "Third umpire low catch review: evaluating whether fingers were cupped underneath or if ball touched grass blades."
            assessment = "Inconclusive"
            what_happened = (
                f"An on-field catch was referred upstairs to inspect a low scoop catch inches above the ground (\"{user_text}\"). "
                f"The TV umpire reviewed synchronized zoom angles of the fielder's hands sliding along the turf."
            )
            assessment_text = (
                "Inconclusive - Requires Conclusive Zoom Angle\n"
                "In low catch reviews, if super-slow-motion angles do not conclusively prove the fingers were completely underneath "
                "the ball cushioning it from the turf, the benefit of the doubt must remain with the batter (Not Out)."
            )

        applicable_rule = (
            "MCC Law 33 (Caught) & Law 33.2 (Fair Catch / Ball Grounding Protocols):\n"
            "A striker is out Caught only if the ball is caught fairly before touching the ground. If the ball touches the turf or grass "
            "blades while sliding before the fielder obtains complete control over both the ball and their own movement, it is NOT a fair "
            "catch and the batter is NOT OUT. Fingers must be completely underneath the ball cushioning it from the ground."
        )

        why_decision = (
            "The TV third umpire reviewed multiple synchronized super-slow-motion and zoom replays (front-on and reverse angles). "
            "Because foreshortening on 2D cameras can make fingers appear under the ball when they are split apart, the umpire checks "
            "for grass blade deflection or ball deformation against the ground before delivering the verdict."
        )

        evidence_to_check = (
            "- Ultra-slow-motion zoom frames at the lowest point of the scoop.\n"
            "- Finger positioning: Were the fingers cup-shaped underneath the ball or split open on the turf?\n"
            "- Grass blade deflection: Did blades of grass bend or trap directly under the ball's leather?\n"
            "- Ball wobble: Did the ball dislodge or roll when the fielder's wrists impacted the ground?"
        )

    # =========================================================================
    # 3. LBW / DRS UMPIRE'S CALL (MCC Law 36)
    # =========================================================================
    elif incident == "LBW / DRS Umpire's Call":
        pitched_outside_leg = "outside leg" in text_lower
        bat_first = any(w in text_lower for w in ["bat first", "inside edge", "edged onto pad", "wood"])
        impact_outside_off = ("outside off" in text_lower or ("outside" in text_lower and "off stump" in text_lower)) and any(w in text_lower for w in ["shot", "stroke", "played", "forward", "offered"])
        missing_wickets = any(w in text_lower for w in ["missing wickets", "missing off", "missing leg", "going over", "bouncing over", "over the stumps"])

        if pitched_outside_leg:
            direct_decision = "NOT OUT (PITCHED OUTSIDE LEG)"
            decision_summary = "Ball pitched outside leg stump line; automatically Not Out under MCC Law 36.1."
            assessment = "Appears correct"
        elif bat_first:
            direct_decision = "NOT OUT (BAT CONTACT FIRST)"
            decision_summary = "UltraEdge confirmed contact with bat blade prior to pad impact; Not Out under MCC Law 36."
            assessment = "Appears correct"
        elif impact_outside_off:
            direct_decision = "NOT OUT (IMPACT OUTSIDE OFF)"
            decision_summary = "Hawk-Eye impact point was outside off stump line with genuine shot offered; Not Out under MCC Law 36.1."
            assessment = "Appears correct"
        elif missing_wickets:
            direct_decision = "NOT OUT (PROJECTED TO MISS STUMPS)"
            decision_summary = "Hawk-Eye projected path shows ball bouncing over or missing stumps; Not Out under MCC Law 36."
            assessment = "Appears correct"
        else:
            direct_decision = "DRS UMPIRE'S CALL"
            decision_summary = "Ball tracking showed impact or wickets clipping within the 50% Umpire's Call tolerance corridor; on-field decision stands."
            assessment = "Inconclusive"

        what_happened = (
            f"The bowling team appealed for an LBW dismissal (\"{user_text}\"). "
            f"A DRS review was initiated to inspect the delivery's pitching location, pad impact alignment, and projected path towards the stumps."
        )
        applicable_rule = (
            "MCC Law 36 (Leg Before Wicket) & ICC DRS Appendix D:\n"
            "1. Pitching: Ball must pitch in line with the stumps or outside off stump (a delivery pitching outside leg is automatically Not Out).\n"
            "2. Impact: If a stroke is offered, impact must be in line with the stumps. At least 50% of the ball must be inside the impact corridor to overturn.\n"
            "3. Wickets: Ball-tracking projection must show at least 50% of the ball hitting the stumps (or bails) to overturn an on-field Not Out."
        )
        why_decision = (
            "The on-field umpire judged the delivery based on real-time trajectory, bounce height, and lateral deviation off the pitch. "
            "When DRS tracking indicates marginal contact (less than 50% of the ball hitting the stump frame), the protocol defers to "
            "the original on-field decision as 'Umpire's Call'."
        )
        evidence_to_check = (
            "- UltraEdge synchronized waveform to rule out any bat contact before pad impact.\n"
            "- Pitch mat Hawk-Eye graphic to verify ball pitched in line or outside off stump.\n"
            "- Hawk-Eye point of impact relative to off stump and leg stump lines.\n"
            "- Virtual ball-tracking projection at the stumps (height and outer stump edge)."
        )
        assessment_text = (
            f"{assessment} - {decision_summary}\n"
            "Under the ICC DRS protocol, virtual ball-tracking margins below 50% ball volume uphold the on-field umpire's judgment."
        )

    # =========================================================================
    # 3B. RUN OUT / CREASE GROUNDING (MCC Law 38)
    # =========================================================================
    elif incident == "Run Out / Crease Grounding (MCC Law 38)":
        bat_in_crease = any(w in text_lower for w in ["bat grounded", "inside crease", "bat crossed", "in his ground", "in her ground", "safely home", "not out"])
        bat_short = any(w in text_lower for w in ["short of crease", "out of crease", "bat in air", "on the line", "out of ground", "bails dislodged before"])

        if bat_in_crease:
            direct_decision = "NOT OUT (BAT GROUNDED IN CREASE)"
            decision_summary = "Replays confirm the batter grounded their bat behind the popping crease before the bails were dislodged."
            assessment = "Appears correct"
            assessment_text = (
                "Appears correct - Not Out (Grounded Behind Crease)\n"
                "Under MCC Law 38 and Law 30, the batter is in their ground if any part of their bat in hand or person is grounded "
                "behind the inside edge of the popping crease when the wicket is broken."
            )
        elif bat_short:
            direct_decision = "OUT RUN OUT"
            decision_summary = "The batter failed to ground any part of their person or bat behind the popping crease before the bails were removed."
            assessment = "Appears correct"
            assessment_text = (
                "Appears correct - Out Run Out\n"
                "Under MCC Law 38, the batter was out of their ground when the bails were legally separated from the stumps."
            )
        else:
            direct_decision = "RUN OUT REVIEW (MCC LAW 38)"
            decision_summary = (
                "TV umpire run-out review: camera inspects whether any part of the bat or person was grounded "
                "behind the popping crease at the frame the bails were dislodged."
            )
            assessment = "Inconclusive"
            assessment_text = (
                "Inconclusive - Decision Hinges on Frame-by-Frame Crease Grounding\n"
                "The decision depends on the exact synchronized frame where the bails separate (or Zing LED lights flash): "
                "if the bat tip is grounded behind the crease line at that frame, it is NOT OUT; if the bat is on the line or in the air, it is OUT."
            )

        what_happened = (
            f"A run-out appeal occurred at the wickets (\"{user_text}\"). "
            f"A running batter dived or stretched with their bat extended towards the popping crease while the fielder or wicketkeeper dislodged the bails."
        )
        applicable_rule = (
            "MCC Law 38 (Run Out) & Law 30 (Batter out of their ground):\n"
            "1. Law 38.1: A batter is out Run Out if, while the ball is in play, they are out of their ground and their wicket is fairly broken by a fielder.\n"
            "2. Law 30.1: A batter is in their ground only if some part of their person or bat in hand is grounded behind the inside edge of the popping crease. "
            "The line itself belongs to the fielding side (bat on the line is NOT in ground).\n"
            "3. Law 30.1.2 (Bat Bouncing Exemption): If a running batter grounds their bat behind the crease and subsequent forward momentum causes the bat "
            "to bounce up into the air while the bails are broken, the batter is deemed NOT OUT."
        )
        why_decision = (
            "The TV third umpire inspects side-on super-slow-motion cameras. The umpire first rocks the replay back and forth to pinpoint "
            "the exact first frame where the bail spigot separates from the stump groove (or the Zing LED illuminates). The umpire then pans to "
            "the popping crease line to check if the bat's blade has touched down behind the white crease marking."
        )
        evidence_to_check = (
            "- Side-on run-out camera aligned with the popping crease line.\n"
            "- Exact frame of bail spigot separation / first Zing light illumination.\n"
            "- Bat tip grounding: Is there green grass visible between the bat tip and the crease line?\n"
            "- Bat bounce check: Did the bat previously ground behind the crease line before lifting up?"
        )

    # =========================================================================
    # 4. CAUGHT BEHIND / ULTRAEDGE (MCC Law 33)
    # =========================================================================
    elif incident == "Caught Behind / UltraEdge":
        has_spike = any(w in text_lower for w in ["spike", "snick", "murmur", "edge", "nicked", "feathered"])
        flatline = any(w in text_lower for w in ["flatline", "no spike", "gap", "missed", "daylight"])

        if flatline:
            direct_decision = "NOT OUT (FLATLINE ON ULTRAEDGE)"
            decision_summary = "UltraEdge showed a complete flatline with daylight between bat and ball; Not Out under MCC Law 33."
            assessment = "Appears correct"
        elif has_spike:
            direct_decision = "OUT CAUGHT BEHIND"
            decision_summary = "Synchronized audio spike on UltraEdge confirmed edge off the bat blade before being caught."
            assessment = "Appears correct"
        else:
            direct_decision = "ULTRAEDGE REVIEW"
            decision_summary = "Third umpire inspecting UltraEdge acoustic waveform synchronized with the ball passing the bat blade."
            assessment = "Inconclusive"

        what_happened = (
            f"An appeal for a catch behind by the wicketkeeper or slips (\"{user_text}\") was referred for third umpire DRS review. "
            f"The review inspects whether the ball made acoustic contact with the bat blade before being gathered."
        )
        applicable_rule = (
            "MCC Law 33 (Caught) & ICC UltraEdge / RTS Protocol:\n"
            "The batter is Out Caught if a legitimately delivered ball touches the bat or the hand holding the bat (glove below wrist) "
            "and is caught cleanly before touching the turf. A distinct acoustic waveform spike exactly aligned with the ball passing "
            "the bat edge confirms contact."
        )
        why_decision = (
            "The umpire listens for sound deflections and inspects seam rotation changes. On review, UltraEdge waveforms are synchronized "
            "frame-by-frame with high-speed cameras to distinguish genuine ball-on-bat impact from ambient noise or bat clipping pad/turf."
        )
        evidence_to_check = (
            "- Real-Time Snickometer (RTS) waveform spike precisely synchronized with the ball passing the edge.\n"
            "- Frame gap between bat and ball to ensure bat did not hit the pad or the ground.\n"
            "- Split-screen zoom to verify keeper's gloves gathered the ball cleanly above the pitch."
        )
        assessment_text = f"{assessment} - {decision_summary}"

    # =========================================================================
    # 5. TIMED OUT (MCC Law 40)
    # =========================================================================
    elif incident == "Timed Out":
        direct_decision = "TIMED OUT"
        decision_summary = "Incoming batter exceeded the official time allowance before being ready to face delivery; dismissed under MCC Law 40."
        assessment = "Appears correct"
        what_happened = (
            f"An incoming batter faced delay upon arriving at the crease (\"{user_text}\"). "
            f"The fielding captain lodged an appeal for dismissal under the Timed Out regulation."
        )
        applicable_rule = (
            "MCC Law 40 & ICC World Cup Playing Conditions (Timed Out):\n"
            "The incoming batter must be in position to receive the ball or be at the wicket within 2 minutes of the previous fall of wicket. "
            "If an equipment issue is not pre-cleared with umpires, the fielding side's appeal must be upheld."
        )
        why_decision = (
            "Umpires cross-checked the official broadcast match clock and established that over 2 minutes elapsed without the batter being ready to take guard."
        )
        evidence_to_check = (
            "- Match timestamp from previous dismissal to batter taking guard.\n"
            "- Confirmation of the fielding captain's official appeal."
        )
        assessment_text = f"{assessment} - {decision_summary}"

    # =========================================================================
    # 9. RUN OUT AT NON-STRIKER'S END (MCC Law 38.3)
    # =========================================================================
    elif incident == "Run Out at Non-Striker's End":
        direct_decision = "OUT RUN OUT"
        decision_summary = "Non-striker left the crease before the bowler's expected delivery release point; legally out under MCC Law 38.3."
        assessment = "Appears correct"
        what_happened = (
            f"The bowler broke the wickets at the non-striker's end before releasing the ball (\"{user_text}\") "
            f"because the non-striker was backing up outside the popping crease."
        )
        applicable_rule = (
            "MCC Law 38.3 (Run Out of the Non-Striker):\n"
            "At any time from the moment the ball comes into play until the instant when the bowler would normally have been expected to release "
            "the ball, the bowler is permitted to run out the non-striker if they are out of their ground."
        )
        why_decision = (
            "The umpire verified on replay that the bowler had not completed their bowling arm swing past vertical when the bails were broken, "
            "and the non-striker had no part of their person or bat grounded behind the crease."
        )
        evidence_to_check = (
            "- Non-striker's position relative to popping crease line.\n"
            "- Bowler's arm angle at the exact moment the bails were removed."
        )
        assessment_text = f"{assessment} - {decision_summary}"

    # =========================================================================
    # 10. WAIST-HIGH FULL TOSS (MCC Law 41.7)
    # =========================================================================
    elif incident == "Waist-High Full Toss (No Ball)":
        direct_decision = "NO BALL"
        decision_summary = "Non-pitching delivery passed around or above the batter's upright standing waist height at the crease line."
        assessment = "Inconclusive"
        what_happened = (
            f"A fast or spin delivery did not pitch before reaching the batter (\"{user_text}\"), "
            f"prompting a review over whether it was an illegal dangerous waist-high full toss."
        )
        applicable_rule = (
            "MCC Law 41.7 (Dangerous and Unfair Non-Pitching Deliveries):\n"
            "Any ball that passes, or would have passed, on the full above the waist height of the striker standing upright at the popping crease is a No Ball."
        )
        why_decision = (
            "Umpires evaluate whether the ball was dipping or maintaining height, and project where it would have crossed the popping crease "
            "relative to the batter standing upright."
        )
        evidence_to_check = (
            "- Ball-tracking waist-height trajectory calculation at the popping crease line.\n"
            "- Pre-recorded upright waist measurement of the batter."
        )
        assessment_text = f"{assessment} - {decision_summary}"

    # =========================================================================
    # DEFAULT / OTHER CRICKET INCIDENTS
    # =========================================================================
    else:
        direct_decision = f"{incident.upper()} REVIEW"
        decision_summary = f"Incident evaluated against official {authority}."
        what_happened = (
            f"A disputed match situation occurred (\"{user_text}\"). "
            f"The incident was reviewed against official {authority} governing {incident}."
        )
        applicable_rule = f"Official regulations under {authority} governing {incident}."
        why_decision = f"The match official evaluated the on-field perspective and protocol guidelines for {incident}."
        evidence_to_check = "- Multi-angle broadcast replay footage.\n- High-speed visual freeze-frames and contact markers."
        assessment_text = f"{assessment} - {decision_summary}"

    sections["what_happened"] = what_happened
    sections["applicable_rule"] = applicable_rule
    sections["referee_reasoning"] = why_decision
    sections["evidence_to_check"] = evidence_to_check
    sections["assessment"] = assessment

    raw_text = (
        f"DIRECT DECISION: {direct_decision}\n"
        f"DECISION SUMMARY: {decision_summary}\n\n"
        f"1. WHAT HAPPENED\n{what_happened}\n\n"
        f"2. APPLICABLE RULE\n{applicable_rule}\n\n"
        f"3. WHY THE {decision_maker.upper()} MAY HAVE MADE THIS DECISION\n{why_decision}\n\n"
        f"4. WHAT EVIDENCE SHOULD BE CHECKED\n{evidence_to_check}\n\n"
        f"5. AI ASSESSMENT\n{assessment_text}"
        f"{visual_evidence_note}"
    )

    return raw_text, sections, assessment, direct_decision, decision_summary
