import axios from "axios";

export default function ClientPanel({ clientId }) {
const sendForceSync = async () => {
  console.log("Force Sync Clicked");

  try {
    const res = await axios.post(
      `http://localhost:5000/api/command/${clientId}`,
      { type: "FORCE_SYNC" }
    );

    console.log("Response:", res.data);
  } catch (err) {
    console.error("Error:", err);
  }
};

  return (
    <div style={{
      marginTop: "20px",
      padding: "15px",
      background: "#334155",
      borderRadius: "10px",
      color: "white"
    }}>
      <h3>Client: {clientId}</h3>
      <button
        onClick={sendForceSync}
        style={{
          padding: "10px",
          background: "#22c55e",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer"
        }}
      >
        Force Sync
      </button>
    </div>
  );
}
