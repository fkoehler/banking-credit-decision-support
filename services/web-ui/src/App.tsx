import { FormEvent, useMemo, useState } from "react";
import { assessCase, createCase, decideCase, type Credentials } from "./api";
import type { Assessment, CaseInput, CreditCase } from "./types";

const initialCase: CaseInput = {
  profession: "DENTIST",
  annualIncome: 185000,
  practiceRevenue: 620000,
  practiceAgeYears: 4,
  existingDebt: 80000,
  requestedCredit: 450000,
  equity: 100000,
  latePayments: 0,
};

const money = new Intl.NumberFormat("en-GB", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

function App() {
  const [role, setRole] = useState<"advisor" | "reviewer">("advisor");
  const [password, setPassword] = useState("advisor-demo");
  const [input, setInput] = useState(initialCase);
  const [creditCase, setCreditCase] = useState<CreditCase | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [decisionComment, setDecisionComment] = useState("Reviewed against the fictional policy and source data.");

  const credentials = useMemo<Credentials>(() => ({ username: role, password }), [role, password]);

  function switchRole(next: "advisor" | "reviewer") {
    setRole(next);
    setPassword(next === "advisor" ? "advisor-demo" : "reviewer-demo");
    setError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const created = await createCase(input, credentials);
      setCreditCase(created);
      setAssessment(await assessCase(created.id, credentials));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected error");
    } finally {
      setBusy(false);
    }
  }

  async function decide(decision: string) {
    if (!creditCase) return;
    setBusy(true);
    setError("");
    try {
      await decideCase(creditCase.id, decision, decisionComment, credentials);
      setCreditCase({ ...creditCase, status: decision });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-mark">BC</div>
        <div>
          <span className="eyebrow">REFERENCE PLATFORM</span>
          <h1>Banking Credit Decision Support</h1>
        </div>
        <div className="session">
          <label>
            Demo role
            <select value={role} onChange={(event) => switchRole(event.target.value as "advisor" | "reviewer")}>
              <option value="advisor">Advisor</option>
              <option value="reviewer">Risk reviewer</option>
            </select>
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
          </label>
        </div>
      </header>

      <div className="demo-banner">
        Synthetic demonstration · Not affiliated with a real bank · Human decision required
      </div>

      <main>
        <section className="intro">
          <span className="section-number">01</span>
          <div>
            <p className="eyebrow">PRACTICE FINANCING</p>
            <h2>Assess a fictional application</h2>
            <p>Combine a trained probability-of-default model with traceable policy retrieval.</p>
          </div>
        </section>

        <div className="workspace">
          <form className="panel application-panel" onSubmit={submit}>
            <div className="panel-heading">
              <h3>Application data</h3>
              <span className="status-dot">Synthetic</span>
            </div>
            <div className="form-grid">
              <Field label="Profession">
                <select value={input.profession} onChange={(event) => setInput({ ...input, profession: event.target.value })}>
                  <option value="PHYSICIAN">Physician</option>
                  <option value="DENTIST">Dentist</option>
                  <option value="PHARMACIST">Pharmacist</option>
                  <option value="THERAPIST">Therapist</option>
                </select>
              </Field>
              <NumberField label="Annual income" value={input.annualIncome} onChange={(value) => setInput({ ...input, annualIncome: value })} />
              <NumberField label="Practice revenue" value={input.practiceRevenue} onChange={(value) => setInput({ ...input, practiceRevenue: value })} />
              <NumberField label="Practice age (years)" value={input.practiceAgeYears} onChange={(value) => setInput({ ...input, practiceAgeYears: value })} />
              <NumberField label="Existing debt" value={input.existingDebt} onChange={(value) => setInput({ ...input, existingDebt: value })} />
              <NumberField label="Requested credit" value={input.requestedCredit} onChange={(value) => setInput({ ...input, requestedCredit: value })} />
              <NumberField label="Equity" value={input.equity} onChange={(value) => setInput({ ...input, equity: value })} />
              <NumberField label="Late payments" value={input.latePayments} onChange={(value) => setInput({ ...input, latePayments: value })} />
            </div>
            <div className="application-summary">
              <span>Requested</span><strong>{money.format(input.requestedCredit)}</strong>
              <span>Equity ratio</span><strong>{(input.equity / input.requestedCredit * 100).toFixed(1)}%</strong>
            </div>
            <button className="primary" disabled={busy}>{busy ? "Assessing…" : "Run assisted assessment"}</button>
            {error && <p className="error" role="alert">{error}</p>}
          </form>

          <section className="panel result-panel" aria-live="polite">
            <div className="panel-heading">
              <h3>Decision support</h3>
              <span className={`case-status ${creditCase ? "active" : ""}`}>{creditCase?.status ?? "Awaiting case"}</span>
            </div>
            {!assessment ? <EmptyState /> : <AssessmentResult assessment={assessment} />}
            {assessment && role === "reviewer" && (
              <div className="review-box">
                <p className="eyebrow">HUMAN REVIEW</p>
                <textarea value={decisionComment} onChange={(event) => setDecisionComment(event.target.value)} />
                <div className="decision-actions">
                  <button onClick={() => decide("APPROVED")} disabled={busy}>Approve</button>
                  <button onClick={() => decide("MORE_INFORMATION_REQUIRED")} disabled={busy}>Request information</button>
                  <button className="danger" onClick={() => decide("REJECTED")} disabled={busy}>Reject</button>
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="field"><span>{label}</span>{children}</label>;
}

function NumberField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return <Field label={label}><input type="number" min="0" value={value} onChange={(event) => onChange(Number(event.target.value))} /></Field>;
}

function EmptyState() {
  return <div className="empty-state"><div className="pulse-ring" /><h4>No assessment yet</h4><p>Enter a fictional case to see the model score, input factors and policy evidence.</p></div>;
}

function AssessmentResult({ assessment }: { assessment: Assessment }) {
  const degrees = Math.min(180, assessment.riskProbability * 600);
  return <div className="assessment">
    <div className="risk-overview">
      <div className="gauge" style={{ "--risk-angle": `${degrees}deg` } as React.CSSProperties}>
        <div><strong>{(assessment.riskProbability * 100).toFixed(1)}%</strong><span>estimated PD</span></div>
      </div>
      <div><p className="eyebrow">MODEL RESULT</p><h4>{assessment.riskBand} risk band</h4><small>{assessment.modelVersion}</small></div>
    </div>
    <div className="factor-columns">
      <FactorList title="Positive inputs" items={assessment.positiveFactors} kind="positive" />
      <FactorList title="Risk inputs" items={assessment.riskFactors} kind="risk" />
    </div>
    <div className="narrative"><div className="narrative-head"><h4>Assisted explanation</h4><span>{assessment.generationMode}</span></div><p>{assessment.summary}</p></div>
    <div className="sources"><h4>Policy evidence</h4>{assessment.citations.map((citation) => <article key={`${citation.documentId}-${citation.section}`}><div><strong>{citation.title}</strong><span>{citation.section}</span></div><code>{(citation.score * 100).toFixed(0)}% match</code></article>)}</div>
    <p className="model-note">Input factors are associations, not causal reasons. The model cannot approve or reject a case.</p>
  </div>;
}

function FactorList({ title, items, kind }: { title: string; items: string[]; kind: string }) {
  return <div><h4>{title}</h4><ul className={kind}>{items.map((item) => <li key={item}>{item}</li>)}</ul></div>;
}

export default App;

