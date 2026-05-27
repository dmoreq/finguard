"use client";

import { useSession } from "@/features/auth/useSession";
import { createClient } from "@/lib/supabase/client";
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
  const { userId, loading: sessionLoading } = useSession();
  const [currency, setCurrency] = useState("USD");
  const [timezone, setTimezone] = useState("UTC");
  const [displayName, setDisplayName] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!userId) return;
    const supabase = createClient();
    void supabase
      .from("profiles")
      .select("currency, timezone, display_name")
      .eq("id", userId)
      .single()
      .then(({ data, error }) => {
        if (error || !data) return;
        if (typeof data.currency === "string") setCurrency(data.currency);
        if (typeof data.timezone === "string") setTimezone(data.timezone);
        if (typeof data.display_name === "string") setDisplayName(data.display_name);
      });
  }, [userId]);

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!userId) return;
    setSaving(true);
    setStatus(null);
    const supabase = createClient();
    const { error } = await supabase
      .from("profiles")
      .update({ currency, timezone, display_name: displayName.trim() || null })
      .eq("id", userId);
    setSaving(false);
    setStatus(error ? error.message : "Settings saved.");
  };

  if (sessionLoading) {
    return (
      <div className="app-root app-loading">
        <p>Loading…</p>
      </div>
    );
  }

  if (!userId) {
    return (
      <div className="app-root app-loading">
        <p>
          <Link href="/login">Sign in</Link> to manage settings.
        </p>
      </div>
    );
  }

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
          Currency and timezone are used by the assistant for reports.
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
