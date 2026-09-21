export interface PinnedMemory {
  id: number;
  timestamp: string;
  content: string;
}

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

export async function getMemories(): Promise<PinnedMemory[]> {
  const response = await fetch("http://127.0.0.1:8000/memory");

  if (!response.ok) {
    throw new Error("Failed to load memories");
  }

  const data = await response.json();

  return data.memories;
}

export async function updateMemory(
  memoryId: number,
  content: string
): Promise<PinnedMemory> {
  const response = await fetch(
    `http://127.0.0.1:8000/memory/${memoryId}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to update memory");
  }

  const data = await response.json();

  return data.memory;
}

export async function deleteMemory(memoryId: number) {
  const response = await fetch(
    `http://127.0.0.1:8000/memory/${memoryId}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to delete memory");
  }

  return response.json();
}