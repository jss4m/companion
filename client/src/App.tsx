import { useEffect, useRef, useState } from "react";
import "./App.css";
import type { ChatMessage } from "./types";
import {
  deleteMemory,
  getMemories,
  processVoice,
  sendMessage,
  speakVoice,
  updateMemory,
  uploadVoice,
  type PinnedMemory,
} from "./api";
import { AudioRecorder } from "./audio/recorder";
import TulipIcon from "./components/TulipIcon";
import TulipWatermark from "./components/TulipWatermark";

type VoiceState =
  | "idle"
  | "listening"
  | "processing"
  | "speaking";

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
  const [voiceError, setVoiceError] = useState("");

  const [showMemories, setShowMemories] = useState(false);
  const [memories, setMemories] = useState<PinnedMemory[]>([]);
  const [memoryLoading, setMemoryLoading] = useState(false);
  const [memoryError, setMemoryError] = useState("");
  const [editingMemoryId, setEditingMemoryId] = useState<number | null>(
    null
  );
  const [editingContent, setEditingContent] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recorderRef = useRef<AudioRecorder | null>(null);
  const pointerActiveRef = useRef(false);
  const pointerReleasedRef = useRef(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading, voiceState]);

  async function playVoice(audioBlob: Blob) {
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    setVoiceState("speaking");

    return new Promise<void>((resolve, reject) => {
      let settled = false;

      const cleanup = () => {
        URL.revokeObjectURL(audioUrl);
      };

      const finish = () => {
        if (settled) {
          return;
        }

        settled = true;
        cleanup();
        setVoiceState("idle");
        resolve();
      };

      const fail = (error: Error) => {
        if (settled) {
          return;
        }

        settled = true;
        cleanup();
        setVoiceState("idle");
        reject(error);
      };

      audio.addEventListener(
        "ended",
        finish,
        { once: true }
      );

      audio.addEventListener(
        "error",
        () => {
          fail(
            new Error(
              "The browser couldn't play the voice response."
            )
          );
        },
        { once: true }
      );

      audio.play().catch((error) => {
        fail(
          error instanceof Error
            ? error
            : new Error(
              "The browser couldn't play the voice response."
            )
        );
      });
    });
  }

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

  async function startVoiceRecording() {
    if (loading || voiceState !== "idle") {
      return;
    }

    setVoiceError("");
    pointerReleasedRef.current = false;

    const recorder = new AudioRecorder();

    try {
      await recorder.start();

      recorderRef.current = recorder;
      setVoiceState("listening");

      if (pointerReleasedRef.current) {
        pointerReleasedRef.current = false;
        await stopVoiceRecording();
      }
    } catch (error) {
      recorderRef.current = null;
      pointerReleasedRef.current = false;
      setVoiceState("idle");

      setVoiceError(
        error instanceof Error
          ? error.message
          : "I couldn't access the microphone."
      );
    }
  }

  async function stopVoiceRecording() {
    const recorder = recorderRef.current;

    if (!recorder) {
      pointerReleasedRef.current = true;
      return;
    }

    try {
      const audio = await recorder.stop();

      recorderRef.current = null;
      setVoiceState("processing");
      setLoading(true);

      await uploadVoice(audio);

      const result = await processVoice();

      const text = result.text?.trim();
      const reply = result.reply?.trim();

      if (!text && !reply) {
        setVoiceState("idle");
        return;
      }

      if (text) {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            sender: "user",
            text,
            timestamp: Date.now(),
          },
        ]);
      }

      if (reply) {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            sender: "assistant",
            text: reply,
            timestamp: Date.now(),
          },
        ]);

        const voiceAudio = await speakVoice(reply);
        await playVoice(voiceAudio);
      } else {
        setVoiceState("idle");
      }
    } catch (error) {
      setVoiceState("idle");

      setVoiceError(
        error instanceof Error
          ? error.message
          : "I couldn't process the recording."
      );
    } finally {
      recorderRef.current = null;
      pointerReleasedRef.current = false;
      setLoading(false);
    }
  }

  function handleVoicePointerDown(
    event: React.PointerEvent<HTMLButtonElement>
  ) {
    if (loading || voiceState !== "idle") {
      return;
    }

    event.preventDefault();
    pointerActiveRef.current = true;
    pointerReleasedRef.current = false;

    event.currentTarget.setPointerCapture(event.pointerId);
    void startVoiceRecording();
  }

  function handleVoicePointerUp(
    event: React.PointerEvent<HTMLButtonElement>
  ) {
    if (!pointerActiveRef.current) {
      return;
    }

    event.preventDefault();
    pointerActiveRef.current = false;

    if (
      event.currentTarget.hasPointerCapture(
        event.pointerId
      )
    ) {
      event.currentTarget.releasePointerCapture(
        event.pointerId
      );
    }

    void stopVoiceRecording();
  }

  function handleVoicePointerCancel() {
    if (!pointerActiveRef.current) {
      return;
    }

    pointerActiveRef.current = false;
    void stopVoiceRecording();
  }

  async function loadMemories() {
    setMemoryLoading(true);
    setMemoryError("");

    try {
      const data = await getMemories();
      setMemories(data);
    } catch {
      setMemoryError("Couldn't load memories.");
    } finally {
      setMemoryLoading(false);
    }
  }

  async function toggleMemories() {
    const nextState = !showMemories;

    setShowMemories(nextState);

    if (nextState) {
      await loadMemories();
    }
  }

  function startEditing(memory: PinnedMemory) {
    setEditingMemoryId(memory.id);
    setEditingContent(memory.content);
  }

  function cancelEditing() {
    setEditingMemoryId(null);
    setEditingContent("");
  }

  async function saveMemory(memoryId: number) {
    const content = editingContent.trim();

    if (!content) {
      return;
    }

    setMemoryError("");

    try {
      const updated = await updateMemory(
        memoryId,
        content
      );

      setMemories((prev) =>
        prev.map((memory) =>
          memory.id === memoryId
            ? updated
            : memory
        )
      );

      cancelEditing();
    } catch {
      setMemoryError("Couldn't update that memory.");
    }
  }

  async function handleDeleteMemory(memoryId: number) {
    setMemoryError("");

    try {
      await deleteMemory(memoryId);

      setMemories((prev) =>
        prev.filter(
          (memory) => memory.id !== memoryId
        )
      );

      if (editingMemoryId === memoryId) {
        cancelEditing();
      }
    } catch {
      setMemoryError("Couldn't delete that memory.");
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

  const busy =
    loading ||
    voiceState === "listening" ||
    voiceState === "processing" ||
    voiceState === "speaking";

  const voiceButtonLabel =
    voiceState === "listening"
      ? "Release to stop recording"
      : voiceState === "processing"
        ? "Processing voice"
        : voiceState === "speaking"
          ? "Speaking"
          : "Hold to record";

  return (
    <div className="app">
      <TulipWatermark />

      <div className="chat-container">
        <header className="header">
          <div>
            <h2>Personal Companion</h2>
            <p>Always present • Quiet reflection</p>
          </div>

          <div className="header-actions">
            <button
              className={`memory-button ${showMemories ? "active" : ""
                }`}
              onClick={toggleMemories}
            >
              Memories
            </button>

            <div className="header-status">
              <span className="status-dot" />
              <span>Online</span>
            </div>
          </div>
        </header>

        {showMemories && (
          <section className="memory-panel">
            <div className="memory-panel-header">
              <div>
                <h3>Known memories</h3>
                <p>Facts your companion has saved.</p>
              </div>

              <button
                className="memory-refresh"
                onClick={loadMemories}
                disabled={memoryLoading}
              >
                Refresh
              </button>
            </div>

            {memoryLoading && (
              <div className="memory-status">
                Loading memories...
              </div>
            )}

            {memoryError && (
              <div className="memory-error">
                {memoryError}
              </div>
            )}

            {!memoryLoading &&
              !memoryError &&
              memories.length === 0 && (
                <div className="memory-status">
                  No pinned memories yet.
                </div>
              )}

            {!memoryLoading && memories.length > 0 && (
              <div className="memory-list">
                {memories.map((memory) => (
                  <div
                    key={memory.id}
                    className="memory-item"
                  >
                    {editingMemoryId === memory.id ? (
                      <div className="memory-edit">
                        <textarea
                          value={editingContent}
                          onChange={(event) =>
                            setEditingContent(
                              event.target.value
                            )
                          }
                          autoFocus
                        />

                        <div className="memory-actions">
                          <button
                            onClick={() =>
                              saveMemory(memory.id)
                            }
                          >
                            Save
                          </button>

                          <button
                            className="secondary"
                            onClick={cancelEditing}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="memory-content">
                          <span className="memory-id">
                            #{memory.id}
                          </span>

                          <span>
                            {memory.content}
                          </span>
                        </div>

                        <div className="memory-actions">
                          <button
                            onClick={() =>
                              startEditing(memory)
                            }
                          >
                            Edit
                          </button>

                          <button
                            className="delete"
                            onClick={() =>
                              handleDeleteMemory(
                                memory.id
                              )
                            }
                          >
                            Delete
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

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

          {loading &&
            voiceState !== "speaking" && (
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

          {voiceState === "listening" && (
            <div className="voice-status">
              Listening...
            </div>
          )}

          {voiceState === "processing" && (
            <div className="voice-status">
              Processing...
            </div>
          )}

          {voiceState === "speaking" && (
            <div className="voice-status">
              Speaking...
            </div>
          )}

          {voiceError && (
            <div className="voice-status">
              {voiceError}
            </div>
          )}

          <div ref={messagesEndRef} />
        </main>

        <div className="input-area">
          <input
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder={
              voiceState === "listening"
                ? "Listening..."
                : voiceState === "processing"
                  ? "Processing..."
                  : voiceState === "speaking"
                    ? "Speaking..."
                    : "Talk to your companion..."
            }
            disabled={busy}
            autoComplete="off"
          />

          <button
            className={`voice-button ${voiceState === "listening"
                ? "recording"
                : ""
              }`}
            onPointerDown={handleVoicePointerDown}
            onPointerUp={handleVoicePointerUp}
            onPointerCancel={handleVoicePointerCancel}
            disabled={
              loading &&
              voiceState !== "listening"
            }
            aria-label={voiceButtonLabel}
            title={voiceButtonLabel}
          >
            {voiceState === "listening"
              ? "●"
              : "Mic"}
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
