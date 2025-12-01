import React, { useState } from "react";

const VALID_PASSWORD = "MINARIS";

const PasswordGate: React.FC<{ onUnlock: () => void }> = ({ onUnlock }) => {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === VALID_PASSWORD) {
      localStorage.setItem("minaris_access", "allowed");
      onUnlock();
    } else {
      setError("Incorrect password");
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "#0d1117",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        zIndex: 9999,
      }}
    >
      <h1 style={{ color: "white", marginBottom: "20px", fontSize: "28px" }}>
        Minaris AI Access
      </h1>

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", width: "260px" }}
      >
        <input
          type="password"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{
            padding: "10px",
            borderRadius: "8px",
            fontSize: "16px",
            marginBottom: "10px",
            border: "1px solid #333",
            background: "#161b22",
            color: "white",
          }}
        />

        <button
          type="submit"
          style={{
            padding: "10px",
            borderRadius: "8px",
            background: "#007bff",
            color: "white",
            fontSize: "16px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          Unlock
        </button>

        {error && (
          <p style={{ color: "red", marginTop: "10px", textAlign: "center" }}>
            {error}
          </p>
        )}
      </form>
    </div>
  );
};

export default PasswordGate;
