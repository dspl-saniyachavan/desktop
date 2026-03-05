"use client";


import { useEffect, useState } from "react";
import socket from "../lib/socket";
import TelemetryCard from "../app/components/TelemetryCard";
import StatusIndicator from "../app/components/StatusIndicator";
import ClientPanel from "../app/components/ClientPanel";

export default function Dashboard() {
  const [telemetry, setTelemetry] = useState(null);
  const [status, setStatus] = useState("Offline");
  const [clientId, setClientId] = useState("client-01");

  useEffect(() => {

    socket.on("connect", () => {
      setStatus("Online");
    });

    socket.on("disconnect", () => {
      setStatus("Offline");
    });

    socket.on("telemetry_update", (data) => {
      setTelemetry(data);
      setClientId(data.client_id);
    });

    socket.on("client_offline", (data) => {
      if (data.client_id === clientId) {
        setStatus("Offline");
      }
    });

    return () => {
      socket.off("telemetry_update");
      socket.off("client_offline");
    };

  }, [clientId]);

  return (
    <div style={{
      padding: "40px",
      background: "#0f172a",
      minHeight: "100vh",
      color: "white"
    }}>

      <h1>PrecisionPulse Live Dashboard</h1>

      <StatusIndicator status={status} />

      {telemetry && (
        <div style={{
          display: "flex",
          gap: "20px",
          marginTop: "30px"
        }}>
          <TelemetryCard
            title="Temperature"
            value={telemetry.temperature}
            unit="°C"
          />
          <TelemetryCard
            title="Humidity"
            value={telemetry.humidity}
            unit="%"
          />
          <TelemetryCard
            title="Flowrate"
            value={telemetry.flowrate}
            unit="L/min"
          />
        </div>
      )}

      <ClientPanel clientId={clientId} />

    </div>
  );
}
