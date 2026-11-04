"""
RefExplain AI - Rules Database (Cricket Edition)
Official rules based on:
- MCC Laws of Cricket (Code 2017)
- ICC Standard Playing Conditions & DRS Protocols
"""

from typing import Tuple, Optional, Dict, Any, List

CRICKET_RULES = {
    "LBW / DRS Umpire's Call": """
    MCC Law 36 – Leg Before Wicket (LBW) & ICC DRS Appendix D.

    A batter is out LBW if all of the following conditions are met:
    1. No Ball Check: The delivery must be a fair ball (not a no-ball).
    2. Bat First: The ball must NOT have touched the bat or the hand holding the bat before hitting the striker's person/pad.
    3. Pitching: The ball must pitch either:
       - In line between wicket and wicket, OR
       - On the off side of the striker's wicket.
       *CRITICAL*: If the ball pitches outside the leg stump line, the batter CANNOT be out LBW, regardless of impact or trajectory.
    4. Impact:
       - If playing a genuine stroke / shot: The first impact with the person/pad must be in line between wicket and wicket.
       - If no genuine shot was offered: The impact can be in line OR outside the off stump.
    5. Wicket Hitting (Ball Tracking):
       - The ball's projected path must be hitting the wickets (stumps or bails).
    
    DRS Umpire's Call Protocols:
    - For Impact: At least 50% of the ball must be inside the impact corridor, or the on-field umpire's call stands.
    - For Wickets: At least 50% of the ball must strike the outer frame of the stumps (or base of bails), otherwise 'Umpire's Call' applies.
    """,

    "Fair Catch / Grounded Catch (MCC Law 33)": """
    MCC Law 33 – Caught & Law 33.2 (Fair Catch / Ball Grounding Protocols).

    1. Definition of Out Caught (Law 33.1):
    The striker is out Caught if a legitimately delivered ball touches the bat or the hand holding the bat (glove below the wrist) and is subsequently held as a fair catch by a fielder before touching the ground.

    2. Grounded Catch & Fingers Under the Ball (Law 33.2):
    - The fielder must obtain complete control over both the ball and their own movement.
    - If the ball touches the pitch or grass surface before the fielder has complete control, the catch is NOT fair and the batter is NOT OUT.
    - Fingers Under the Ball: If the fielder's fingers are completely underneath the ball, cushioning it and preventing contact with the turf, the catch is fair and the batter is OUT.
    - Grass Contact / Ground Deflection: If the ball touches the turf between the fingers or spills onto the grass while sliding, the third umpire must rule NOT OUT.
    - Zoom & Super Slow-Motion: Umpires inspect multiple synchronized zoom angles (front-on, side-on, reverse) to check if blades of grass bend underneath the ball or if the ball deforms against the turf.

    3. Benefit of the Doubt:
    In low catch reviews, if conclusive camera angles do not confirm fingers were completely under the ball, the benefit of doubt remains with the batter (Not Out).
    """,

    "Caught Behind / UltraEdge": """
    MCC Law 33 – Caught & ICC DRS UltraEdge (Snicko) Protocol.

    1. Definition of Caught:
    The striker is out Caught if a legitimately delivered ball touches the bat or the hand holding the bat (glove below the wrist) and is held by a fielder cleanly before touching the ground.

    2. Third Umpire & UltraEdge (Snicko) Review Sequence:
    - Check fair delivery (front-foot and back-foot no-ball).
    - UltraEdge / Real-Time Snickometer (RTS): Look for a sharp audio waveform spike exactly synchronized with the visual frame of the ball passing the edge of the bat.
    - Flatline on UltraEdge: If there is a flatline when the ball passes the bat, no contact occurred.
    - Bat hitting pad/ground: If the spike coincides with the bat hitting the turf or pad rather than the ball, it must be dismissed as ambient contact.
    - Grounding Check: If caught near turf, zoom frames must establish whether fingers were completely underneath the ball before the ball touched the pitch.
    """,

    "Run Out / Crease Grounding (MCC Law 38)": """
    MCC Law 38 – Run Out & Law 30 (Batter out of their ground).

    1. Definition of Run Out (Law 38.1 & 38.2):
    Either batter is out Run Out if, at any time while the ball is in play, they are out of their ground and their wicket is fairly broken by the action of a fielder.

    2. Batter in or out of their ground (Law 30):
    - A batter is considered in their ground only if some part of their person or their bat in hand is grounded behind the inside edge of the popping crease.
    - If the bat or foot is merely ON the line, the batter is NOT in their ground (the crease line belongs to the fielding side).
    - Bat bouncing after grounding (Law 30.1.2): If a running batter grounds their bat or foot behind the popping crease and subsequent forward momentum causes the bat to bounce up into the air while the bails are broken, the batter is deemed NOT OUT.

    3. Fairly breaking the wicket (Law 29):
    - At least one bail must be completely dislodged from the stump top.
    - On LED Zing wickets, the wicket is broken at the first frame the red lights illuminate indicating bail spigot separation.

    4. Third Umpire Protocol:
    The TV umpire inspects synchronized side-on cameras to determine whether the bat or person was grounded behind the popping crease at the exact frame the bails were dislodged.
    """,

    "Run Out at Non-Striker's End": """
    MCC Law 38.3 – Run Out at Non-Striker's End (formerly Law 41.16).

    1. Official Law:
    At any time from the moment the ball comes into play until the instant when the bowler would normally have been expected to release the ball in their delivery stride, the bowler is permitted to run out the non-striker with the ball if the non-striker is out of their ground.

    2. Key Timing Considerations:
    - The bowler must attempt the run out BEFORE completing their normal bowling arm rotation / release point.
    - Once the bowler reaches the point where they would normally release the ball, they can no longer legally run out the non-striker.
    - MCC re-codified this from 'Unfair Play' (Law 41) into Law 38 (Run Out) to confirm it is a completely legitimate method of dismissal.
    - Non-strikers are responsible for staying behind the popping crease line until the ball is actually bowled.
    """,

    "Waist-High Full Toss (No Ball)": """
    MCC Law 41.7 – Bowling of Dangerous and Unfair Non-Pitching Deliveries & ICC Playing Conditions.

    1. Waist-Height Threshold:
    Any ball that passes, or would have passed, on the full (without pitching) above the waist height of the striker standing upright at the popping crease is deemed unfair and shall be called a No Ball.

    2. Modern DRS / Ball-Tracking Waist Height Technology:
    - The batsman's waist height is pre-measured in an upright standing stance at the crease.
    - Trajectory calculation: If the batter crouches, bends their knees, or steps down the pitch, the third umpire calculates where the ball WOULD have crossed the popping crease relative to the batter standing upright at the crease.
    - Dipping delivery: Slower balls dipping sharply must be projected at the crease line, not where the batter met the ball out in front.
    - Consequence: A No Ball awards 1 penalty run plus a Free Hit on the subsequent delivery in limited-overs cricket.
    """,

    "Boundary Catch / Aerial Relay": """
    MCC Law 19 – Boundaries & Law 33.2 (Fair Catch).

    1. Grounding Criteria:
    - A fielder's first contact with the ball must be made within the boundary (i.e. the fielder must not be grounded beyond the boundary line).
    - If a fielder jumps from inside the boundary, takes the ball airborne, and throws it back into play before landing beyond the boundary line, it is legitimate.
    - Any subsequent touch: An airborne fielder who previously landed outside the boundary MUST re-ground themselves inside the field of play BEFORE touching the ball again.
    
    2. Touching the Boundary:
    - If any part of the fielder's body or clothing touches the boundary rope, cushions, or the turf beyond the rope while they are in contact with the ball, a boundary (4 or 6) is scored immediately.
    """,

    "Timed Out": """
    MCC Law 40 – Timed Out & ICC Men's Cricket World Cup Playing Conditions (Clause 40.1.1).

    1. Time Limit:
    After the fall of a wicket or the retirement of a batter, the incoming batter must be in position to take guard or for the other batter to be ready to receive the next ball within:
    - 3 minutes under standard MCC Laws.
    - 2 minutes under ICC World Cup, ODI, and T20 Playing Conditions.

    2. Equipment Malfunction & Appeal:
    - The incoming batter must be ready to receive within the required time window.
    - If equipment fails (e.g. broken helmet strap) after stepping onto the pitch, the umpires must determine whether the batter initiated the delay or requested permission before the time expired.
    - The fielding captain MUST officially lodge an appeal for 'Timed Out' to be awarded by the umpire. The captain is entitled to withdraw the appeal before the next ball is bowled.
    """
}

