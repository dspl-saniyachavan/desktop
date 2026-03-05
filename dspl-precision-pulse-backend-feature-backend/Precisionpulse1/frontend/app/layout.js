export const metadata = {
  title: "PrecisionPulse Dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html>
      <body style={{ margin: 0, fontFamily: "Arial" }}>
        {children}
      </body>
    </html>
  );
}
