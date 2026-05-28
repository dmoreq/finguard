"use client";

import { downloadBackup, fetchUserProfile, restoreBackup } from "@/lib/data/financial-data";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

const CURRENCIES = ["VND", "USD", "EUR", "GBP", "JPY", "AUD", "CAD"];
const TIMEZONES = [
  "Asia/Ho_Chi_Minh",
  "UTC",
  "America/New_York",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Paris",
  "Asia/Tokyo",
  "Australia/Sydney",
];
const LOCALES = [
  { value: "vi", label: "Tiếng Việt" },
  { value: "en", label: "English" },
];

export default function SettingsPage() {
  const [currency, setCurrency] = useState("VND");
  const [timezone, setTimezone] = useState("Asia/Ho_Chi_Minh");
  const [locale, setLocale] = useState("vi");
  const [displayName, setDisplayName] = useState("Local user");
  const [status, setStatus] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const fileRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    void fetchUserProfile()
      .then((data) => {
        setCurrency(data.currency);
        setTimezone(data.timezone);
        setLocale(data.locale);
        setDisplayName(data.display_name);
      })
      .catch(() => {
        // defaults are fine
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
          locale,
        }),
      });
      if (!response.ok) throw new Error("Could not save settings.");
      setStatus(locale.startsWith("vi") ? "Đã lưu cài đặt." : "Settings saved.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not save settings.");
    } finally {
      setSaving(false);
    }
  };

  const handleBackup = async () => {
    try {
      const blob = await downloadBackup();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `finguard-backup-${new Date().toISOString().slice(0, 10)}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
      setStatus(locale.startsWith("vi") ? "Đã tải bản sao lưu." : "Backup downloaded.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Backup failed.");
    }
  };

  const handleRestore = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (
      !window.confirm(
        locale.startsWith("vi")
          ? "Khôi phục sẽ ghi đè dữ liệu hiện tại. Tiếp tục?"
          : "Restore will overwrite current data. Continue?",
      )
    ) {
      return;
    }
    try {
      await restoreBackup(file);
      setStatus(locale.startsWith("vi") ? "Đã khôi phục dữ liệu." : "Data restored.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Restore failed.");
    } finally {
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const isVi = locale.startsWith("vi");

  return (
    <div className="app-root settings-page">
      <header className="app-header">
        <Link href="/chat" className="button button-ghost">
          ← {isVi ? "Về chat" : "Back to chat"}
        </Link>
      </header>
      <main className="settings-main">
        <h1>{isVi ? "Cài đặt hồ sơ" : "Profile settings"}</h1>
        <p className="settings-note">
          {isVi
            ? "Lưu cục bộ trong SQLite. Dùng cho tiền tệ, múi giờ và ngôn ngữ chat."
            : "Stored locally in SQLite. Used for currency, timezone, and chat language."}
        </p>
        <form className="settings-form" onSubmit={handleSave}>
          <label className="login-label" htmlFor="displayName">
            {isVi ? "Tên hiển thị" : "Display name"}
          </label>
          <input
            id="displayName"
            className="login-input"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />

          <label className="login-label" htmlFor="locale">
            {isVi ? "Ngôn ngữ" : "Language"}
          </label>
          <select
            id="locale"
            className="login-input"
            value={locale}
            onChange={(e) => setLocale(e.target.value)}
          >
            {LOCALES.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>

          <label className="login-label" htmlFor="currency">
            {isVi ? "Tiền tệ" : "Currency"}
          </label>
          <select
            id="currency"
            className="login-input"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
          >
            {CURRENCIES.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>

          <label className="login-label" htmlFor="timezone">
            {isVi ? "Múi giờ" : "Timezone"}
          </label>
          <select
            id="timezone"
            className="login-input"
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
          >
            {TIMEZONES.map((zone) => (
              <option key={zone} value={zone}>
                {zone}
              </option>
            ))}
          </select>

          {status && (
            <output
              className={
                status.includes("saved") ||
                status.includes("lưu") ||
                status.includes("khôi") ||
                status.includes("tải")
                  ? "settings-ok"
                  : "login-error"
              }
            >
              {status}
            </output>
          )}

          <button className="button button-primary login-submit" type="submit" disabled={saving}>
            {saving ? (isVi ? "Đang lưu…" : "Saving…") : isVi ? "Lưu" : "Save"}
          </button>
        </form>

        <section className="settings-form" style={{ marginTop: 24 }}>
          <h2 style={{ fontSize: 16, marginBottom: 8 }}>
            {isVi ? "Sao lưu & khôi phục" : "Backup & restore"}
          </h2>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              type="button"
              className="button button-ghost"
              onClick={() => void handleBackup()}
            >
              {isVi ? "Tải bản sao lưu" : "Download backup"}
            </button>
            <button
              type="button"
              className="button button-ghost"
              onClick={() => fileRef.current?.click()}
            >
              {isVi ? "Khôi phục từ file" : "Restore from file"}
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="application/json,.json"
              hidden
              onChange={(e) => void handleRestore(e)}
            />
          </div>
        </section>
      </main>
    </div>
  );
}
