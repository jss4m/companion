import React from "react";

interface TulipIconProps {
  className?: string;
}

export default function TulipIcon({
  className = "",
}: TulipIconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 3C9.2 3 7 5.2 7 9.2C7 13.2 10.2 14.8 12 16C13.8 14.8 17 13.2 17 9.2C17 5.2 14.8 3 12 3Z" />
      <path d="M12 3C11 6.2 10 10.2 12 16" opacity="0.5" />
      <path d="M12 3C13 6.2 14 10.2 12 16" opacity="0.5" />
      <path d="M12 16V21" />
    </svg>
  );
}