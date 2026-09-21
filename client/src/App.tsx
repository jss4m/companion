import { useEffect, useRef, useState } from "react";
import "./App.css";
import type { ChatMessage } from "./types";
import { sendMessage, sendVoice } from "./api";
import TulipIcon from "./components/TulipIcon";
import TulipWatermark from "./components/TulipWatermark";

type VoiceState = "idle" | "listening" | "processing";

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
  const [voiceState, setVoiceState] = useState<VoiceState>("idle");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading, voiceState]);

  async function handleSend() {
    const text = input.trim();

    if (!text || loading || voiceState !== "idle") {
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

  async function handleVoice() {
    if (loading || voiceState !== "idle") {
      return;
    }

    setVoiceState("listening");

    try {
      setVoiceState("processing");

      const data = await sendVoice(5);

      if (data.text) {
        const userMessage: ChatMessage = {
          id: crypto.randomUUID(),
          sender: "user",
          text: data.text,
          timestamp: Date.now(),
        };

        setMessages((prev) => [...prev, userMessage]);
      }

      if (data.reply) {
        const assistantMessage: ChatMessage = {
          id: crypto.randomUUID(),
          sender: "assistant",
          text: data.reply,
          timestamp: Date.now(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          sender: "assistant",
          text: "I couldn't use the voice service.",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setVoiceState("idle");
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

  const busy = loading || voiceState !== "idle";

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

          {(loading || voiceState === "processing") && (
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
            placeholder={
              voiceState === "listening"
                ? "Listening..."
                : voiceState === "processing"
                  ? "Processing..."
                  : "Talk to your companion..."
            }
            disabled={busy}
            autoComplete="off"
          />

          <button
            className={`voice-button ${
              voiceState === "listening" ? "recording" : ""
            }`}
            onClick={handleVoice}
            disabled={busy}
            aria-label="Talk by voice"
            title="Talk by voice"
          >
            {voiceState === "listening" ? "●" : "Mic"}
          </button>

          <button
            onClick={handleSend}
            disabled={!input.trim() || busy}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;