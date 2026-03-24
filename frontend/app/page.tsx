import Link from "next/link";

export default function Home() {
  return (
    <main style={{ maxWidth: 900, margin: "0 auto" }}>
      <h1>Salary Table Tool</h1>
      <p>ExcelテンプレDL → 編集 → Upload → Version管理 → Excel出力</p>
      <ul>
        <li>/loginログイン</Link></li>
        <li>/tableテーブル管理</Link></li>
      </ul>
    </main>
  );
}
