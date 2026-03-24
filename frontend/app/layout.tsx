export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body style={{ fontFamily: "system-ui", margin: 0, padding: 24 }}>
        {children}
      </body>
    </html>
  );
}
