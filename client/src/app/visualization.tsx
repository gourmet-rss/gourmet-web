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
        <div className="fixed top-0 left-0 w-full h-full z-40 bg-white">
          <button
            onClick={() => setOpen(false)}
            className="btn btn-primary z-50 fixed top-12 left-8"
          >
            Close
          </button>
          <iframe
            src="http://localhost:8000/visualization"
            className="w-full h-full"
          />
        </div>
      )}
    </>
  );
}
