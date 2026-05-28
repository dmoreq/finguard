"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const CURRENCIES = ["USD", "EUR", "GBP", "VND", "JPY", "AUD", "CAD"];
const TIMEZONES = [
  "UTC",
  "America/New_York",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Paris",
  "Asia/Ho_Chi_Minh",
  "Asia/Tokyo",
  "Australia/Sydney",
];

export default function SettingsPage() {
  const [currency, setCurrency] = useState("USD");
  const [timezone, setTimezone] = useState("UTC");
  const [displayName, setDisplayName] = useState("Local user");
  const [status, setStatus] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void fetch("/api/data/profile")
      .then((res) => res.json())
      .then((data) => {
        if (typeof data.currency === "string") setCurrency(data.currency);
        if (typeof data.timezone === "string") setTimezone(data.timezone);
        if (typeof data.display_name === "string") setDisplayName(data.display_name);
      })
      .catch(() => {
        // Profile defaults are fine
      });
  }, []);

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setStatus(null);
    try {
      const response = await fetch("/api/data/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          display_name: displayName.trim() || "Local user",
          currency,
          timezone,
        }),
      });
      if (!response.ok) throw new Error("Could not save settings.");
      setStatus("Settings saved.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not save settings.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="app-root settings-page">
      <header className="app-header">
        <Link href="/chat" className="button button-ghost">
          ← Back to chat
        </Link>
      </header>
      <main className="settings-main">
        <h1>Profile settings</h1>
        <p className="settings-note">
          Stored locally in SQLite. Used by Rasa for currency and timezone on reports.
        </p>
        <form className="settings-form" onSubmit={handleSave}>
          <label className="login-label" htmlFor="displayName">
            Display name
          </label>
          <input
            id="displayName"
            className="login-input"
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
          />

          <label className="login-label" htmlFor="currency">
            Currency
          </label>
          <select
            id="currency"
            className="login-input"
            value={currency}
            onChange={(event) => setCurrency(event.target.value)}
          >
            {CURRENCIES.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>

          <label className="login-label" htmlFor="timezone">
            Timezone
          </label>
          <select
            id="timezone"
            className="login-input"
            value={timezone}
            onChange={(event) => setTimezone(event.target.value)}
          >
            {TIMEZONES.map((zone) => (
              <option key={zone} value={zone}>
                {zone}
              </option>
            ))}
          </select>

          {status && (
            <output className={status === "Settings saved." ? "settings-ok" : "login-error"}>
              {status}
            </output>
          )}

          <button className="button button-primary login-submit" type="submit" disabled={saving}>
            {saving ? "Saving…" : "Save"}
          </button>
        </form>
      </main>
    </div>
  );
}
