export async function sendMessage(message: string) {
  const response = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to connect to companion");
  }

  return response.json();
}

export async function sendVoice(duration = 5) {
  const response = await fetch("http://127.0.0.1:8000/voice", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      duration,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to connect to voice service");
  }

  return response.json();
}