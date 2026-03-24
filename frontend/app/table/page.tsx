"use client";
import { useEffect, useState } from "react";
import { apiFetch, API_BASE } from "../api";

type Version = { id:number; name:string; effective_date:string; currency:string; created_at:string };

export default function TablePage() {
  const [versions, setVersions] = useState<Version[]>([]);
  const [name, setName] = useState("2026.01 Initial");
  const [file, setFile] = useState<File|null>(null);
  const [msg, setMsg] = useState("");

  async function refresh() {
    const res = await apiFetch("/tables");
    if (!res.ok) { setMsg("failed to load"); return; }
    setVersions(await res.json());
  }

  useEffect(()=>{ refresh(); }, []);

  async function downloadTemplate() {
    const res = await apiFetch("/template/salary-table.xlsx");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "Salary_Table_Template.xlsx";
    a.click();
  }

  async function upload() {
    if (!file) { setMsg("choose file"); return; }
    setMsg("uploading...");
    const fd = new FormData();
    fd.append("file", file);
    const res = await apiFetch(`/tables/upload?name=${encodeURIComponent(name)}`, {
      method: "POST",
      body: fd
    });
    if (!res.ok) {
      const err = await res.json().catch(()=>({detail:"upload failed"}));
      setMsg(err.detail || "upload failed");
      return;
    }
    const data = await res.json();
    setMsg(`uploaded: version_id=${data.version_id}, rows=${data.rows}`);
    await refresh();
  }

  function exportXlsx(id:number) {
    window.open(`${API_BASE}/tables/${id}/export.xlsx`, "_blank");
  }

  return (
    <main style={{ maxWidth: 900 }}>
      <h2>テーブル管理</h2>

      <section style={{ display:"flex", gap: 12, alignItems:"center", flexWrap:"wrap" }}>
        <button onClick={downloadTemplate}>テンプレDL</button>
        <input value={name} onChange={e=>setName(e.target.value)} style={{ minWidth: 240 }}/>
        <input type="file" accept=".xlsx" onChange={e=>setFile(e.target.files?.[0]||null)} />
        <button onClick={upload}>Upload</button>
        <span style={{ color:"#555" }}>{msg}</span>
      </section>

      <hr style={{ margin: "16px 0" }} />

      <h3>保存済みバージョン</h3>
      <ul style={{ lineHeight: 1.8 }}>
        {versions.map(v=>(
          <li key={v.id}>
            <b>#{v.id}</b> {v.name} / effective: {v.effective_date} / {v.currency}
            {" "}
            <button onClick={()=>exportXlsx(v.id)}>Excel出力</button>
          </li>
        ))}
      </ul>

      <p style={{ fontSize: 12, color:"#777" }}>
        ※ Uploadは admin/editor のみ。viewerは閲覧・DLのみ（API側で制御）
      </p>
    </main>
  );
}
