# AI & Vernacular Explanation Architecture — GRAMAVISE

## 1. Role of AI in GramaVise
In GramaVise, AI is **strictly an explainer and translator**, never a calculator or primary decision maker.

```text
┌───────────────────────────┐
│     User Input Form       │
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│  Deterministic Engines    │  <-- 100% Math & Rule Based
│ (Financial, Geo, Schemes) │
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│    Structured JSON Fact   │  <-- Ground Truth Context
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│    AI Explanation Layer   │  <-- Summarizes & Translates to Vernacular
│  (Mock / Gemini / Claude) │
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│ Vernacular Advisory Output│
└───────────────────────────┘
```

---

## 2. Guardrails & Non-Hallucination Constraints
1. **Strict Context Injection:** Prompts strictly forbid the LLM from fabricating financial values, interest rates, or government policies. All numbers mentioned in the advisory must originate from the input JSON.
2. **Pydantic Structured Output:** All LLM responses are parsed into typed Pydantic models (`AIExplanationResponse`).
3. **Mock Provider for Local Testing:** `MockAIProvider` ensures deterministic, zero-cost, offline-friendly testing without requiring external API keys during hackathon development.

---

## 3. Supported Vernacular Languages
* English (`en`)
* Hindi (`hi`)
* Marathi (`mr`)
* Bengali (`bn`)
* Telugu (`te`)
* Tamil (`ta`)
