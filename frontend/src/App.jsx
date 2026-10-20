
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello! Welcome to the MIPaaS medical information assistant. How can I help you today?",
    },
  ]);
  const [loading, setLoading] = useState(false);

  async function sendMessage(event) {
    event.preventDefault();

    const text = message.trim();

    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", text },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const detail =
          typeof data.detail === "string"
            ? data.detail
            : "The request could not be completed.";

        const errorText = detail.toLowerCase();

        if (
          response.status === 429 ||
          errorText.includes("resource_exhausted") ||
          errorText.includes("rate limit") ||
          errorText.includes("quota") ||
          errorText.includes("usage limit")
        ) {
          throw new Error(
            "Gemini usage limit reached. Please wait until your quota resets or check your API usage limits."
          );
        }

        if (
          response.status === 502 ||
          response.status === 503 ||
          response.status === 504
        ) {
          throw new Error(
            detail ||
              "The AI service is temporarily unavailable. Please try again later."
          );
        }

        throw new Error(detail);
      }

      if (typeof data.reply !== "string") {
        throw new Error(
          "The backend responded, but no valid reply was received."
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: data.reply,
        },
      ]);
    } catch (error) {
      let errorMessage;

      if (error instanceof TypeError) {
        errorMessage =
          "Could not connect to the backend. Please check that your server is running and that your browser can access it.";
      } else {
        errorMessage =
          error.message || "Something went wrong. Please try again.";
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: errorMessage,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // Fix common Markdown markers that Gemini may incorrectly escape.
  function formatMarkdown(text) {
    return text.replace(/\\([*#_-])/g, "$1");
  }

  return (
    <main className="app">
      <header className="chat-header">
        <div className="logo">M</div>

        <div>
          <h1>MIPaaS Chatbot</h1>
          <p>Medical Information Assistant</p>
        </div>

        <span className="status">
          <span className="status-dot" />
          Online
        </span>
      </header>

      <section
        className="chat-window"
        aria-label="Chat messages"
        aria-live="polite"
      >
        {messages.map((item, index) => (
          <div
            key={index}
            className={`message-row ${item.role}`}
          >
            <div className="message">
              <strong>
                {item.role === "user"
                  ? "You"
                  : "MIPaaS Assistant"}
              </strong>

              {item.role === "assistant" ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                >
                  {formatMarkdown(item.text)}
                </ReactMarkdown>
              ) : (
                <p>{item.text}</p>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-row assistant">
            <div className="message">
              <p>Sending your message...</p>
            </div>
          </div>
        )}
      </section>

      <form className="chat-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Type your message here..."
          aria-label="Your message"
          maxLength={2000}
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading || !message.trim()}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </form>

      <footer className="chat-footer">
        For informational purposes only. Not a substitute for
        professional medical advice or diagnosis.
      </footer>
    </main>
  );
}

export default App;
