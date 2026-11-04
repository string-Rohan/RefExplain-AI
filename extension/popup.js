/**
 * RefExplain Cricket AI - Extension Popup Logic
 * Dedicated Cricket Decision Review Assistant evaluated against official MCC Laws of Cricket and ICC DRS Protocols.
 */

const API_BASE = "http://127.0.0.1:8000";

const CRICKET_CONFIG = {
  name: "CRICKET",
  officialRole: "UMPIRE",
  rulebook: "MCC Laws & ICC DRS Protocols",
  loadingText: "Evaluating cricket incident against official MCC Laws & DRS tracking evidence...",
  placeholder: "Describe the cricket incident (e.g. ball pitched outside off and struck front pad in line with stumps, UltraEdge spike timing as ball passed bat, diving batter bat grounding before bails removed)...",
  presets: {
    "kohli-lbw-umpires-call": {
      title: "LBW: Virat Kohli Umpire's Call on Impact",
      incident: "LBW / DRS Umpire's Call",
      description: "Kohli played forward to a ball spinning sharply back in. The ball struck him on the front pad in line with off stump. The on-field umpire ruled Out. Kohli reviewed via DRS; ball tracking showed impact clipping the 50% line of off stump, so Umpire's Call stood."
    },
    "mathews-timed-out": {
      title: "Timed Out: Angelo Mathews vs Bangladesh (World Cup)",
      incident: "Timed Out",
      description: "Mathews walked in to bat after a wicket fell. His helmet strap broke before taking guard. While waiting for a replacement helmet, the fielding captain appealed for 'Timed Out'. Umpires upheld the appeal as more than 2 minutes elapsed."
    },
    "deepti-mankad-dean": {
      title: "Run Out: Deepti Sharma vs Charlie Dean (Lord's)",
      incident: "Run Out at Non-Striker's End",
      description: "Non-striker consistently backed up yards out of her crease before ball release. The bowler entered her delivery stride and took the bails off before completing the delivery swing. Batter was given out run out."
    },
    "nawaz-mcg-noball": {
      title: "No Ball: Nawaz Waist-High Full Toss to Kohli",
      incident: "Waist-High Full Toss (No Ball)",
      description: "In the final over of a tense chase, bowler bowled a high full toss. Batter pulled it for six and signaled for waist-height no-ball. The square-leg umpire signaled a No Ball, granting a free hit."
    },
    "pant-ultraedge-caught-behind": {
      title: "UltraEdge: Rishabh Pant Caught Behind Dispute",
      incident: "Caught Behind / UltraEdge",
      description: "Fast bowler bowled a delivery shaping past outside edge. Keeper caught it and appealed. On-field umpire gave Not Out. On DRS review, UltraEdge displayed a murmur spike as ball was 2 inches past the bat blade. Umpire overturned to Out."
    },
    "boundary-relay-catch": {
      title: "Boundary Catch: Aerial Relay Over Rope",
      incident: "Boundary Catch / Aerial Relay",
      description: "Fielder leaps inside the boundary rope, catches ball airborne, tosses it into the air before his momentum takes him over the rope. He steps back inside the boundary cushions and completes the catch cleanly."
    },
    "low-catch-grounded": {
      title: "Fair Catch: Low Diving Catch & Turf Contact Check",
      incident: "Fair Catch / Grounded Catch (MCC Law 33)",
      description: "Fielder dived forward to pouch a low catch inches above the turf. Umpires inspect super-slow-mo zoom frames to verify whether fingers were cleanly underneath the ball or if the ball touched the grass before control was established."
    },
    "run-out-crease-grounding": {
      title: "Run Out: Diving Batter Crease Grounding Check",
      incident: "Run Out / Crease Grounding (MCC Law 38)",
      description: "A diving batter stretches with outstretched bat towards the popping crease while the wicketkeeper breaks the wickets. The third umpire inspects side-on super-slow-mo frames to determine whether the bat grounded behind the crease before the bails separated."
    }
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const presetSelect = document.getElementById("presetSelect");
  const descriptionInput = document.getElementById("descriptionInput") || document.getElementById("description");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const loading = document.getElementById("loading");
  const loadingText = document.getElementById("loadingText");
  const result = document.getElementById("result");
  const errorState = document.getElementById("errorState");
  const errorMessage = document.getElementById("errorMessage");

  const imageDropzone = document.getElementById("imageDropzone");
  const imageInput = document.getElementById("imageInput");
  const uploadPrompt = document.getElementById("uploadPrompt");
  const imagePreviewCard = document.getElementById("imagePreviewCard");
  const imagePreviewImg = document.getElementById("imagePreviewImg");
  const imagePreviewName = document.getElementById("imagePreviewName");
  const imagePreviewSize = document.getElementById("imagePreviewSize");
  const imageRemoveBtn = document.getElementById("imageRemoveBtn");
  const imageBadge = document.getElementById("imageBadge");

  const sportBadge = document.getElementById("sportBadge");
  const assessmentBadge = document.getElementById("assessmentBadge");
  const secHeadingDecisionMaker = document.getElementById("secHeadingDecisionMaker");
  const secWhatHappened = document.getElementById("secWhatHappened");
  const secApplicableRule = document.getElementById("secApplicableRule");
  const secRefereeReasoning = document.getElementById("secRefereeReasoning");
  const secEvidenceToCheck = document.getElementById("secEvidenceToCheck");
  const secAssessment = document.getElementById("secAssessment");
  const rawFallback = document.getElementById("rawFallback");
  const explanationText = document.getElementById("explanationText");

  let currentImageBase64 = null;

  function initUI() {
    if (descriptionInput) {
      descriptionInput.placeholder = CRICKET_CONFIG.placeholder;
    }
    if (loadingText) {
      loadingText.textContent = CRICKET_CONFIG.loadingText;
    }
    if (presetSelect) {
      presetSelect.innerHTML = '<option value="">-- Choose a cricket scenario --</option>';
      for (const [key, preset] of Object.entries(CRICKET_CONFIG.presets)) {
        const opt = document.createElement("option");
        opt.value = key;
        opt.textContent = preset.title;
        presetSelect.appendChild(opt);
      }
    }
    if (sportBadge) {
      sportBadge.textContent = "CRICKET";
    }
    if (secHeadingDecisionMaker) {
      secHeadingDecisionMaker.textContent = "3. WHY THE UMPIRE MADE THIS DECISION";
    }
  }

  initUI();

  function handleImageFile(file) {
    if (!file || !file.type.startsWith("image/")) {
      showError("Please upload a valid image file (PNG, JPG, or WebP).");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      showError("Image file size is too large (maximum 10 MB).");
      return;
    }
    hideError();
    const reader = new FileReader();
    reader.onload = (e) => {
      currentImageBase64 = e.target.result;
      if (imagePreviewImg) imagePreviewImg.src = currentImageBase64;
      if (imagePreviewName) imagePreviewName.textContent = file.name || "Match screenshot";
      const kb = Math.round(file.size / 1024);
      if (imagePreviewSize) imagePreviewSize.textContent = `${kb > 0 ? kb : 1} KB • Attached`;
      if (uploadPrompt) uploadPrompt.hidden = true;
      if (imagePreviewCard) imagePreviewCard.hidden = false;
    };
    reader.readAsDataURL(file);
  }

  function clearImage() {
    currentImageBase64 = null;
    if (imageInput) imageInput.value = "";
    if (imagePreviewImg) imagePreviewImg.src = "";
    if (imagePreviewCard) imagePreviewCard.hidden = true;
    if (uploadPrompt) uploadPrompt.hidden = false;
  }

  if (imageDropzone) {
    imageDropzone.addEventListener("click", (e) => {
      if (e.target.closest("#imageRemoveBtn")) return;
      imageInput.click();
    });

    imageDropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      imageDropzone.classList.add("dragover");
    });

    imageDropzone.addEventListener("dragleave", () => {
      imageDropzone.classList.remove("dragover");
    });

    imageDropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      imageDropzone.classList.remove("dragover");
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleImageFile(e.dataTransfer.files[0]);
      }
    });
  }

  if (imageInput) {
    imageInput.addEventListener("change", () => {
      if (imageInput.files && imageInput.files[0]) {
        handleImageFile(imageInput.files[0]);
      }
    });
  }

  if (imageRemoveBtn) {
    imageRemoveBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      clearImage();
    });
  }

  // Ctrl+V paste support for match screen clips
  window.addEventListener("paste", (e) => {
    const items = e.clipboardData && e.clipboardData.items;
    if (!items) return;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          handleImageFile(file);
          break;
        }
      }
    }
  });

  // Preset selection handler
  if (presetSelect) {
    presetSelect.addEventListener("change", (e) => {
      const key = e.target.value;
      hideError();
      if (key && CRICKET_CONFIG.presets[key]) {
        const preset = CRICKET_CONFIG.presets[key];
        if (descriptionInput) descriptionInput.value = preset.description;
      }
    });
  }

  // Synchronize typing: clear preset selection if user edits text
  if (descriptionInput) {
    descriptionInput.addEventListener("input", () => {
      hideError();
      if (presetSelect && presetSelect.value) {
        const found = CRICKET_CONFIG.presets[presetSelect.value];
        if (found && found.description !== descriptionInput.value) {
          presetSelect.value = "";
        }
      }
    });
  }

  // Analyze decision button click handler
  if (analyzeBtn) {
    analyzeBtn.addEventListener("click", async () => {
      const description = descriptionInput ? descriptionInput.value.trim() : "";
      const hasImage = Boolean(currentImageBase64);

      if (!description && !hasImage) {
        showError("Please describe what happened or upload a match screenshot.");
        return;
      }

      hideError();
      if (result) result.hidden = true;
      if (loading) loading.hidden = false;
      analyzeBtn.disabled = true;

      try {
        const response = await fetch(`${API_BASE}/analyze`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            sport: "cricket",
            description: description,
            image_base64: currentImageBase64
          })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || `Server error (${response.status})`);
        }

        displayResult(data);

      } catch (err) {
        console.error("[RefExplain AI]", err);
        showError(
          `Unable to reach backend: ${err.message}.\nMake sure FastAPI is running:\n` +
          `cd backend && uvicorn main:app --reload --port 8000`
        );
      } finally {
        if (loading) loading.hidden = true;
        analyzeBtn.disabled = false;
      }
    });
  }

  function displayResult(data) {
    // Sport badge
    if (sportBadge) {
      sportBadge.textContent = "CRICKET";
    }

    // Image evidence badge
    if (imageBadge) {
      imageBadge.hidden = !data.has_image;
    }

    // Populate direct decision hero
    const extHeroBadge = document.getElementById("extHeroBadge");
    const extHeroSummary = document.getElementById("extHeroSummary");
    if (extHeroBadge && extHeroSummary) {
      const directDec = (data.direct_decision || "REVIEW").toUpperCase();
      extHeroBadge.textContent = directDec;
      extHeroSummary.textContent = data.decision_summary || (data.sections && data.sections.what_happened) || "Match incident evaluated under MCC Laws of Cricket.";
      if (directDec.includes("NOT OUT") || directDec.includes("FAIR CATCH")) {
        extHeroBadge.style.color = "#1b4332";
        extHeroBadge.style.borderColor = "#2d6a4f";
        extHeroBadge.style.background = "#e8f5e9";
      } else if (directDec.includes("OUT") || directDec.includes("NO BALL") || directDec.includes("TIMED OUT") || directDec.includes("RUN OUT")) {
        extHeroBadge.style.color = "#b91c1c";
        extHeroBadge.style.borderColor = "#ef4444";
        extHeroBadge.style.background = "#fee2e2";
      } else {
        extHeroBadge.style.color = "#b89230";
        extHeroBadge.style.borderColor = "#e9c46a";
        extHeroBadge.style.background = "#fef9c3";
      }
    }

    // Update section 3 heading
    if (secHeadingDecisionMaker) {
      secHeadingDecisionMaker.textContent = "3. WHY THE UMPIRE MADE THIS DECISION";
    }

    // Assessment badge
    const assessment = (data.assessment || "Inconclusive").trim();
    if (assessmentBadge) {
      assessmentBadge.textContent = assessment;
      assessmentBadge.className = "badge";
      const lower = assessment.toLowerCase();
      if (lower.includes("appears correct")) {
        assessmentBadge.classList.add("correct");
      } else if (lower.includes("appears incorrect")) {
        assessmentBadge.classList.add("incorrect");
      } else {
        assessmentBadge.classList.add("inconclusive");
      }
    }

    // Populate structured sections if available
    if (data.sections && data.sections.what_happened) {
      if (secWhatHappened) secWhatHappened.textContent = data.sections.what_happened;
      if (secApplicableRule) secApplicableRule.textContent = data.sections.applicable_rule;
      if (secRefereeReasoning) secRefereeReasoning.textContent = data.sections.referee_reasoning;
      if (secEvidenceToCheck) secEvidenceToCheck.textContent = data.sections.evidence_to_check;
      if (secAssessment) secAssessment.textContent = data.sections.assessment;

      if (secWhatHappened && secWhatHappened.parentElement) secWhatHappened.parentElement.hidden = false;
      if (secApplicableRule && secApplicableRule.parentElement) secApplicableRule.parentElement.hidden = false;
      if (secRefereeReasoning && secRefereeReasoning.parentElement) secRefereeReasoning.parentElement.hidden = false;
      if (secEvidenceToCheck && secEvidenceToCheck.parentElement) secEvidenceToCheck.parentElement.hidden = false;
      if (secAssessment && secAssessment.parentElement) secAssessment.parentElement.hidden = false;
      if (rawFallback) rawFallback.hidden = true;
    } else {
      if (explanationText) explanationText.textContent = data.explanation || "No explanation returned.";
      if (rawFallback) rawFallback.hidden = false;
      if (secWhatHappened && secWhatHappened.parentElement) secWhatHappened.parentElement.hidden = true;
      if (secApplicableRule && secApplicableRule.parentElement) secApplicableRule.parentElement.hidden = true;
      if (secRefereeReasoning && secRefereeReasoning.parentElement) secRefereeReasoning.parentElement.hidden = true;
      if (secEvidenceToCheck && secEvidenceToCheck.parentElement) secEvidenceToCheck.parentElement.hidden = true;
      if (secAssessment && secAssessment.parentElement) secAssessment.parentElement.hidden = true;
    }

    if (result) {
      result.hidden = false;
      result.scrollIntoView({ behavior: "smooth" });
    }
  }

  function showError(msg) {
    if (errorMessage) errorMessage.textContent = msg;
    if (errorState) errorState.hidden = false;
  }

  function hideError() {
    if (errorState) errorState.hidden = true;
  }
});
