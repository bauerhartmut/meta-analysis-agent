"""Minimal local review workflow for verification records.

Run:
    python -m research_agent.verification.review_server \
        --state public_benchmark/evaluation/verification_pilot/audit.json

The server binds to 127.0.0.1 by default.  It has no authentication and must
not be exposed on a network interface.
"""

from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse

from .store import VerificationStore
from .workflow import finalize_after_review

_CSS = """
body{font-family:system-ui,Segoe UI,sans-serif;margin:24px;color:#1f2933;background:#f7f8fa}
h1{margin:0 0 4px} .muted{color:#5f6b7a;font-size:13px}
.summary{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}
.card{background:#fff;border:1px solid #d9dee6;border-radius:8px;padding:12px 16px;min-width:120px}
.card b{display:block;font-size:24px} .pending{border-left:5px solid #b7791f}
.verified{border-left:5px solid #2f855a} .rejected{border-left:5px solid #c53030}
.record{background:#fff;border:1px solid #d9dee6;border-radius:8px;margin:14px 0;padding:12px 16px}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:13px}
th,td{border-bottom:1px solid #e4e8ee;padding:6px;text-align:left;vertical-align:top}
th{background:#f1f4f8}.status{font-weight:600}.bad{color:#9b2c2c}.ok{color:#276749}
pre{white-space:pre-wrap;background:#f8fafc;border:1px solid #e2e8f0;padding:8px;max-height:160px;overflow:auto}
input,textarea,button{font:inherit;margin:2px 0;padding:4px}
button{cursor:pointer}.actions{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
small{color:#5f6b7a}.evidence{max-width:420px}
"""


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _short(value: Any, limit: int = 72) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[:limit - 1] + "..."


def _evidence_select(record: Dict[str, Any], name: str,
                     current: str) -> str:
    items = [
        (str(evidence_id), evidence)
        for evidence_id, evidence in (record.get("evidence") or {}).items()
        if str((evidence or {}).get("field") or "") == name
    ]
    if not items:
        return ('<span class="muted">keine Evidenz</span>'
                '<input type="hidden" name="evidence_id" value="">')
    options = []
    for evidence_id, evidence in items:
        label = " | ".join(part for part in (
            str(evidence.get("table_id") or ""),
            _short(evidence.get("row_label")),
            _short(evidence.get("column_label")),
            _short(evidence.get("raw_cell")),
        ) if part)
        selected = " selected" if evidence_id == current else ""
        options.append(
            f'<option value="{_e(evidence_id)}"{selected}>{_e(label)}</option>'
        )
    if current and current not in {item[0] for item in items}:
        options.insert(0, f'<option value="{_e(current)}" selected>'
                           f'{_e(_short(current))} (nicht gespeichert)</option>')
    return ('<select name="evidence_id">'
            + "".join(options) + "</select>")


def _field_row(record_id: str, name: str, field: Dict[str, Any],
               record: Dict[str, Any]) -> str:
    evidence_id = str(field.get("evidence_id") or "")
    status = str(field.get("status") or "")
    cls = "ok" if status == "verified" else "bad"
    return f"""
    <tr>
      <td><b>{_e(name)}</b><br><small>{_e(field.get('rule'))}</small></td>
      <td>{_e(field.get('value_a'))}</td>
      <td>{_e(field.get('value_b'))}</td>
      <td class="{cls}">{_e(status)}<br><small>{_e(field.get('comparison'))}</small></td>
      <td class="evidence"><small>{_e(field.get('note'))}</small></td>
      <td>
        <form method="post" action="/decision" class="actions">
          <input type="hidden" name="record_id" value="{_e(record_id)}">
          <input type="hidden" name="field" value="{_e(name)}">
          {_evidence_select(record, name, evidence_id)}
          <input name="reviewer" placeholder="Pruefer" required size="10">
          <input name="value" placeholder="Wert" size="8">
          <input name="note" placeholder="Begruendung" size="18">
          <button name="action" value="confirm">bestaetigen</button>
          <button name="action" value="correct">korrigieren</button>
          <button name="action" value="not_reported">nicht berichtet</button>
          <button name="action" value="unclear">unklar</button>
        </form>
      </td>
    </tr>"""