ALL_RULES = CRICKET_RULES

SPORTS = {
    "cricket": {
        "name": "Cricket",
        "governing_body": "MCC Laws of Cricket & ICC DRS Playing Conditions",
        "rules": CRICKET_RULES
    }
}


def get_rule(incident: str, sport: str = "cricket") -> Optional[str]:
    """Finds rule text for a given cricket incident name."""
    return CRICKET_RULES.get(incident)


def get_supported_incidents(sport: str = "cricket") -> list:
    """Returns list of supported cricket incidents."""
    return list(CRICKET_RULES.keys())


def classify_incident(description: str, sport: Optional[str] = "cricket") -> Tuple[str, str]:
    """
    Automatically identifies the most relevant official cricket rule category
    from the user's description or match scenario.
    Returns: (detected_incident, "cricket")
    """
    if not description:
        return "LBW / DRS Umpire's Call", "cricket"

    text = description.lower()

    # Cricket rule signals
    cricket_signals = [
        ("Fair Catch / Grounded Catch (MCC Law 33)", "cricket", [
            "is it caught out or not", "is it caught out", "caught out or not", "caught out", 
            "is it caught", "is it out or not", "out or not out", "out or not", 
            "not out", "caught", "catch", "low catch", "grounded", "ground", 
            "grass", "turf", "fingers under", "fingers under the ball", "under the ball", 
            "diving catch", "diving", "dive", "clean catch", "fair catch", "bump ball", 
            "taken cleanly", "cleanly taken", "slip catch", "spilled", "dropped", "fingers"
        ]),
        ("LBW / DRS Umpire's Call", "cricket", [
            "lbw", "leg before", "pad", "pitched", "pitching", "impact in line", 
            "ball tracking", "hawk-eye", "stumps", "wicket hitting", "stump line", 
            "umpire's call", "front pad", "spinning back in", "clipping"
        ]),
        ("Caught Behind / UltraEdge", "cricket", [
            "ultraedge", "snicko", "snickometer", "caught behind", "edge", 
            "spike", "murmur", "bat blade", "keeper caught", "edging", "nicked", 
            "outside edge", "snick", "feathered"
        ]),
        ("Run Out / Crease Grounding (MCC Law 38)", "cricket", [
            "run out", "runout", "run-out", "crease", "popping crease", 
            "diving for crease", "diving into the crease", "bat grounded", 
            "bails off", "stumps broken", "direct hit", "out of his ground", 
            "out of her ground", "out of ground", "out of crease", "bat on line", 
            "on the line", "line belongs to umpire", "bat bounced", "diving bat", 
            "dragged bat", "stumped", "stumping", "run out appeal", "is it run out", 
            "is he run out", "was he run out", "run out or not", "run-out check"
        ]),
        ("Run Out at Non-Striker's End", "cricket", [
            "non-striker", "mankad", "delivery stride", "backed up", "bails off", 
            "popping crease before release", "bowler stopped", "crease before release", 
            "deepti", "charlie dean"
        ]),
        ("Waist-High Full Toss (No Ball)", "cricket", [
            "full toss", "waist", "beamer", "above waist", "no ball", 
            "free hit", "high full toss", "nawaz"
        ]),
        ("Boundary Catch / Aerial Relay", "cricket", [
            "boundary catch", "catch or boundary", "boundary or catch", 
            "is this a catch or boundary", "is it a catch or boundary",
            "is it catch or boundary", "catch or six", "six or catch",
            "is it out or six", "is it six or out", "six or out", "out or six",
            "boundary rope", "boundary cushion", "boundary sponge", "cushion", 
            "boundary line", "aerial relay", "relay catch", "over the rope", 
            "jumped inside", "touched the rope", "foot on the rope", "brushing the rope", 
            "stepped on the rope", "stepped over the rope", "beyond the boundary",
            "boundary rider", "cushions", "boundary", "rope"
        ]),
        ("Timed Out", "cricket", [
            "timed out", "helmet strap", "2 minutes", "3 minutes", "take guard", 
            "incoming batter", "delay", "mathews", "shakib"
        ])
    ]

    candidates = []
    for inc_name, inc_sport, keywords in cricket_signals:
        score = 0
        for kw in keywords:
            if kw in text:
                score += len(kw.split()) * 3
        if score > 0:
            candidates.append((score, inc_name, "cricket"))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1], "cricket"

    return "LBW / DRS Umpire's Call", "cricket"
