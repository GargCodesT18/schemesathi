"""Export Service for generating CSC (Common Service Center) printable PDF checklists"""
from io import BytesIO
from typing import List
from fpdf import FPDF
from app.models.profile import CitizenProfile
from app.models.result import EligibilityStatus, SchemeEvaluationResult


class CSCReportPDF(FPDF):
    """Custom PDF layout for citizen scheme verification checklist."""

    def header(self):
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(24, 43, 73)
        self.cell(0, 9, "SchemeSathi - Government Scheme Verification Checklist", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, "Official Common Service Center (CSC) / Citizen Seva Kendra Application Docket", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, "SchemeSathi | Free & Open-Source Citizen Navigator | Page " + str(self.page_no()), align="C")


class ExportService:
    """Generates printable citizen artifacts for CSC / Seva Kendra visits."""

    @classmethod
    def generate_csc_checklist_pdf(
        cls,
        profile: CitizenProfile,
        results: List[SchemeEvaluationResult]
    ) -> bytes:
        """Generates a clean PDF document containing citizen details and document checklist."""
        pdf = CSCReportPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Section 1: Citizen Profile Details
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 7, "1. CITIZEN PROFILE SUMMARY", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(51, 65, 85)

        known = profile.get_known_fields()
        if not known:
            pdf.cell(0, 5, "No specific profile attributes registered.", new_x="LMARGIN", new_y="NEXT")
        else:
            col_width = 95
            items = list(known.items())
            for i in range(0, len(items), 2):
                k1, v1 = items[i]
                v1_str = f"Rs. {v1:,.0f}" if isinstance(v1, (int, float)) and "income" in k1 else str(v1)
                text1 = f"- {k1.replace('_', ' ').title()}: {v1_str}"
                
                if i + 1 < len(items):
                    k2, v2 = items[i + 1]
                    v2_str = f"Rs. {v2:,.0f}" if isinstance(v2, (int, float)) and "income" in k2 else str(v2)
                    text2 = f"- {k2.replace('_', ' ').title()}: {v2_str}"
                else:
                    text2 = ""

                pdf.cell(col_width, 5, text1)
                pdf.cell(col_width, 5, text2, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(4)

        # Section 2: Eligible & Recommended Schemes
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 7, "2. APPLICABLE SCHEMES & DOCUMENT CHECKLIST", new_x="LMARGIN", new_y="NEXT")

        # Focus on Likely and Possibly Eligible schemes
        applicable = [
            r for r in results
            if r.status in (EligibilityStatus.LIKELY_ELIGIBLE, EligibilityStatus.POSSIBLY_ELIGIBLE)
        ]

        if not applicable:
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 6, "No schemes currently identified as Likely or Possibly Eligible.", new_x="LMARGIN", new_y="NEXT")
        else:
            for idx, r in enumerate(applicable, 1):
                scheme = r.scheme
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(15, 23, 42)
                
                status_label = "[LIKELY ELIGIBLE]" if r.status == EligibilityStatus.LIKELY_ELIGIBLE else "[POSSIBLY ELIGIBLE]"
                pdf.cell(0, 6, f"{idx}. {scheme.name} ({scheme.short_name or ''})  --  {status_label}", new_x="LMARGIN", new_y="NEXT")

                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(71, 85, 105)
                pdf.cell(0, 5, f"   Sector: {scheme.category}  |  Authority: {scheme.source_name}", new_x="LMARGIN", new_y="NEXT")
                
                # Benefits
                pdf.set_font("Helvetica", "I", 8.5)
                pdf.set_text_color(30, 64, 175)
                clean_benefits = scheme.benefits.encode("latin-1", "replace").decode("latin-1")
                pdf.cell(0, 5, f"   Benefit: {clean_benefits}", new_x="LMARGIN", new_y="NEXT")

                # Required Documents checklist
                pdf.set_font("Helvetica", "B", 8.5)
                pdf.set_text_color(30, 41, 59)
                pdf.cell(0, 5, "   Required Documents Checklist for CSC Verification:", new_x="LMARGIN", new_y="NEXT")
                
                pdf.set_font("Helvetica", "", 8.5)
                pdf.set_text_color(51, 65, 85)
                for doc in scheme.required_documents:
                    clean_doc = doc.encode("latin-1", "replace").decode("latin-1")
                    pdf.cell(0, 4.5, f"      [  ]  {clean_doc}", new_x="LMARGIN", new_y="NEXT")

                # Where to apply
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(100, 116, 139)
                clean_app = scheme.application_information.encode("latin-1", "replace").decode("latin-1")
                pdf.cell(0, 4.5, f"   Application Path: {clean_app}", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 4.5, f"   Official Portal: {scheme.source_url}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(3)

        # Section 3: Official Guidance & CSC Advice
        pdf.ln(3)
        pdf.set_draw_color(226, 232, 240)
        pdf.set_fill_color(248, 250, 252)
        pdf.rect(10, pdf.get_y(), 190, 26, style="DF")
        
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(30, 41, 59)
        pdf.set_xy(12, pdf.get_y() + 2)
        pdf.cell(0, 4.5, "INSTRUCTIONS FOR CITIZEN AT COMMON SERVICE CENTER (CSC):", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(71, 85, 105)
        pdf.set_x(12)
        pdf.cell(0, 4, "1. Carry original and photocopies of each checked document above along with Aadhaar-linked mobile.", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(12)
        pdf.cell(0, 4, "2. Request the Village Level Entrepreneur (VLE) at the CSC to cross-verify eligibility on the official portal.", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(12)
        pdf.cell(0, 4, "3. Notice: SchemeSathi provides transparent guidance; final sanction rests solely with the statutory authority.", new_x="LMARGIN", new_y="NEXT")

        # Output bytes
        buf = BytesIO()
        pdf.output(buf)
        return buf.getvalue()

    @classmethod
    def generate_csc_checklist_text(
        cls,
        profile: CitizenProfile,
        results: List[SchemeEvaluationResult]
    ) -> str:
        """Generates plain text / markdown checklist for quick copying or offline reading."""
        lines = [
            "=" * 70,
            "SCHEMESATHI - COMMON SERVICE CENTER (CSC) VERIFICATION DOCKET",
            "=" * 70,
            "\n[1] CITIZEN PROFILE SUMMARY",
        ]
        known = profile.get_known_fields()
        if not known:
            lines.append("  No specific profile attributes provided.")
        else:
            for k, v in known.items():
                v_str = f"Rs. {v:,.0f}" if isinstance(v, (int, float)) and "income" in k else str(v)
                lines.append(f"  * {k.replace('_', ' ').title()}: {v_str}")

        lines.append("\n[2] APPLICABLE SCHEMES & REQUIRED DOCUMENT CHECKLIST")
        applicable = [
            r for r in results
            if r.status in (EligibilityStatus.LIKELY_ELIGIBLE, EligibilityStatus.POSSIBLY_ELIGIBLE)
        ]

        if not applicable:
            lines.append("  No schemes currently identified as Likely or Possibly Eligible.")
        else:
            for idx, r in enumerate(applicable, 1):
                s = r.scheme
                lines.append(f"\n{idx}. {s.name} ({s.short_name or ''}) [{r.status.value}]")
                lines.append(f"   Sector: {s.category} | Authority: {s.source_name}")
                lines.append(f"   Benefit: {s.benefits}")
                lines.append("   Documents Required:")
                for doc in s.required_documents:
                    lines.append(f"     [ ] {doc}")
                lines.append(f"   Application: {s.application_information}")
                lines.append(f"   Official Portal: {s.source_url}")

        lines.extend([
            "\n" + "-" * 70,
            "IMPORTANT CITIZEN NOTICE FOR CSC VISIT:",
            "Carry original identity papers and bank passbook linked with Aadhaar.",
            "SchemeSathi provides navigational assistance; statutory approval rests with the authority.",
            "=" * 70
        ])
        return "\n".join(lines)

