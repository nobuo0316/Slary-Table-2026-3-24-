"use client";
import { useState } from "react";
import { API_BASE } from "../api";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [msg, setMsg] = useState("");

  async function login() {
    setMsg("logging in...");
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      setMsg("login failed");
      return;
    }
    const data = await res.json();
    localStorage.setItem("token", data.token);
    localStorage.setItem("role", data.role);
    setMsg(`ok (${data.role})`);
  }

  return (
    <main style={{ maxWidth: 520 }}>
      <h2>ログイン</h2>
      <div style={{ display: "grid", gap: 8 }}>
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
        <input value={password} onChange={e=>setPassword(e.target.value)} placeholder="password" type="password"/>
        <button onClick={login}>Login</button>
        <div style={{ color: "#555" }}>{msg}</div>
        <div style={{ fontSize: 12, color: "#777" }}>
          初期ユーザー: admin@example.com / admin123 (admin)<br/>
          editor@example.com / editor123 (editor)<br/>
          viewer@example.com / viewer123 (viewer)
        </div>
      </div>
    </main>
  );
}
