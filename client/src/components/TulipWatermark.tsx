import React from "react";

export default function TulipWatermark() {
  return (
    <div className="tulip-watermark">
      <svg
        width="240"
        height="280"
        viewBox="0 0 100 120"
        fill="none"
        stroke="currentColor"
      >
        <path
          d="M50 15 C30 15 15 35 15 60 C15 85 40 95 50 105 C60 95 85 85 85 60 C85 35 70 15 50 15Z"
          strokeWidth="1"
        />

        <path
          d="M50 15 C44 40 40 70 50 105"
          strokeWidth="0.6"
        />

        <path
          d="M50 15 C56 40 60 70 50 105"
          strokeWidth="0.6"
        />

        <path
          d="M50 105 V120"
          strokeWidth="1.5"
        />
      </svg>
    </div>
  );
}