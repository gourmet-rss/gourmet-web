"use client";

import { useState } from "react";

export default function Visualization() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button onClick={() => setOpen(!open)} className="btn">
        {open ? "Hide" : "Show"} embeddings visualisation
      </button>
      {open && (
        <iframe
          src="http://localhost:8000/visualization"
          className="w-[calc(100vw-40px)] h-[calc(100vh-40px)] fixed top-[40px] left-0 right-0 bg-white"
        />
      )}
    </>
  );
}
