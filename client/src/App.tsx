import { useEffect, useRef, useState } from "react";
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

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function handleSend() {
    const text = input.trim();

    if (!text || loading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      sender: "user",
      text,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendMessage(text);

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        sender: "assistant",
        text: data.reply,
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          sender: "assistant",
          text: "I couldn't reach the companion server.",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLInputElement>
  ) {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="app">
      <TulipWatermark />

      <div className="chat-container">
        <header className="header">
          <div>
            <h2>Personal Companion</h2>
            <p>Always present • Quiet reflection</p>
          </div>

          <div className="header-status">
            <span className="status-dot" />
            <span>Online</span>
          </div>
        </header>

        <main className="messages">
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
                <span className="message-sender">
                  {message.sender === "user"
                    ? "You"
                    : "Companion"}
                </span>

                <p>{message.text}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row assistant">
              <div className="assistant-avatar">
                <TulipIcon className="tulip-icon" />
              </div>

              <div className="message thinking-message">
                <span className="message-sender">
                  Companion
                </span>

                <div className="thinking-indicator">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </main>

        <div className="input-area">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Talk to your companion..."
            disabled={loading}
            autoComplete="off"
          />

          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
