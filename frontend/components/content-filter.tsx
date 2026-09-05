"use client";

import { FormEvent, useEffect, useState } from "react";
import { Check, CircleHelp, Edit2, Plus, Power, Trash2, X } from "lucide-react";

type MatchType = "contains" | "startsWith" | "exact";
type ActionType = "highlight" | "tooltip";
type Rule = {
  id: number; keyword: string; match_type: MatchType; action_type: ActionType;
  color: string | null; label: string | null; priority: number; enabled: boolean; case_sensitive: boolean;
};
type Match = { rule_id: number; keyword: string; action_type: ActionType; color: string | null; label: string | null; priority: number };
type Result = { segments: { text: string; matches: Match[] }[]; match_count: number; matched_rule_count: number };
type FormState = Omit<Rule, "id">;
type ApiStatus = "checking" | "connected" | "unavailable";

const emptyForm: FormState = {
  keyword: "", match_type: "contains", action_type: "highlight", color: "#fde68a",
  label: "", priority: 0, enabled: true, case_sensitive: false,
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = Array.isArray(data.detail) ? data.detail.map((item: { msg: string }) => item.msg).join(", ") : data.detail;
    throw new Error(detail || "Request failed");
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export default function ContentFilter() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [text, setText] = useState("The meeting with the finance team is tomorrow. The deadline is urgent.");
  const [result, setResult] = useState<Result | null>(null);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");

  const loadRules = async () => {
    try { setRules(await request<Rule[]>("/rules")); }
    catch (error) { setMessage((error as Error).message); }
  };
  useEffect(() => { void loadRules(); }, []);
  useEffect(() => {
    let active = true;
    const checkApi = async () => {
      try {
        const health = await request<{ status: string; database: string }>("/health");
        if (active) setApiStatus(health.status === "ok" && health.database === "ok" ? "connected" : "unavailable");
      } catch {
        if (active) setApiStatus("unavailable");
      }
    };
    void checkApi();
    const interval = window.setInterval(checkApi, 30_000);
    return () => { active = false; window.clearInterval(interval); };
  }, []);
  useEffect(() => {
    if (!open) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [open]);

  function newRule() { setEditingId(null); setForm(emptyForm); setOpen(true); }
  function editRule(rule: Rule) {
    const { id, ...values } = rule;
    setEditingId(id); setForm(values); setOpen(true);
  }
  function update<K extends keyof FormState>(key: K, value: FormState[K]) { setForm(current => ({ ...current, [key]: value })); }

  async function saveRule(event: FormEvent) {
    event.preventDefault(); setLoading(true); setMessage("");
    try {
      const body = { ...form, color: form.action_type === "highlight" ? form.color : null, label: form.action_type === "tooltip" ? form.label : null };
      await request(editingId ? `/rules/${editingId}` : "/rules", { method: editingId ? "PUT" : "POST", body: JSON.stringify(body) });
      setOpen(false); await loadRules();
    } catch (error) { setMessage((error as Error).message); }
    finally { setLoading(false); }
  }

  async function toggle(rule: Rule) {
    setMessage("");
    try {
      await request(`/rules/${rule.id}`, { method: "PUT", body: JSON.stringify({ enabled: !rule.enabled }) });
      await loadRules();
    } catch (error) {
      setMessage((error as Error).message);
    }
  }
  async function remove(rule: Rule) {
    if (!window.confirm(`Delete “${rule.keyword}”?`)) return;
    setMessage("");
    try {
      await request(`/rules/${rule.id}`, { method: "DELETE" });
      await loadRules();
      setResult(null);
    } catch (error) {
      setMessage((error as Error).message);
    }
  }
  async function processText(event: FormEvent) {
    event.preventDefault(); if (!text.trim()) return;
    setLoading(true); setMessage("");
    try { setResult(await request<Result>("/process", { method: "POST", body: JSON.stringify({ text }) })); }
    catch (error) { setMessage((error as Error).message); }
    finally { setLoading(false); }
  }

  return (
    <>
      <header className="site-header">
        <div className="container header-inner"><div className="brand"><span>CF</span> Content Filter</div><div className={`api-status ${apiStatus}`}><i /> API {apiStatus}</div></div>
      </header>
      <main className="container">
        <div className="page-title"><div><h1>Rule-based content filter</h1><p>Create rules and use them to mark important parts of your text.</p></div></div>
        {message && <div className="alert" role="alert" aria-live="polite"><CircleHelp size={16} />{message}<button type="button" aria-label="Dismiss message" onClick={() => setMessage("")}><X size={14} /></button></div>}

        <div className="grid">
          <section className="card rules-card">
            <div className="card-header"><div><h2>Rules</h2><p>{rules.filter(rule => rule.enabled).length} active of {rules.length}</p></div><button type="button" className="button" onClick={newRule}><Plus size={15} /> Add rule</button></div>
            <div className="rule-list">
              {!rules.length && <div className="empty"><p>No rules yet</p><span>Add a rule to start filtering text.</span></div>}
              {rules.map(rule => <div className={`rule ${rule.enabled ? "" : "muted"}`} key={rule.id}>
                <div className="rule-main"><span className="swatch" style={{ background: rule.color || "#18181b" }} /><div><strong>{rule.keyword}</strong><small>{rule.match_type === "startsWith" ? "starts with" : rule.match_type} · {rule.action_type}</small></div></div>
                <div className="row-actions"><button type="button" aria-label={`${rule.enabled ? "Disable" : "Enable"} ${rule.keyword}`} title={rule.enabled ? "Disable" : "Enable"} onClick={() => void toggle(rule)} className={rule.enabled ? "enabled" : ""}><Power size={15} /></button><button type="button" aria-label={`Edit ${rule.keyword}`} title="Edit" onClick={() => editRule(rule)}><Edit2 size={15} /></button><button type="button" aria-label={`Delete ${rule.keyword}`} title="Delete" onClick={() => void remove(rule)}><Trash2 size={15} /></button></div>
              </div>)}
            </div>
          </section>

          <div className="right-column">
            <section className="card">
              <div className="card-header"><div><h2>Text input</h2><p>Enter the content you want to check.</p></div></div>
              <form onSubmit={processText} className="content-form"><textarea value={text} onChange={event => setText(event.target.value)} maxLength={100000} placeholder="Paste your text here..." /><div className="form-footer"><span>{text.length.toLocaleString()} characters</span><button className="button primary" disabled={loading || !text.trim()}>{loading ? "Processing..." : "Process text"}</button></div></form>
            </section>
            <section className="card">
              <div className="card-header"><div><h2>Result</h2><p>{result ? `${result.match_count} matches from ${result.matched_rule_count} rules` : "Processed text appears here."}</p></div></div>
              <div className={`result ${result ? "" : "result-empty"}`} aria-live="polite">
                {!result ? "No result yet." : result.segments.map((segment, index) => <Segment key={index} text={segment.text} matches={segment.matches} />)}
              </div>
            </section>
          </div>
        </div>
      </main>

      {open && <div className="dialog-backdrop" onMouseDown={event => { if (event.currentTarget === event.target) setOpen(false); }}>
        <div className="dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title">
          <div className="dialog-header"><div><h2 id="dialog-title">{editingId ? "Edit rule" : "Add rule"}</h2><p>Choose what to match and how it should appear.</p></div><button type="button" className="icon-button" aria-label="Close dialog" onClick={() => setOpen(false)}><X size={17} /></button></div>
          <form onSubmit={saveRule}>
            <Field label="Keyword or phrase"><input required maxLength={255} value={form.keyword} onChange={event => update("keyword", event.target.value)} placeholder="e.g. urgent" autoFocus /></Field>
            <div className="two-columns"><Field label="Match type"><select value={form.match_type} onChange={event => update("match_type", event.target.value as MatchType)}><option value="contains">Contains</option><option value="startsWith">Starts with</option><option value="exact">Exact match</option></select></Field><Field label="Action"><select value={form.action_type} onChange={event => update("action_type", event.target.value as ActionType)}><option value="highlight">Highlight</option><option value="tooltip">Tooltip</option></select></Field></div>
            {form.action_type === "highlight" ? <Field label="Highlight color"><div className="color-input"><input type="color" value={form.color || "#fde68a"} onChange={event => update("color", event.target.value)} /><input pattern="#[0-9a-fA-F]{6}" value={form.color || ""} onChange={event => update("color", event.target.value)} /></div></Field> : <Field label="Tooltip label"><input maxLength={100} value={form.label || ""} onChange={event => update("label", event.target.value)} placeholder="e.g. IMPORTANT" /></Field>}
            <div className="two-columns"><Field label="Priority (0–100)"><input type="number" min="0" max="100" value={form.priority} onChange={event => update("priority", Number(event.target.value))} /></Field><label className="checkbox"><input type="checkbox" checked={form.case_sensitive} onChange={event => update("case_sensitive", event.target.checked)} /><span><Check size={12} /></span>Case sensitive</label></div>
            <div className="dialog-footer"><button type="button" className="button secondary" onClick={() => setOpen(false)}>Cancel</button><button className="button primary" disabled={loading}>{editingId ? "Save changes" : "Create rule"}</button></div>
          </form>
        </div>
      </div>}
    </>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) { return <label className="field"><span>{label}</span>{children}</label>; }
function Segment({ text, matches }: { text: string; matches: Match[] }) {
  if (!matches.length) return text;
  const highlights = matches.filter(match => match.action_type === "highlight");
  const labels = matches.filter(match => match.action_type === "tooltip").map(match => match.label).filter(Boolean);
  const colors = highlights.map(match => match.color).filter((color): color is string => Boolean(color));
  const background = colors.length < 2
    ? colors[0] || "transparent"
    : `linear-gradient(to bottom, ${colors.map((color, index) => `${color} ${index * 100 / colors.length}% ${(index + 1) * 100 / colors.length}%`).join(", ")})`;
  const description = [...highlights.map(match => `highlighted by ${match.keyword}`), ...labels.map(label => `tooltip ${label}`)].join(", ");
  return <mark className={labels.length ? "has-tooltip" : ""} style={{ background, borderBottomColor: labels.length ? "#18181b" : "transparent" }} tabIndex={labels.length ? 0 : undefined} aria-label={`${text}: ${description}`}>{text}{labels.length > 0 && <span className="tooltip" role="tooltip">{labels.join(" · ")}</span>}</mark>;
}
