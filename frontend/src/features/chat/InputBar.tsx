"use client";

import { useRef, useState } from "react";

type Props = {
  disabled?: boolean;
  onSend: (text: string) => void;
};

export function InputBar({ disabled = false, onSend }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const canSend = value.trim().length > 0 && !disabled;

  const send = () => {
    const text = value.trim();
    if (!text || disabled) return;

    onSend(text);
    setValue("");

    requestAnimationFrame(() => {
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
        textareaRef.current.focus();
      }
    });
  };

  return (
    <div className="input-bar">
      <div className="input-shell">
        <textarea
          ref={textareaRef}
          className="chat-input"
          value={value}
          disabled={disabled}
          onChange={(event) => setValue(event.target.value)}
          onInput={(event) => {
            event.currentTarget.style.height = "auto";
            event.currentTarget.style.height = `${Math.min(event.currentTarget.scrollHeight, 112)}px`;
          }}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              send();
            }
          }}
          placeholder='e.g. "I got paid $3,200" or "Spent $45 on groceries"...'
          rows={1}
        />
      </div>
      <button className="send-button" disabled={!canSend} onClick={send} title="Send">
        &gt;
      </button>
    </div>
  );
}
