import React, { useState, useEffect } from 'react';
import { 
  Sparkles, CheckCircle2, HelpCircle, XCircle, FileDown, 
  RefreshCw, ExternalLink, ShieldCheck, ArrowRight, UserCheck, 
  MapPin, Briefcase, IndianRupee, Layers, CheckSquare
} from 'lucide-react';

export default function App() {
  const [inputText, setInputText] = useState("");
  const [language, setLanguage] = useState("English");
  const [activeCategory, setActiveCategory] = useState("All");
  const [profile, setProfile] = useState({});
  const [results, setResults] = useState([]);
  const [metrics, setMetrics] = useState({ likely: 0, possibly: 0, more_info: 0, not_eligible: 0, total: 0 });
  const [missingPrompt, setMissingPrompt] = useState(null);
  const [loading, setLoading] = useState(false);
  const [checkedDocs, setCheckedDocs] = useState({});
  const [extractionError, setExtractionError] = useState(null);
  const [apiKey, setApiKey] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [clarificationInput, setClarificationInput] = useState("");

  // Quick Scenarios tailored for English, Punjabi, Hindi
  const scenarios = [
    {
      id: 'farmer-en',
      tag: '🌾 Punjab Farmer (EN)',
      text: "I'm a 42-year-old farmer from Punjab with an annual family income of ₹2 lakh."
    },
    {
      id: 'farmer-pa',
      tag: '🌾 ਕਿਸਾਨ (ਪੰਜਾਬੀ)',
      text: "ਮੈਂ ਪੰਜਾਬ ਤੋਂ 42 ਸਾਲਾਂ ਦਾ ਕਿਸਾਨ ਹਾਂ ਅਤੇ ਮੇਰੀ ਸਾਲਾਨਾ ਪਰਿਵਾਰਕ ਆਮਦਨ 2 ਲੱਖ ਰੁਪਏ ਹੈ।"
    },
    {
      id: 'farmer-hi',
      tag: '🌾 किसान (हिंदी)',
      text: "मैं पंजाब से 42 साल का किसान हूँ, पारिवारिक वार्षिक आय 2 लाख रुपये है।"
    },
    {
      id: 'student-pa',
      tag: '🎓 ਵਿਦਿਆਰਥੀ (Scholarship)',
      text: "ਮੈਂ ਪੰਜਾਬ ਦਾ ਵਿਦਿਆਰਥੀ ਹਾਂ ਅਤੇ ਪੜ੍ਹਾਈ ਲਈ ਵਜ਼ੀਫ਼ਾ (scholarship) ਲੱਭ ਰਿਹਾ ਹਾਂ। ਪਰਿਵਾਰਕ ਆਮਦਨ ₹1.5 ਲੱਖ ਹੈ।"
    },
    {
      id: 'senior-pa',
      tag: '👵 ਬਜ਼ੁਰਗ (Pension)',
      text: "ਮੇਰੀ ਉਮਰ 68 ਸਾਲ ਹੈ, ਪੇਂਡੂ ਖੇਤਰ ਵਿੱਚ ਰਹਿੰਦਾ ਹਾਂ ਅਤੇ ਸਾਲਾਨਾ ਆਮਦਨ ₹80,000 ਹੈ।"
    }
  ];

  // Placeholder mapping
  const placeholders = {
    "English": "e.g. I am a 42-year-old farmer from Punjab with an annual family income of ₹2 lakh.",
    "ਪੰਜਾਬੀ (Punjabi)": "ਜਿਵੇਂ: ਮੈਂ ਪੰਜਾਬ ਤੋਂ 42 ਸਾਲਾਂ ਦਾ ਕਿਸਾਨ ਹਾਂ ਅਤੇ ਮੇਰੀ ਸਾਲਾਨਾ ਪਰਿਵਾਰਕ ਆਮਦਨ 2 ਲੱਖ ਰੁਪਏ ਹੈ।",
    "हिंदी (हिंदी)": "जैसे: मैं पंजाब से 42 वर्ष का किसान हूँ और मेरी पारिवारिक आय ₹2 लाख है।"
  };

  // Initial fetch of schemes
  useEffect(() => {
    handleEvaluate("", false);
  }, []);

  const handleEvaluate = async (textToUse = inputText, shouldMerge = false) => {
    setLoading(true);
    setExtractionError(null);
    try {
      const res = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textToUse,
          profile: shouldMerge ? profile : null,
          category: activeCategory,
          api_key: apiKey ? apiKey.trim() : null,
          merge: shouldMerge
        })
      });
      if (res.ok) {
        const data = await res.json();
        setProfile(data.profile || {});
        setResults(data.results || []);
        setMetrics(data.metrics || { likely: 0, possibly: 0, more_info: 0, not_eligible: 0, total: 0 });
        setMissingPrompt(data.missing_prompt);
        if (data.extraction_error) {
          setExtractionError(data.extraction_error);
        }
      }
    } catch (err) {
      console.error("Evaluation request error:", err);
      setExtractionError("Failed to connect to SchemeSathi API server.");
    } finally {
      setLoading(false);
    }
  };

  const handleResetProfile = () => {
    setProfile({});
    setInputText("");
    setClarificationInput("");
    handleEvaluate("", false);
  };

  const handleCategoryChange = async (cat) => {
    setActiveCategory(cat);
    setLoading(true);
    try {
      const res = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: "",
          profile: profile,
          category: cat
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
        setMetrics(data.metrics || { likely: 0, possibly: 0, more_info: 0, not_eligible: 0, total: 0 });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const res = await fetch("/api/export/pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile, category: activeCategory })
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "SchemeSathi_CSC_Checklist.pdf";
      a.click();
    } catch (e) {
      alert("Failed to download PDF.");
    }
  };

  const handleDownloadText = async () => {
    try {
      const res = await fetch("/api/export/text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile, category: activeCategory })
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "SchemeSathi_Verification_Docket.txt";
      a.click();
    } catch (e) {
      alert("Failed to download text docket.");
    }
  };

  const toggleDoc = (schemeId, docName) => {
    const key = `${schemeId}_${docName}`;
    setCheckedDocs(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const knownFields = Object.entries(profile).filter(([k, v]) => v !== null && v !== undefined && v !== "");

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Top Navbar */}
      <nav style={{
        borderBottom: "1px solid var(--border-subtle)",
        background: "rgba(11, 15, 25, 0.8)",
        backdropFilter: "blur(12px)",
        position: "sticky",
        top: 0,
        zIndex: 50,
        padding: "16px 28px"
      }}>
        <div style={{ maxWidth: "1280px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span style={{ fontSize: "1.8rem" }}>🇮🇳</span>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "1.25rem", fontWeight: "800", letterSpacing: "-0.02em", color: "#ffffff" }}>SchemeSathi</span>
                <span style={{ 
                  background: "linear-gradient(90deg, #f59e0b, #10b981)", 
                  color: "#000", 
                  padding: "2px 8px", 
                  borderRadius: "9999px", 
                  fontSize: "0.65rem", 
                  fontWeight: "800" 
                }}>MVP</span>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Transparent Government Scheme Navigator</div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            {/* Language Selector */}
            <div style={{ display: "flex", background: "rgba(255,255,255,0.05)", borderRadius: "8px", padding: "3px", border: "1px solid var(--border-subtle)" }}>
              {["English", "ਪੰਜਾਬੀ (Punjabi)", "हिंदी (हिंदी)"].map((lang) => (
                <button
                  key={lang}
                  onClick={() => setLanguage(lang)}
                  style={{
                    background: language === lang ? "rgba(59, 130, 246, 0.3)" : "transparent",
                    color: language === lang ? "#60a5fa" : "var(--text-muted)",
                    border: language === lang ? "1px solid rgba(59, 130, 246, 0.4)" : "none",
                    borderRadius: "6px",
                    padding: "4px 10px",
                    fontSize: "0.75rem",
                    fontWeight: "600",
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                >
                  {lang}
                </button>
              ))}
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.78rem", color: "#34d399", background: "rgba(16, 185, 129, 0.1)", padding: "4px 10px", borderRadius: "9999px", border: "1px solid rgba(16, 185, 129, 0.25)" }}>
              <ShieldCheck size={14} /> CSC Ready
            </div>

            <button
              onClick={() => setShowSettings(!showSettings)}
              style={{
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid var(--border-subtle)",
                color: "#94a3b8",
                borderRadius: "8px",
                padding: "6px 10px",
                fontSize: "0.75rem",
                cursor: "pointer"
              }}
              title="API Key Configuration"
            >
              ⚙️ Settings
            </button>
          </div>
        </div>

        {/* Optional Settings Drawer */}
        {showSettings && (
          <div style={{
            maxWidth: "1280px",
            margin: "12px auto 0 auto",
            background: "rgba(16, 23, 38, 0.95)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "10px",
            padding: "16px 20px",
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            gap: "16px",
            fontSize: "0.85rem"
          }}>
            <div style={{ flex: 1, minWidth: "260px" }}>
              <label style={{ display: "block", color: "#cbd5e1", marginBottom: "4px", fontWeight: "600" }}>
                OpenRouter API Key (Optional override, defaults to .env):
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Leave blank to use server .env key automatically"
                style={{
                  width: "100%",
                  background: "#07090e",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "6px",
                  padding: "6px 12px",
                  color: "#f8fafc",
                  fontSize: "0.85rem"
                }}
              />
            </div>
            <div style={{ color: "#94a3b8", fontSize: "0.75rem", maxWidth: "450px" }}>
              💡 If left blank, SchemeSathi securely reads <code>OPENROUTER_API_KEY</code> from your local <code>.env</code> file.
            </div>
          </div>
        )}
      </nav>

      {/* Main Content Container */}
      <main style={{ maxWidth: "1280px", margin: "0 auto", padding: "40px 24px", width: "100%", flex: 1 }}>
        
        {/* Sarvam AI Style Hero Section */}
        <section style={{ textAlign: "center", marginBottom: "40px" }}>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            background: "rgba(245, 158, 11, 0.1)",
            color: "#fbbf24",
            padding: "6px 14px",
            borderRadius: "9999px",
            fontSize: "0.8rem",
            fontWeight: "600",
            marginBottom: "16px",
            border: "1px solid rgba(245, 158, 11, 0.25)"
          }}>
            <Sparkles size={14} /> Regional Language AI + Deterministic Statutory Rules
          </div>
          
          <h1 style={{
            fontSize: "clamp(2rem, 5vw, 3.25rem)",
            fontWeight: "800",
            letterSpacing: "-0.03em",
            lineHeight: 1.15,
            marginBottom: "16px",
            background: "linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent"
          }}>
            Find Indian Government Schemes<br />That Fit Your Exact Situation.
          </h1>
          
          <p style={{
            fontSize: "1.1rem",
            color: "var(--text-muted)",
            maxWidth: "760px",
            margin: "0 auto 28px auto",
            fontWeight: "400"
          }}>
            Speak or type naturally in <strong>ਪੰਜਾਬੀ, हिंदी, or English</strong>. SchemeSathi extracts your profile and deterministically evaluates statutory eligibility with zero hallucination.
          </p>

          {/* Quick Scenario Buttons */}
          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "10px", maxWidth: "900px", margin: "0 auto" }}>
            {scenarios.map((sc) => (
              <button
                key={sc.id}
                onClick={() => {
                  setInputText(sc.text);
                  setProfile({});
                  handleEvaluate(sc.text, false);
                }}
                className="btn-secondary"
                style={{ fontSize: "0.82rem", padding: "6px 14px" }}
              >
                {sc.tag}
              </button>
            ))}
          </div>
        </section>

        {/* Input Console */}
        <section className="glass-panel" style={{ padding: "24px", marginBottom: "32px", position: "relative" }}>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: "600", color: "#e2e8f0", marginBottom: "10px" }}>
            Tell SchemeSathi about yourself (Age, State, Occupation, Annual Income, Rural/Urban):
          </label>
          
          <div style={{ position: "relative" }}>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={placeholders[language] || placeholders["English"]}
              rows={3}
              style={{
                width: "100%",
                background: "rgba(7, 9, 14, 0.8)",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                borderRadius: "10px",
                padding: "14px 16px",
                color: "#f8fafc",
                fontSize: "1rem",
                fontFamily: "inherit",
                resize: "vertical",
                outline: "none"
              }}
              onFocus={(e) => e.target.style.borderColor = "#3b82f6"}
              onBlur={(e) => e.target.style.borderColor = "rgba(255, 255, 255, 0.12)"}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "14px" }}>
            <div style={{ fontSize: "0.8rem", color: "var(--text-dim)" }}>
              AI extracts structured facts • Deterministic code verifies statutory rules
            </div>
            <button
              onClick={() => handleEvaluate(inputText, false)}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="animate-spin" /> Evaluating...
                </>
              ) : (
                <>
                  Check Eligibility <ArrowRight size={16} />
                </>
              )}
            </button>
          </div>
        </section>

        {/* Extraction Error Notice (if any) */}
        {extractionError && (
          <div style={{
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "10px",
            padding: "14px 18px",
            marginBottom: "24px",
            color: "#fca5a5",
            fontSize: "0.88rem",
            display: "flex",
            alignItems: "center",
            gap: "10px"
          }}>
            <XCircle size={18} color="#ef4444" style={{ flexShrink: 0 }} />
            <div>
              <strong>AI Notice:</strong> {extractionError}
              <div style={{ fontSize: "0.78rem", color: "#f87171", marginTop: "2px" }}>
                Make sure your OpenRouter API key is set in <code>.env</code> or in the top ⚙️ Settings.
              </div>
            </div>
          </div>
        )}

        {/* Active Profile Snapshot (if present) */}
        {knownFields.length > 0 && (
          <section className="glass-panel" style={{ padding: "18px 24px", marginBottom: "32px", borderLeft: "4px solid #3b82f6" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: "700", fontSize: "0.95rem" }}>
                <UserCheck size={18} color="#3b82f6" /> Extracted Citizen Profile
              </div>
              <button 
                onClick={handleResetProfile} 
                style={{ background: "none", border: "none", color: "#94a3b8", cursor: "pointer", fontSize: "0.8rem", display: "flex", alignItems: "center", gap: "4px" }}
              >
                <RefreshCw size={12} /> Clear Profile
              </button>
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
              {knownFields.map(([k, v]) => {
                const label = k.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                let displayVal = String(v);
                if (k.includes("income") && typeof v === 'number') {
                  displayVal = `₹${v.toLocaleString('en-IN')}`;
                }
                return (
                  <div key={k} style={{
                    background: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid var(--border-subtle)",
                    borderRadius: "8px",
                    padding: "6px 12px",
                    fontSize: "0.82rem"
                  }}>
                    <span style={{ color: "var(--text-dim)" }}>{label}: </span>
                    <strong style={{ color: "#38bdf8" }}>{displayVal}</strong>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* Smart Clarification Box */}
        {missingPrompt && knownFields.length > 0 && (
          <div style={{
            background: "rgba(245, 158, 11, 0.08)",
            border: "1px solid rgba(245, 158, 11, 0.25)",
            borderRadius: "12px",
            padding: "16px 20px",
            marginBottom: "32px",
            display: "flex",
            flexDirection: "column",
            gap: "12px"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <HelpCircle size={22} color="#fbbf24" style={{ flexShrink: 0 }} />
              <div style={{ fontSize: "0.92rem", color: "#fef3c7" }}>
                <strong>Smart Clarification:</strong> {missingPrompt}
              </div>
            </div>
            <div style={{ display: "flex", gap: "10px", marginTop: "2px" }}>
              <input
                type="text"
                placeholder="Reply to clarify (e.g. 'female', 'ਸ਼ਹਿਰੀ', 'no land')..."
                value={clarificationInput}
                onChange={(e) => setClarificationInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && clarificationInput.trim()) {
                    handleEvaluate(clarificationInput.trim(), true);
                    setClarificationInput("");
                  }
                }}
                style={{
                  flex: 1,
                  background: "rgba(7, 9, 14, 0.7)",
                  border: "1px solid rgba(245, 158, 11, 0.3)",
                  borderRadius: "8px",
                  padding: "8px 12px",
                  color: "#f8fafc",
                  fontSize: "0.85rem",
                  outline: "none"
                }}
              />
              <button
                onClick={() => {
                  if (clarificationInput.trim()) {
                    handleEvaluate(clarificationInput.trim(), true);
                    setClarificationInput("");
                  }
                }}
                className="btn-secondary"
                style={{
                  background: "rgba(245, 158, 11, 0.2)",
                  borderColor: "rgba(245, 158, 11, 0.4)",
                  color: "#fef3c7",
                  padding: "8px 14px",
                  fontSize: "0.82rem",
                  fontWeight: "600",
                  whiteSpace: "nowrap"
                }}
              >
                Refine Profile
              </button>
            </div>
          </div>
        )}

        {/* Metrics Counter Bar */}
        <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "16px", marginBottom: "32px" }}>
          <div className="glass-panel" style={{ padding: "18px 20px", borderLeft: "4px solid #10b981" }}>
            <div style={{ fontSize: "0.75rem", textTransform: "uppercase", fontWeight: "700", color: "#34d399", letterSpacing: "0.05em" }}>Likely Eligible</div>
            <div style={{ fontSize: "2rem", fontWeight: "800", color: "#ffffff", marginTop: "4px" }}>{metrics.likely}</div>
          </div>
          <div className="glass-panel" style={{ padding: "18px 20px", borderLeft: "4px solid #f59e0b" }}>
            <div style={{ fontSize: "0.75rem", textTransform: "uppercase", fontWeight: "700", color: "#fbbf24", letterSpacing: "0.05em" }}>Possibly Eligible</div>
            <div style={{ fontSize: "2rem", fontWeight: "800", color: "#ffffff", marginTop: "4px" }}>{metrics.possibly}</div>
          </div>
          <div className="glass-panel" style={{ padding: "18px 20px", borderLeft: "4px solid #3b82f6" }}>
            <div style={{ fontSize: "0.75rem", textTransform: "uppercase", fontWeight: "700", color: "#60a5fa", letterSpacing: "0.05em" }}>More Info Needed</div>
            <div style={{ fontSize: "2rem", fontWeight: "800", color: "#ffffff", marginTop: "4px" }}>{metrics.more_info}</div>
          </div>
          <div className="glass-panel" style={{ padding: "18px 20px", borderLeft: "4px solid #ef4444" }}>
            <div style={{ fontSize: "0.75rem", textTransform: "uppercase", fontWeight: "700", color: "#f87171", letterSpacing: "0.05em" }}>Not Eligible</div>
            <div style={{ fontSize: "2rem", fontWeight: "800", color: "#ffffff", marginTop: "4px" }}>{metrics.not_eligible}</div>
          </div>
        </section>

        {/* Sector Filter & Export Bar */}
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "16px", marginBottom: "24px" }}>
          {/* Sector Category Pills */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {["All", "Agriculture", "Housing", "Senior Citizens", "Women", "Employment", "Education", "Entrepreneurship"].map((cat) => (
              <button
                key={cat}
                onClick={() => handleCategoryChange(cat)}
                style={{
                  background: activeCategory === cat ? "rgba(59, 130, 246, 0.2)" : "rgba(255, 255, 255, 0.04)",
                  color: activeCategory === cat ? "#60a5fa" : "var(--text-muted)",
                  border: activeCategory === cat ? "1px solid #3b82f6" : "1px solid var(--border-subtle)",
                  borderRadius: "8px",
                  padding: "6px 14px",
                  fontSize: "0.82rem",
                  fontWeight: "600",
                  cursor: "pointer",
                  transition: "all 0.15s ease"
                }}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* CSC Export Actions */}
          <div style={{ display: "flex", gap: "10px" }}>
            <button onClick={handleDownloadPDF} className="btn-secondary" title="Download printable PDF for CSC Kendra visit">
              <FileDown size={15} color="#34d399" /> Download CSC PDF
            </button>
            <button onClick={handleDownloadText} className="btn-secondary" title="Download text docket">
              <FileDown size={15} color="#60a5fa" /> Text Docket
            </button>
          </div>
        </div>

        {/* Scheme Recommendation Cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {results.length === 0 ? (
            <div className="glass-panel" style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
              No schemes found for this sector filter.
            </div>
          ) : (
            results.map((res, idx) => {
              const statusClass = {
                "LIKELY ELIGIBLE": "badge-likely",
                "POSSIBLY ELIGIBLE": "badge-possibly",
                "MORE INFORMATION NEEDED": "badge-more-info",
                "NOT ELIGIBLE": "badge-not-eligible"
              }[res.status] || "badge-more-info";

              return (
                <div key={res.scheme_name || idx} className="glass-panel" style={{ padding: "24px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "12px", marginBottom: "12px" }}>
                    <div>
                      <span style={{ 
                        background: "rgba(255,255,255,0.06)", 
                        color: "#94a3b8", 
                        padding: "3px 10px", 
                        borderRadius: "6px", 
                        fontSize: "0.72rem", 
                        fontWeight: "700",
                        textTransform: "uppercase",
                        letterSpacing: "0.05em" 
                      }}>
                        {res.category}
                      </span>
                      <h3 style={{ fontSize: "1.25rem", fontWeight: "700", color: "#ffffff", marginTop: "8px" }}>
                        {res.scheme_name} {res.short_name && <span style={{ color: "var(--text-dim)", fontWeight: "400" }}>({res.short_name})</span>}
                      </h3>
                    </div>
                    <span className={`badge-status ${statusClass}`}>{res.status}</span>
                  </div>

                  {/* Key Benefit Banner */}
                  <div style={{
                    background: "rgba(30, 58, 138, 0.2)",
                    borderLeft: "3px solid #3b82f6",
                    padding: "10px 14px",
                    borderRadius: "6px",
                    marginBottom: "18px",
                    fontSize: "0.9rem"
                  }}>
                    <strong style={{ color: "#93c5fd" }}>Key Benefit: </strong>
                    <span style={{ color: "#e2e8f0" }}>{res.benefits}</span>
                  </div>

                  {/* Evaluation Grid */}
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px", marginBottom: "18px" }}>
                    
                    {/* Transparent Rule Evaluation */}
                    <div>
                      <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-dim)", letterSpacing: "0.05em", marginBottom: "8px" }}>
                        Statutory Rules Breakdown
                      </h4>
                      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                        {res.matched && res.matched.map((m, i) => (
                          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: "6px", color: "#34d399", fontSize: "0.85rem" }}>
                            <CheckCircle2 size={16} style={{ flexShrink: 0, marginTop: "2px" }} />
                            <span>{m.replace('✓ ', '')}</span>
                          </div>
                        ))}
                        {res.unknown && res.unknown.map((u, i) => (
                          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: "6px", color: "#94a3b8", fontSize: "0.85rem" }}>
                            <HelpCircle size={16} style={{ flexShrink: 0, marginTop: "2px" }} />
                            <span>{u.replace('? ', '')}</span>
                          </div>
                        ))}
                        {res.failed && res.failed.map((f, i) => (
                          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: "6px", color: "#f87171", fontSize: "0.85rem" }}>
                            <XCircle size={16} style={{ flexShrink: 0, marginTop: "2px" }} />
                            <span>{f.replace('✗ ', '')}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Required Documents Checklist */}
                    <div>
                      <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-dim)", letterSpacing: "0.05em", marginBottom: "8px" }}>
                        Required Documents for Verification
                      </h4>
                      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                        {res.required_documents && res.required_documents.map((doc, docIdx) => {
                          const isChecked = checkedDocs[`${res.scheme_name}_${doc}`] || false;
                          return (
                            <label
                              key={docIdx}
                              onClick={() => toggleDoc(res.scheme_name, doc)}
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "8px",
                                fontSize: "0.85rem",
                                color: isChecked ? "#34d399" : "#cbd5e1",
                                cursor: "pointer",
                                textDecoration: isChecked ? "line-through" : "none"
                              }}
                            >
                              <input 
                                type="checkbox" 
                                checked={isChecked} 
                                onChange={() => {}} 
                                style={{ accentColor: "#10b981", cursor: "pointer" }}
                              />
                              <span>{doc}</span>
                            </label>
                          );
                        })}
                      </div>

                      <div style={{ marginTop: "12px", fontSize: "0.82rem", color: "var(--text-muted)" }}>
                        <strong>Where to Apply:</strong> {res.application_info}
                      </div>
                    </div>
                  </div>

                  {/* Provenance Footer */}
                  <div style={{
                    borderTop: "1px solid var(--border-subtle)",
                    paddingTop: "12px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "8px",
                    fontSize: "0.78rem",
                    color: "var(--text-dim)"
                  }}>
                    <div>
                      🏛️ <strong>Authority:</strong> {res.source_name}
                    </div>
                    <div>
                      <a
                        href={res.source_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ color: "#60a5fa", display: "inline-flex", alignItems: "center", gap: "4px", textDecoration: "none" }}
                      >
                        Official Government Portal <ExternalLink size={12} />
                      </a>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: "1px solid var(--border-subtle)",
        background: "rgba(11, 15, 25, 0.9)",
        padding: "24px 28px",
        marginTop: "40px"
      }}>
        <div style={{ maxWidth: "1280px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-dim)" }}>
            Notice: SchemeSathi provides transparent navigation based on statutory criteria. Final eligibility rests with administering authorities.
          </div>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
            Built for Hacktoberfest Open-Source AI Challenge • MIT License
          </div>
        </div>
      </footer>
    </div>
  );
}

