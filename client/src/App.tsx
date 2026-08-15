import { useState } from "react";
import "./App.css";
import type { ChatMessage } from "./types";
import { sendMessage } from "./api";
import TulipIcon from "./components/TulipIcon";
import TulipWatermark from "./components/TulipWatermark";

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      sender: "assistant",
      text: "Hello. I'm here.",
      timestamp: Date.now(),
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      sender: "user",
      text: input,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendMessage(userMessage.text);

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        sender: "assistant",
        text: data.reply,
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          sender: "assistant",
          text: "Connection error.",
          timestamp: Date.now(),
        },
      ]);
    }

    setLoading(false);
  }

  return (
    <div className="app">
      <TulipWatermark />
      <div className="chat-container">

        <header className="header">
          <h2>Personal Companion</h2>
          <p>Always present • Quiet reflection</p>
        </header>

        <div className="messages">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-row ${message.sender}`}
            >
              {message.sender === "assistant" && (
                <div className="assistant-avatar">
                  <TulipIcon className="tulip-icon" />
                </div>
              )}

              <div className="message">
                <strong>
                  {message.sender === "user"
                    ? "You"
                    : "Companion"}
                </strong>

                <p>{message.text}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row assistant">
              <div className="message">
                Thinking...
              </div>
            </div>
          )}
        </div>

        <div className="input-area">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend();
            }}
            placeholder="Talk to your companion..."
          />

          <button onClick={handleSend}>
            Send
          </button>
        </div>

      </div>
    </div>
  );
}

export default App;