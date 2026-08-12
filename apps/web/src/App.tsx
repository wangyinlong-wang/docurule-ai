import { ChangeEvent, DragEvent, FormEvent, useEffect, useRef, useState } from "react";
import { api } from "./lib/api";
import type { CaseRecord, CaseStatus, ExtractedField, ProviderStatus } from "./types";

const statusLabel: Record<CaseStatus, string> = {
  uploaded: "Uploaded",
  processing: "Processing",
  needs_review: "Needs review",
  approved: "Approved",
  rejected: "Rejected",
  failed: "Failed",
};

function App() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [current, setCurrent] = useState<CaseRecord | null>(null);
  const [provider, setProvider] = useState<ProviderStatus | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refreshCases = async () => {
    const items = await api.listCases();
    setCases(items);
    return items;
  };

  useEffect(() => {
    Promise.all([refreshCases(), api.getProvider()])
      .then(([, providerStatus]) => setProvider(providerStatus))
      .catch((reason: Error) => setError(reason.message));
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setCurrent(null);
      return;
    }
    let active = true;
    let timer: number | undefined;
    const load = async () => {
      try {
        const item = await api.getCase(selectedId);
        if (!active) return;
        setCurrent(item);
        setCases((existing) => [item, ...existing.filter((entry) => entry.id !== item.id)]);
        if (item.status === "uploaded" || item.status === "processing") {
          timer = window.setTimeout(load, 800);
        }
      } catch (reason) {
        if (active) setError((reason as Error).message);
      }
    };
    load();
    return () => {
      active = false;
      if (timer) window.clearTimeout(timer);
    };
  }, [selectedId]);

  const openCase = (item: CaseRecord) => {
    setSelectedId(item.id);
    setCurrent(item);
    setError("");
  };

  const createDemo = async () => {
    setBusy(true);
    setError("");
    try {
      openCase(await api.createDemo());
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const upload = async (name: string, files: File[]) => {
    setBusy(true);
    setError("");
    try {
      const item = await api.createCase(name, files);
      setShowUpload(false);
      openCase(item);
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const updateCurrent = (item: CaseRecord) => {
    setCurrent(item);
    setCases((existing) => [item, ...existing.filter((entry) => entry.id !== item.id)]);
  };

  return (
    <div className="app-shell">
      <Sidebar
        cases={cases}
        selectedId={selectedId}
        onSelect={openCase}
        onHome={() => setSelectedId(null)}
        onNew={() => setShowUpload(true)}
      />
      <main className="main-stage">
        <Topbar provider={provider} onNew={() => setShowUpload(true)} />
        {error && (
          <div className="error-banner">
            <span>!</span> {error}
            <button onClick={() => setError("")} aria-label="Dismiss error">×</button>
          </div>
        )}
        {current ? (
          <CaseWorkspace item={current} onChange={updateCurrent} />
        ) : (
          <Welcome onDemo={createDemo} onUpload={() => setShowUpload(true)} busy={busy} />
        )}
      </main>
      {showUpload && (
        <UploadDialog onClose={() => setShowUpload(false)} onSubmit={upload} busy={busy} />
      )}
    </div>
  );
}

function Sidebar({
  cases,
  selectedId,
  onSelect,
  onHome,
  onNew,
}: {
  cases: CaseRecord[];
  selectedId: string | null;
  onSelect: (item: CaseRecord) => void;
  onHome: () => void;
  onNew: () => void;
}) {
  return (
    <aside className="sidebar">
      <button className="brand" onClick={onHome}>
        <span className="brand-mark"><i /><i /><i /></span>
        <span><strong>DocuRule</strong><small>AI workspace</small></span>
      </button>
      <button className="new-button" onClick={onNew}><span>＋</span> New review</button>
      <nav className="primary-nav">
        <button className={!selectedId ? "active" : ""} onClick={onHome}><span>⌂</span> Overview</button>
      </nav>
      <div className="case-heading"><span>Recent reviews</span><span>{cases.length}</span></div>
      <div className="case-list">
        {cases.length === 0 && <p className="empty-list">Your reviews will appear here.</p>}
        {cases.slice(0, 12).map((item) => (
          <button
            className={`case-link ${selectedId === item.id ? "active" : ""}`}
            key={item.id}
            onClick={() => onSelect(item)}
          >
            <span className="case-icon">{item.documents.length || 0}</span>
            <span className="case-copy"><strong>{item.name}</strong><small>{statusLabel[item.status]}</small></span>
            <span className={`mini-dot ${item.status}`} />
          </button>
        ))}
      </div>
      <div className="sidebar-footer">
        <span className="local-dot" />
        <span><strong>Private by default</strong><small>Runs on your machine</small></span>
      </div>
    </aside>
  );
}

function Topbar({ provider, onNew }: { provider: ProviderStatus | null; onNew: () => void }) {
  return (
    <header className="topbar">
      <div><span className="eyebrow">DOCUMENT INTELLIGENCE</span></div>
      <div className="topbar-actions">
        <span className={`provider-pill ${provider?.available ? "online" : "fallback"}`}>
          <i /> {provider?.available ? provider.model : "Rules fallback"}
        </span>
        <a href="https://github.com/wangyinlong-wang/docurule-ai" target="_blank" rel="noreferrer" className="github-button" title="Star DocuRule on GitHub">☆ <span>Star on GitHub</span></a>
        <button className="mobile-new" onClick={onNew}>＋</button>
      </div>
    </header>
  );
}

function Welcome({ onDemo, onUpload, busy }: { onDemo: () => void; onUpload: () => void; busy: boolean }) {
  return (
    <div className="welcome">
      <section className="hero">
        <div className="hero-copy">
          <span className="hero-kicker"><i /> OPEN SOURCE · LOCAL FIRST</span>
          <h1>Turn documents into<br /><em>decisions you can trust.</em></h1>
          <p>Classify files, extract structured data, run cross-document checks, and keep a human in control—all with your own AI.</p>
          <div className="hero-actions">
            <button className="primary-button" onClick={onUpload}>Review documents <span>→</span></button>
            <button className="text-button" onClick={onDemo} disabled={busy}>{busy ? "Preparing demo…" : "Explore a 10-second demo"} <span>↗</span></button>
          </div>
          <div className="trust-row"><span>✓ No cloud required</span><span>✓ Ollama ready</span><span>✓ Evidence attached</span></div>
        </div>
        <WorkflowPreview />
      </section>
      <section className="how-it-works">
        <div className="section-title"><span>ONE REVIEW, END TO END</span><h2>From a messy folder to a clear answer</h2></div>
        <div className="steps">
          <article><span className="step-number">01</span><div className="step-icon">⇧</div><h3>Drop documents</h3><p>PDF, JPG, PNG, and text files. Mixed document sets are welcome.</p></article>
          <article><span className="step-number">02</span><div className="step-icon">✦</div><h3>Extract with evidence</h3><p>Every field carries a confidence score and its original source quote.</p></article>
          <article><span className="step-number">03</span><div className="step-icon">✓</div><h3>Validate & decide</h3><p>Cross-check names, dates, amounts, and your own business rules.</p></article>
        </div>
      </section>
    </div>
  );
}

function WorkflowPreview() {
  return (
    <div className="preview-wrap">
      <div className="preview-glow" />
      <div className="preview-card">
        <div className="preview-top"><span><i /> Claim review</span><small>2 documents</small></div>
        <div className="preview-files">
          <div><span className="file-icon coral">PDF</span><p><strong>medical-invoice.pdf</strong><small>Invoice · 98% confidence</small></p><b>✓</b></div>
          <div><span className="file-icon mint">IMG</span><p><strong>claim-form.png</strong><small>Claim form · 96% confidence</small></p><b>✓</b></div>
        </div>
        <div className="preview-rule"><span className="rule-check">✓</span><p><strong>Claim amount matches invoice</strong><small>Both documents show $3,258.67</small></p><span className="passed">PASSED</span></div>
        <div className="preview-rule warning"><span className="rule-check">!</span><p><strong>Official seal detected</strong><small>Manual confirmation requested</small></p><span className="review">REVIEW</span></div>
        <div className="preview-bottom"><span>4 / 5 checks passed</span><button>Review decision →</button></div>
      </div>
      <div className="floating-chip top"><span>✦</span><p><strong>AI extraction</strong><small>12 fields found</small></p></div>
      <div className="floating-chip bottom"><span>✓</span><p><strong>Evidence linked</strong><small>Every value traceable</small></p></div>
    </div>
  );
}

function CaseWorkspace({ item, onChange }: { item: CaseRecord; onChange: (item: CaseRecord) => void }) {
  const [savingKey, setSavingKey] = useState("");
  const processing = item.status === "uploaded" || item.status === "processing";
  const passed = item.validations.filter((result) => result.status === "passed").length;
  const flagged = item.validations.filter((result) => result.status !== "passed").length;

  const saveField = async (field: ExtractedField, rawValue: string) => {
    if (String(field.value ?? "") === rawValue) return;
    setSavingKey(field.key);
    try {
      onChange(await api.updateField(item.id, field.key, rawValue));
    } finally {
      setSavingKey("");
    }
  };

  const decide = async (decision: "approved" | "rejected") => onChange(await api.review(item.id, decision));

  if (processing) {
    return (
      <div className="processing-view">
        <div className="processing-orbit"><span>✦</span></div>
        <span className="hero-kicker"><i /> LOCAL PROCESSING</span>
        <h1>Reading your documents…</h1>
        <p>Classifying files, extracting fields, and running validation rules.</p>
        <div className="progress-track"><i style={{ width: `${Math.max(item.progress, 6)}%` }} /></div>
        <small>{item.progress}% complete · You can safely leave this review open</small>
      </div>
    );
  }

  return (
    <div className="workspace">
      <div className="workspace-header">
        <div><span className="breadcrumb">REVIEWS / {item.id.toUpperCase()}</span><h1>{item.name}</h1><p>Created {new Date(item.created_at).toLocaleString()}</p></div>
        <div className="header-controls"><StatusBadge status={item.status} /><a className="outline-button" href={`/api/v1/cases/${item.id}/export`}>Export JSON ↓</a></div>
      </div>
      <div className="metric-row">
        <Metric value={item.documents.length} label="Documents" note={`${item.documents.filter((doc) => doc.status === "processed").length} processed`} />
        <Metric value={item.fields.length} label="Fields extracted" note={`${item.fields.filter((field) => field.confidence >= .9).length} high confidence`} />
        <Metric value={passed} label="Checks passed" note={`${flagged} need attention`} />
        <Metric value={`${Math.round((item.fields.reduce((sum, field) => sum + field.confidence, 0) / Math.max(item.fields.length, 1)) * 100)}%`} label="Avg. confidence" note={item.metadata.engine || "processing engine"} />
      </div>
      <div className="review-grid">
        <section className="panel documents-panel">
          <div className="panel-title"><div><span>01</span><h2>Documents</h2></div><small>{item.documents.length} files</small></div>
          <div className="document-list">
            {item.documents.map((document, index) => (
              <a href={`/api/v1/cases/${item.id}/documents/${document.id}`} target="_blank" key={document.id} className={index === 0 ? "selected" : ""}>
                <span className={`file-icon ${index % 2 ? "mint" : "coral"}`}>{document.media_type.includes("pdf") ? "PDF" : document.media_type.includes("image") ? "IMG" : "TXT"}</span>
                <p><strong>{document.file_name}</strong><small>{document.kind_label} · {document.fields.length} fields</small></p><span>↗</span>
              </a>
            ))}
          </div>
          <div className="privacy-note"><span>⌾</span><p><strong>Documents stay local</strong><small>Files are stored only in your DocuRule data volume.</small></p></div>
        </section>

        <section className="panel fields-panel">
          <div className="panel-title"><div><span>02</span><h2>Extracted fields</h2></div><small>Click a value to edit</small></div>
          <div className="field-table">
            {item.fields.length === 0 && <div className="empty-fields">No structured fields were found. Connect a vision model for image-only documents.</div>}
            {item.fields.map((field) => {
              const source = item.documents.find((document) => document.id === field.source_document_id);
              return (
                <div className="field-row" key={field.key}>
                  <div className="field-label"><strong>{field.label}</strong><small>{source?.file_name || "Manual field"}</small></div>
                  <div className="field-value">
                    <input defaultValue={String(field.value ?? "")} onBlur={(event) => saveField(field, event.target.value)} aria-label={field.label} />
                    {savingKey === field.key && <small>Saving…</small>}
                    {field.source_quote && <span className="quote" title={field.source_quote}>“{field.source_quote}”</span>}
                  </div>
                  <Confidence value={field.confidence} reviewed={field.reviewed} />
                </div>
              );
            })}
          </div>
        </section>

        <section className="panel validation-panel">
          <div className="panel-title"><div><span>03</span><h2>Validation</h2></div><small>{passed}/{item.validations.length} passed</small></div>
          <div className="validation-list">
            {item.validations.map((result) => (
              <div className={`validation-item ${result.status}`} key={result.id}>
                <span className="validation-icon">{result.status === "passed" ? "✓" : result.status === "warning" ? "!" : "×"}</span>
                <p><strong>{result.title}</strong><small>{result.message}</small></p>
                <span className="validation-label">{result.status}</span>
              </div>
            ))}
          </div>
          <div className={`decision-box ${item.decision || ""}`}>
            {item.decision ? (
              <><span className="decision-seal">{item.decision === "approved" ? "✓" : "×"}</span><div><strong>Review {item.decision}</strong><small>The decision is stored in the exportable audit record.</small></div></>
            ) : (
              <><div><strong>Human decision required</strong><small>Review evidence and resolve warnings before completing this case.</small></div><div className="decision-actions"><button onClick={() => decide("rejected")}>Reject</button><button className="approve" onClick={() => decide("approved")}>Approve case ✓</button></div></>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

function Metric({ value, label, note }: { value: string | number; label: string; note: string }) {
  return <div className="metric"><span>{value}</span><div><strong>{label}</strong><small>{note}</small></div></div>;
}

function StatusBadge({ status }: { status: CaseStatus }) {
  return <span className={`status-badge ${status}`}><i /> {statusLabel[status]}</span>;
}

function Confidence({ value, reviewed }: { value: number; reviewed: boolean }) {
  const percent = Math.round(value * 100);
  const level = percent >= 90 ? "high" : percent >= 75 ? "medium" : "low";
  return <div className={`confidence ${level}`}><span>{reviewed ? "✓" : `${percent}%`}</span><i><b style={{ width: `${percent}%` }} /></i></div>;
}

function UploadDialog({ onClose, onSubmit, busy }: { onClose: () => void; onSubmit: (name: string, files: File[]) => void; busy: boolean }) {
  const [files, setFiles] = useState<File[]>([]);
  const [name, setName] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const addFiles = (incoming: FileList | null) => incoming && setFiles((existing) => [...existing, ...Array.from(incoming)]);
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (files.length) onSubmit(name || `Document review · ${new Date().toLocaleDateString()}`, files);
  };
  const drop = (event: DragEvent) => { event.preventDefault(); addFiles(event.dataTransfer.files); };
  return (
    <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <form className="upload-dialog" onSubmit={submit}>
        <button type="button" className="close-button" onClick={onClose}>×</button>
        <span className="hero-kicker"><i /> NEW REVIEW</span>
        <h2>Bring your document set</h2>
        <p>Upload related files together so DocuRule can validate data across them.</p>
        <label className="name-field">Review name<input value={name} onChange={(event: ChangeEvent<HTMLInputElement>) => setName(event.target.value)} placeholder="e.g. Claim CLM-2026-0812" /></label>
        <div className="dropzone" onDragOver={(event) => event.preventDefault()} onDrop={drop} onClick={() => inputRef.current?.click()}>
          <span className="upload-symbol">⇧</span><strong>Drop PDF, PNG, JPG or text files</strong><small>or click to browse · up to 20 MB each</small>
          <input ref={inputRef} type="file" multiple accept=".pdf,.png,.jpg,.jpeg,.txt,.md" onChange={(event) => addFiles(event.target.files)} hidden />
        </div>
        {files.length > 0 && <div className="upload-files">{files.map((file, index) => <div key={`${file.name}-${index}`}><span>{file.name}</span><small>{(file.size / 1024).toFixed(1)} KB</small><button type="button" onClick={() => setFiles(files.filter((_, itemIndex) => itemIndex !== index))}>×</button></div>)}</div>}
        <div className="modal-actions"><button type="button" onClick={onClose}>Cancel</button><button className="primary-button" disabled={!files.length || busy}>{busy ? "Uploading…" : `Start review${files.length ? ` (${files.length})` : ""}`} <span>→</span></button></div>
      </form>
    </div>
  );
}

export default App;
