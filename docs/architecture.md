# System Architecture — SchemeSathi

## 1. Architectural Philosophy: Neuro-Symbolic Separation

A core tenet of **SchemeSathi** is the strict boundary between statistical natural language understanding and deterministic software logic:

$$\text{Citizen Request} \xrightarrow{\text{LLM Language Layer}} \text{Structured Profile} \xrightarrow{\text{Deterministic Rule Engine}} \text{Auditable Results}$$

- **Large Language Models (LLM Layer)**: Responsible exclusively for parsing unconstrained conversational input, extracting entities (age, occupation, income, location), and normalizing colloquial phrasing. The LLM is **never** permitted to make the final eligibility determination.
- **Deterministic Python Engine (Symbolic Layer)**: Evaluates the verified profile against statutory scheme criteria using Boolean and relational algebra (`equals`, `less_than_or_equal`, `greater_than_or_equal`, `in`). Every evaluation yields an auditable evidence chain: `MATCHED (✓)`, `FAILED (✗)`, or `UNKNOWN (?)`.

---

## 2. Component Diagram

```mermaid
flowchart TD
    subgraph UI ["Presentation Layer (Streamlit)"]
        A["Citizen Web Interface\n(Dark Modern Theme)"]
        B["Sidebar Controls &\nSector Filters"]
        C["Interactive Profile Editor &\nMissing Info Prompts"]
    end

    subgraph Service ["Service Layer (Python)"]
        D["ProfileService\n(Extract & Merge)"]
        E["LLMService\n(Provider Abstraction)"]
        F["EligibilityEngine\n(Deterministic Rules)"]
        G["ExplanationService\n(Transparancy & Provenance)"]
        H["SchemeService\n(Navigator Orchestrator)"]
    end

    subgraph AI ["AI Provider Layer"]
        I["OpenRouterProvider\n(llama-3.1 / customizable)"]
        J["Future Local Provider\n(Ollama / ONNX / vLLM)"]
    end

    subgraph Data ["Data & Provenance"]
        K[("Curated Schemes Database\ndata/schemes.json")]
        L["Official Portals\n(pmkisan, nsap, pmay, etc.)"]
    end

    A -->|"Natural Language Query"| D
    D --> E
    E --> I
    I -.->|"Alternative / Future"| J
    E -->|"Validated JSON"| D
    D -->|"CitizenProfile Pydantic Object"| H
    H --> F
    H --> G
    F <--> K
    K <-->|"Statutory Rules & URLs"| L
    G -->|"Criterion Breakdown & Recommendations"| A
```

---

## 3. Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Citizen
    participant UI as Streamlit UI
    participant PS as ProfileService
    participant LLM as LLMService
    participant OR as OpenRouter API
    participant EE as EligibilityEngine
    participant DB as SchemeRepository
    participant EX as ExplanationService

    Citizen->>UI: Inputs "I am a 42yo farmer from Punjab earning 2L"
    UI->>PS: Process natural language input
    PS->>LLM: extract_profile(user_text)
    LLM->>OR: POST /chat/completions (Structured JSON prompt)
    OR-->>LLM: {"age": 42, "state": "Punjab", "occupation": "farmer", "annual_income": 200000}
    LLM-->>PS: Cleaned & validated dictionary
    PS-->>UI: CitizenProfile(Pydantic validated)
    UI->>EE: evaluate_all(schemes, profile)
    DB->>EE: Load curated schemes & statutory criteria
    EE-->>UI: List[SchemeEvaluationResult]
    UI->>EX: format_evaluation_details(results)
    EX-->>UI: Matched (✓), Failed (✗), Unknown (?), Follow-up prompt
    UI-->>Citizen: Renders cards, status badges, & official provenance links
```

---

## 4. Evaluation State Machine

```mermaid
stateDiagram-v2
    [*] --> EvaluatingRules
    
    EvaluatingRules --> NOT_ELIGIBLE: Any mandatory rule evaluated to False
    EvaluatingRules --> MORE_INFORMATION_NEEDED: All rules evaluated to UNKNOWN (profile empty)
    EvaluatingRules --> POSSIBLY_ELIGIBLE: Some rules Matched AND Some rules Unknown
    EvaluatingRules --> LIKELY_ELIGIBLE: All rules Matched (0 Failed, 0 Unknown)
    
    NOT_ELIGIBLE --> [*]
    MORE_INFORMATION_NEEDED --> CitizenFollowUp: Ask focused clarifying question
    POSSIBLY_ELIGIBLE --> CitizenFollowUp: Ask clarifying question for missing fields
    CitizenFollowUp --> EvaluatingRules: Incremental profile merge
    LIKELY_ELIGIBLE --> [*]: Display requirements & official application portal
```

---

## 5. Security and Privacy Principles

1. **Zero Data Retention**: SchemeSathi operates in-memory; user conversations and extracted citizen profiles are neither logged to persistent databases nor transmitted to third-party telemetry.
2. **Provider Agnostic**: OpenRouter is utilized exclusively through an abstract interface (`OpenRouterProvider`). Swapping to local or air-gapped inference requires zero modifications to business or presentation logic.
3. **Statutory Truth**: Scheme eligibility criteria and document lists are manually audited against official gazettes rather than dynamically hallucinated.

