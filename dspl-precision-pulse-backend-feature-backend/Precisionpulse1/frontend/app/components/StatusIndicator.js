export default function StatusIndicator({ status }) {
  const color = status === "Online" ? "limegreen" : "red";

  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: "8px",
      color: color
    }}>
      <div style={{
        width: "12px",
        height: "12px",
        borderRadius: "50%",
        background: color
      }} />
      {status}
    </div>
  );
}