def render(store: VerificationStore) -> str:
    summary = store.summary()
    cards = "".join(
        f'<div class="card"><b>{_e(value)}</b>{_e(key)}</div>'
        for key, value in summary.items()
    )
    records: List[str] = []
    for record_id, record in sorted(store.state["records"].items()):
        status = str(record.get("status") or "")
        fields = record.get("fields") or {}
        rows = "".join(_field_row(record_id, name, field, record)
                       for name, field in sorted(fields.items()))
        validations = "".join(
            f"<li><b>{_e(item.get('severity'))}</b> {_e(item.get('rule'))}: "
            f"{_e(item.get('message'))}</li>"
            for item in record.get("validations") or []
        ) or "<li>keine</li>"
        decisions = "".join(
            f"<li>{_e(d.get('created_at'))} {_e(d.get('reviewer'))}: "
            f"{_e(d.get('field'))} {_e(d.get('action'))} "
            f"(alt: {_e((d.get('old') or {}).get('final_value'))}, "
            f"neu: {_e((d.get('new') or {}).get('final_value'))})</li>"
            for d in record.get("decisions") or []
        ) or "<li>keine</li>"
        evidence_rows = []
        for field_name, field in sorted(fields.items()):
            ev = (record.get("evidence") or {}).get(field.get("evidence_id") or "")
            if not ev:
                continue
            evidence_rows.append(
                f"<tr><td>{_e(field_name)}</td>"
                f"<td>{_e(ev.get('table_id'))}<br>{_e(ev.get('row_label'))}</td>"
                f"<td>{_e(ev.get('column_label'))}</td>"
                f"<td><code>{_e(ev.get('raw_cell'))}</code></td>"
                f"<td>{_e(ev.get('line_start'))}</td></tr>"
            )
        evidence_table = (
            "<table><tr><th>Feld</th><th>Tabelle/Zeile</th><th>Spalte</th>"
            "<th>Originalzelle</th><th>Zeile</th></tr>"
            + "".join(evidence_rows) + "</table>"
            if evidence_rows else "<p class='muted'>Keine Evidenzzelle vorhanden.</p>"
        )
        records.append(f"""
        <section class="record {_e(status)}">
          <h2>{_e(record_id)} <span class="status">{_e(status)}</span></h2>
          <p class="muted">{_e(record.get('status_reason'))} | Dokument:
             {_e(record.get('document_id'))} | Hash:
             {_e(record.get('document_hash'))[:16]}...</p>
          <details><summary>Originalbeleg und Tabellenstruktur</summary>
            {evidence_table}
          </details>
          <table>
            <tr><th>Feld</th><th>Pipeline A</th><th>Pipeline B</th>
                <th>Status</th><th>Hinweis</th><th>Pruefentscheidung</th></tr>
            {rows}
          </table>
          <details><summary>Plausibilitaet und Audit</summary>
            <p><b>Warnungen/Fehler</b></p><ul>{validations}</ul>
            <p><b>Entscheidungen</b></p><ul>{decisions}</ul>
          </details>
          <form method="post" action="/decision" class="actions">
            <input type="hidden" name="record_id" value="{_e(record_id)}">
            <input type="hidden" name="field" value="">
            <input name="reviewer" placeholder="Pruefer" required size="10">
            <input name="note" placeholder="Grund fuer Record-Ablehnung" size="28">
            <button name="action" value="reject">Record ablehnen</button>
          </form>
        </section>""")
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
    <title>Record-Verifikation</title><style>{_CSS}</style></head><body>
    <h1>Record-Verifikation</h1>
    <p class="muted">Originalzelle, zwei getrennte Lesungen, Status und Audit.
    Aenderungen werden nie still ueberschrieben.</p>
    <div class="summary">{cards}</div>
    {''.join(records)}
    </body></html>"""


class ReviewHandler(BaseHTTPRequestHandler):
    store: VerificationStore

    def do_GET(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/":
            self.send_error(404)
            return
        body = render(self.store).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/decision":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        def one(key: str) -> str:
            values = form.get(key) or [""]
            return str(values[0])
        record_id = one("record_id")
        field = one("field")
        action = one("action")
        reviewer = one("reviewer").strip()
        note = one("note")
        try:
            if action == "reject":
                self.store.apply_decision(record_id, field or "record", "reject",
                                          reviewer=reviewer, note=note)
            else:
                if not field:
                    raise ValueError("Feld fehlt.")
                value = one("value")
                self.store.apply_decision(
                    record_id, field, action,
                    value=value if value != "" else None,
                    reviewer=reviewer, note=note, evidence_id=one("evidence_id"))
                finalize_after_review(self.store, record_id, reviewer)
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        except Exception as exc:  # keep the local workflow usable on input errors
            body = f"<p>Entscheidung nicht gespeichert: {_e(exc)}</p><p><a href='/'>zurueck</a></p>".encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True,
                        help="Pfad zur audit.json des Verifikationslaufs")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    store = VerificationStore(args.state)
    ReviewHandler.store = store
    server = ThreadingHTTPServer((args.host, args.port), ReviewHandler)
    print(f"Review: http://{args.host}:{args.port}/  ({len(store.state['records'])} Records)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
