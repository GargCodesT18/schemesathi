"""SchemeSathi - Transparent AI-Powered Government Scheme Navigator
Streamlit Application
"""
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path regardless of how Streamlit is invoked
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.config import (
    APP_NAME,
    APP_TAGLINE,
    APP_VERSION,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)
from app.data.scheme_repository import SchemeRepository
from app.models.profile import CitizenProfile
from app.models.result import EligibilityStatus, CriterionStatus
from app.services.eligibility_service import EligibilityEngine
from app.services.explanation_service import ExplanationService
from app.services.export_service import ExportService
from app.services.llm_service import LLMService, OpenRouterProvider
from app.services.profile_service import ProfileService
from app.services.scheme_service import SchemeService

# Configure Page
st.set_page_config(
    page_title=f"{APP_NAME} — Government Scheme Navigator",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Theme CSS inspired by IndiaAI / AI Kosh dark aesthetics
CUSTOM_CSS = """
<style>
/* Main container background */
.stApp {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0e1526;
    border-right: 1px solid #1e293b;
}

/* Card styling */
.scheme-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.scheme-card:hover {
    border-color: #3b82f6;
}

/* Badge styling */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-likely {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.badge-possibly {
    background-color: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
.badge-more-info {
    background-color: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.3);
}
.badge-not-eligible {
    background-color: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}
.badge-category {
    background-color: #1e293b;
    color: #cbd5e1;
    border: 1px solid #334155;
}

/* Criteria checklist styles */
.criterion-matched {
    color: #34d399;
    font-size: 0.9rem;
    margin: 4px 0;
}
.criterion-failed {
    color: #f87171;
    font-size: 0.9rem;
    margin: 4px 0;
}
.criterion-unknown {
    color: #94a3b8;
    font-size: 0.9rem;
    margin: 4px 0;
}

/* Header highlight */
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.2rem;
}
.hero-tagline {
    font-size: 1.05rem;
    color: #94a3b8;
    margin-bottom: 1.5rem;
}

/* Provenance note */
.provenance-note {
    font-size: 0.8rem;
    color: #64748b;
    border-top: 1px solid #1e293b;
    padding-top: 8px;
    margin-top: 12px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Initialize Application Services
@st.cache_resource
def get_services():
    repo = SchemeRepository()
    engine = EligibilityEngine()
    explanation = ExplanationService()
    scheme_service = SchemeService(repository=repo, engine=engine, explanation_service=explanation)
    return repo, engine, explanation, scheme_service

repo, engine, explanation_service, scheme_service = get_services()

# Session State Initialization
if "profile" not in st.session_state:
    st.session_state.profile = CitizenProfile()
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "active_category" not in st.session_state:
    st.session_state.active_category = "All"
if "api_key" not in st.session_state:
    st.session_state.api_key = OPENROUTER_API_KEY
if "model_name" not in st.session_state:
    st.session_state.model_name = OPENROUTER_MODEL


# SIDEBAR
with st.sidebar:
    st.markdown(f"## 🇮🇳 {APP_NAME}")
    st.caption(f"v{APP_VERSION} • Open-Source Citizen Navigator")
    st.divider()

    # Sector Filter
    categories = ["All"] + repo.get_all_categories()
    selected_cat = st.selectbox(
        "🔍 Filter by Sector",
        categories,
        index=categories.index(st.session_state.active_category) if st.session_state.active_category in categories else 0
    )
    st.session_state.active_category = selected_cat

    st.divider()

    # Current Citizen Profile Snapshot
    st.markdown("### 👤 Active Profile")
    known_fields = st.session_state.profile.get_known_fields()
    if known_fields:
        for k, v in known_fields.items():
            field_display = k.replace('_', ' ').title()
            if isinstance(v, float) and "income" in k:
                val_display = f"₹{v:,.0f}"
            else:
                val_display = str(v)
            st.markdown(f"**{field_display}:** `{val_display}`")
        if st.button("🔄 Reset Profile", use_container_width=True):
            st.session_state.profile = CitizenProfile()
            st.rerun()
    else:
        st.info("No profile extracted yet. Describe your situation on the main page to populate.")

    st.divider()

    # OpenRouter AI Configuration
    with st.expander("⚙️ OpenRouter Settings", expanded=False):
        api_input = st.text_input("OpenRouter API Key", value=st.session_state.api_key, type="password")
        if api_input != st.session_state.api_key:
            st.session_state.api_key = api_input

        model_input = st.text_input("Model ID", value=st.session_state.model_name)
        if model_input != st.session_state.model_name:
            st.session_state.model_name = model_input

        st.caption("AI is used strictly for language understanding. All eligibility evaluations are deterministic Python software.")

    st.divider()
    with st.expander("🛡️ Privacy & Architecture", expanded=False):
        st.markdown(
            "• **Data Flow**: Your text is processed through the configured AI provider (OpenRouter) "
            "solely to extract structured attributes into memory.<br>"
            "• **No Long-term Storage**: Conversations and citizen profiles are not saved permanently.<br>"
            "• **Future Local Inference**: SchemeSathi is built with a provider-agnostic interface "
            "ready to support on-device models later.",
            unsafe_allow_html=True
        )


# MAIN CONTENT AREA
st.markdown(f'<div class="hero-title">{APP_NAME}</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-tagline">Find Indian government schemes that fit your exact situation. '
    'Transparent, criterion-by-criterion eligibility explanations with verified government provenance.</div>',
    unsafe_allow_html=True
)

# Regional Language Support (English, Punjabi, Hindi)
st.markdown("##### 🌐 Select Input Language / ਭਾਸ਼ਾ ਚੁਣੋ / भाषा चुनें:")
lang_col1, lang_col2 = st.columns([1.2, 3])
with lang_col1:
    selected_language = st.selectbox(
        "Input Language",
        ["English", "ਪੰਜਾਬੀ (Punjabi)", "हिंदी (Hindi)"],
        label_visibility="collapsed"
    )

with lang_col2:
    st.caption("SchemeSathi natively extracts profiles from English, ਪੰਜਾਬੀ (Punjabi), and हिंदी (Hindi), as well as Roman script.")

st.markdown("##### 💡 Quick Regional Scenarios:")
col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns(5)

scenario_text = None
with col_d1:
    if st.button("🌾 Punjab Farmer (EN)", use_container_width=True):
        scenario_text = "I'm a 42-year-old farmer from Punjab with an annual family income of ₹2 lakh."
with col_d2:
    if st.button("🌾 ਕਿਸਾਨ (ਪੰਜਾਬੀ)", use_container_width=True):
        scenario_text = "ਮੈਂ ਪੰਜਾਬ ਤੋਂ 42 ਸਾਲਾਂ ਦਾ ਕਿਸਾਨ ਹਾਂ ਅਤੇ ਮੇਰੀ ਸਾਲਾਨਾ ਪਰਿਵਾਰਕ ਆਮਦਨ 2 ਲੱਖ ਰੁਪਏ ਹੈ।"
with col_d3:
    if st.button("🌾 किसान (हिंदी)", use_container_width=True):
        scenario_text = "मैं पंजाब से 42 साल का किसान हूँ, पारिवारिक वार्षिक आय 2 लाख रुपये है।"
with col_d4:
    if st.button("🎓 ਵਿਦਿਆਰਥੀ / Student", use_container_width=True):
        scenario_text = "ਮੈਂ ਪੰਜਾਬ ਦਾ ਵਿਦਿਆਰਥੀ ਹਾਂ ਅਤੇ ਪੜ੍ਹਾਈ ਲਈ ਵਜ਼ੀਫ਼ਾ (scholarship) ਲੱਭ ਰਿਹਾ ਹਾਂ। ਪਰਿਵਾਰਕ ਆਮਦਨ ₹1.5 ਲੱਖ ਹੈ।"
with col_d5:
    if st.button("👵 ਬਜ਼ੁਰਗ / Senior", use_container_width=True):
        scenario_text = "ਮੇਰੀ ਉਮਰ 68 ਸਾਲ ਹੈ, ਪੇਂਡੂ ਖੇਤਰ ਵਿੱਚ ਰਹਿੰਦਾ ਹਾਂ ਅਤੇ ਸਾਲਾਨਾ ਆਮਦਨ ₹80,000 ਹੈ।"

# Placeholder text reflecting selected language
placeholders = {
    "English": "e.g. I am a 42-year-old farmer from Punjab with an annual family income of ₹2 lakh.",
    "ਪੰਜਾਬੀ (Punjabi)": "ਜਿਵੇਂ: ਮੈਂ ਪੰਜਾਬ ਤੋਂ 42 ਸਾਲਾਂ ਦਾ ਕਿਸਾਨ ਹਾਂ ਅਤੇ ਮੇਰੀ ਸਾਲਾਨਾ ਆਮਦਨ 2 ਲੱਖ ਰੁਪਏ ਹੈ।",
    "हिंदी (Hindi)": "जैसे: मैं पंजाब से 42 वर्ष का किसान हूँ और मेरी पारिवारिक आय ₹2 लाख है।"
}

# Conversational Input Form
default_query = scenario_text or st.session_state.last_query
with st.form("citizen_input_form"):
    user_query = st.text_area(
        "Tell SchemeSathi about yourself (Age, State, Occupation, Income, Rural/Urban) / ਆਪਣੇ ਬਾਰੇ ਦੱਸੋ / अपने बारे में बताएं:",
        value=default_query,
        height=95,
        placeholder=placeholders.get(selected_language, placeholders["English"])
    )
    submit_btn = st.form_submit_button("🔍 Find Applicable Schemes / ਯੋਜਨਾਵਾਂ ਲੱਭੋ / योजनाएं खोजें", use_container_width=True)

if submit_btn and user_query.strip():
    st.session_state.last_query = user_query.strip()
    
    # Process with LLM
    try:
        with st.spinner("Understanding your profile with AI..."):
            provider = OpenRouterProvider(
                api_key=st.session_state.api_key,
                model=st.session_state.model_name,
                base_url=OPENROUTER_BASE_URL
            )
            llm_service = LLMService(provider=provider)
            profile_service = ProfileService(llm_service=llm_service)
            
            # If we already have some data, merge; otherwise create fresh
            if st.session_state.profile.get_known_fields():
                updated_profile = profile_service.merge_profiles(st.session_state.profile, user_query.strip())
            else:
                updated_profile = profile_service.create_from_text(user_query.strip())
                
            st.session_state.profile = updated_profile
            st.success("Profile parsed and validated successfully!")
    except Exception as e:
        st.error(f"⚠️ Profile Extraction Notice: {str(e)}")
        st.info("You can still manually configure your profile fields below or set your OpenRouter API Key in the sidebar.")


# Interactive Profile Fine-Tuning Expander
with st.expander("✏️ Refine / Edit Extracted Profile", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cur_age = st.session_state.profile.age or 0
        new_age = st.number_input("Age", min_value=0, max_value=120, value=cur_age)
        cur_gender = st.session_state.profile.gender or "Not Specified"
        gender_options = ["Not Specified", "female", "male", "transgender", "other"]
        new_gender = st.selectbox("Gender", gender_options, index=gender_options.index(cur_gender) if cur_gender in gender_options else 0)
    with col2:
        cur_state = st.session_state.profile.state or ""
        new_state = st.text_input("State", value=cur_state)
        cur_rural = st.session_state.profile.rural_or_urban or "Not Specified"
        rural_opts = ["Not Specified", "rural", "urban"]
        new_rural = st.selectbox("Area Type", rural_opts, index=rural_opts.index(cur_rural) if cur_rural in rural_opts else 0)
    with col3:
        cur_occ = st.session_state.profile.occupation or ""
        new_occ = st.text_input("Occupation", value=cur_occ)
        cur_income = st.session_state.profile.annual_income or 0.0
        new_income = st.number_input("Annual Family Income (₹)", min_value=0.0, step=10000.0, value=float(cur_income))
    with col4:
        cur_farmer = st.session_state.profile.farmer_status or False
        new_farmer = st.checkbox("Farmer Status", value=cur_farmer)
        cur_student = st.session_state.profile.student_status or False
        new_student = st.checkbox("Student Status", value=cur_student)

    if st.button("Apply Profile Changes"):
        st.session_state.profile = CitizenProfile(
            age=new_age if new_age > 0 else None,
            gender=None if new_gender == "Not Specified" else new_gender,
            state=new_state.strip() if new_state.strip() else None,
            rural_or_urban=None if new_rural == "Not Specified" else new_rural,
            occupation=new_occ.strip() if new_occ.strip() else None,
            annual_income=new_income if new_income > 0 else None,
            farmer_status=new_farmer if new_farmer else None,
            student_status=new_student if new_student else None,
        )
        st.rerun()


# Evaluate Schemes
results = scheme_service.evaluate_citizen(st.session_state.profile, category_filter=st.session_state.active_category)

# Missing Information Clarification Prompt
missing_prompt = scheme_service.get_missing_info_question(st.session_state.profile, results)
if missing_prompt and st.session_state.profile.get_known_fields():
    st.warning(f"💬 **Smart Clarification:** {missing_prompt}")

st.markdown("---")

# Summary Metrics Row
m1, m2, m3, m4 = st.columns(4)
likely_count = sum(1 for r in results if r.status == EligibilityStatus.LIKELY_ELIGIBLE)
possibly_count = sum(1 for r in results if r.status == EligibilityStatus.POSSIBLY_ELIGIBLE)
more_info_count = sum(1 for r in results if r.status == EligibilityStatus.MORE_INFORMATION_NEEDED)
not_eligible_count = sum(1 for r in results if r.status == EligibilityStatus.NOT_ELIGIBLE)

m1.metric("Likely Eligible", likely_count)
m2.metric("Possibly Eligible", possibly_count)
m3.metric("More Info Needed", more_info_count)
m4.metric("Not Eligible", not_eligible_count)

# Common Service Center (CSC) Checklist Export Bar
exp_col1, exp_col2, exp_col3 = st.columns([2, 1, 1])
with exp_col1:
    st.markdown("### 📋 Government Scheme Recommendations")
with exp_col2:
    pdf_bytes = ExportService.generate_csc_checklist_pdf(st.session_state.profile, results)
    st.download_button(
        label="📄 Download CSC PDF Checklist",
        data=pdf_bytes,
        file_name="SchemeSathi_CSC_Checklist.pdf",
        mime="application/pdf",
        use_container_width=True,
        help="Printable document with required papers checklist to carry to nearest CSC / Seva Kendra"
    )
with exp_col3:
    txt_content = ExportService.generate_csc_checklist_text(st.session_state.profile, results)
    st.download_button(
        label="📋 Download Text Docket",
        data=txt_content,
        file_name="SchemeSathi_Verification_Docket.txt",
        mime="text/plain",
        use_container_width=True,
        help="Text checklist for offline viewing or mobile sharing"
    )

# Filter Tabs
tab_all, tab_likely, tab_possibly, tab_more_info, tab_not_eligible = st.tabs([
    f"All ({len(results)})",
    f"Likely Eligible ({likely_count})",
    f"Possibly Eligible ({possibly_count})",
    f"More Info Needed ({more_info_count})",
    f"Not Eligible ({not_eligible_count})"
])

def render_scheme_card(res):
    formatted = explanation_service.format_evaluation_details(res)
    badge_class = {
        EligibilityStatus.LIKELY_ELIGIBLE.value: "badge-likely",
        EligibilityStatus.POSSIBLY_ELIGIBLE.value: "badge-possibly",
        EligibilityStatus.MORE_INFORMATION_NEEDED.value: "badge-more-info",
        EligibilityStatus.NOT_ELIGIBLE.value: "badge-not-eligible",
    }.get(formatted["status"], "badge-category")

    st.markdown(f"""
    <div class="scheme-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div>
                <span class="badge badge-category">{formatted['category']}</span>
                <h3 style="margin: 6px 0 2px 0; color: #f8fafc;">{formatted['scheme_name']} ({formatted['short_name']})</h3>
            </div>
            <span class="badge {badge_class}">{formatted['status']}</span>
        </div>
        <p style="color: #cbd5e1; margin-bottom: 12px; font-size: 0.95rem;">{res.scheme.description}</p>
        <div style="background-color: #0b1120; border-left: 3px solid #3b82f6; padding: 10px 14px; margin-bottom: 14px; border-radius: 4px;">
            <strong style="color: #93c5fd;">🎁 Key Benefit:</strong> <span style="color: #e2e8f0;">{formatted['benefits']}</span>
        </div>
    """, unsafe_allow_html=True)

    c_left, c_right = st.columns([1.2, 1])
    with c_left:
        st.markdown("**Transparent Rule Evaluation:**")
        if formatted["matched"]:
            for item in formatted["matched"]:
                st.markdown(f'<div class="criterion-matched">{item}</div>', unsafe_allow_html=True)
        if formatted["unknown"]:
            for item in formatted["unknown"]:
                st.markdown(f'<div class="criterion-unknown">{item}</div>', unsafe_allow_html=True)
        if formatted["failed"]:
            for item in formatted["failed"]:
                st.markdown(f'<div class="criterion-failed">{item}</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown("**Required Documents:**")
        docs_html = "".join([f"<li>{doc}</li>" for doc in formatted['required_documents']])
        st.markdown(f"<ul style='font-size: 0.85rem; color: #94a3b8; margin: 4px 0 8px 16px; padding: 0;'>{docs_html}</ul>", unsafe_allow_html=True)
        st.markdown(f"**Application:** <span style='font-size: 0.85rem; color: #cbd5e1;'>{formatted['application_info']}</span>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="provenance-note">
            🏛️ <strong>Official Authority:</strong> {formatted['source_name']} &nbsp;|&nbsp; 
            🔗 <a href="{formatted['source_url']}" target="_blank" style="color: #60a5fa; text-decoration: none;">Official Portal</a> &nbsp;|&nbsp;
            📅 Verified: {res.scheme.last_verified}
        </div>
    </div>
    """, unsafe_allow_html=True)


with tab_all:
    for r in results:
        render_scheme_card(r)

with tab_likely:
    filtered = [r for r in results if r.status == EligibilityStatus.LIKELY_ELIGIBLE]
    if filtered:
        for r in filtered:
            render_scheme_card(r)
    else:
        st.info("No schemes currently marked as Likely Eligible based on current details.")

with tab_possibly:
    filtered = [r for r in results if r.status == EligibilityStatus.POSSIBLY_ELIGIBLE]
    if filtered:
        for r in filtered:
            render_scheme_card(r)
    else:
        st.info("No schemes currently marked as Possibly Eligible.")

with tab_more_info:
    filtered = [r for r in results if r.status == EligibilityStatus.MORE_INFORMATION_NEEDED]
    if filtered:
        for r in filtered:
            render_scheme_card(r)
    else:
        st.info("No schemes in this category.")

with tab_not_eligible:
    filtered = [r for r in results if r.status == EligibilityStatus.NOT_ELIGIBLE]
    if filtered:
        for r in filtered:
            render_scheme_card(r)
    else:
        st.info("No schemes marked as Not Eligible.")

st.markdown("---")
st.caption(explanation_service.get_legal_disclaimer())

