export default function TelemetryCard({ title, value, unit }) {
  return (
    <div style={{
      background: "#1e293b",
      padding: "20px",
      borderRadius: "10px",
      color: "white",
      width: "200px",
      textAlign: "center"
    }}>
      <h3>{title}</h3>
      <h1>{value} {unit}</h1>
    </div>
  );
}
