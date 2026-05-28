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
  const [exporting, setExporting] = useState(false);
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
      setExporting(true);
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
    } finally {
      setExporting(false);
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
        <Link href="/chat" className="button button-ghost" style={{ minHeight: "40px" }}>
          ← {isVi ? "Về chat" : "Back"}
        </Link>
      </header>
      <main className="settings-container">
        <div className="settings-header">
          <h1>{isVi ? "Cài đặt" : "Settings"}</h1>
          <p className="settings-subtitle">
            {isVi
              ? "Quản lý hồ sơ, tùy chọn và dữ liệu của bạn"
              : "Manage your profile, preferences, and data"}
          </p>
        </div>

        {/* PROFILE SECTION */}
        <section className="settings-section">
          <div className="section-header">
            <h2>{isVi ? "Hồ sơ" : "Profile"}</h2>
          </div>
          <form className="settings-form" onSubmit={handleSave}>
            <div className="form-group">
              <label className="form-label" htmlFor="displayName">
                {isVi ? "Tên hiển thị" : "Display name"}
              </label>
              <input
                id="displayName"
                className="form-input"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder={isVi ? "Tên của bạn" : "Your name"}
              />
            </div>

            {/* PREFERENCES SECTION */}
            <div className="section-header" style={{ marginTop: 24 }}>
              <h2>{isVi ? "Tùy chọn" : "Preferences"}</h2>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="locale">
                {isVi ? "Ngôn ngữ" : "Language"}
              </label>
              <select id="locale" className="form-input" value={locale} onChange={(e) => setLocale(e.target.value)}>
                {LOCALES.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="currency">
                {isVi ? "Tiền tệ" : "Currency"}
              </label>
              <select
                id="currency"
                className="form-input"
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
              >
                {CURRENCIES.map((code) => (
                  <option key={code} value={code}>
                    {code}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="timezone">
                {isVi ? "Múi giờ" : "Timezone"}
              </label>
              <select
                id="timezone"
                className="form-input"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
              >
                {TIMEZONES.map((zone) => (
                  <option key={zone} value={zone}>
                    {zone}
                  </option>
                ))}
              </select>
            </div>

            {status && (
              <output
                className={
                  status.includes("saved") || status.includes("lưu") || status.includes("khôi") || status.includes("tải")
                    ? "settings-ok"
                    : "login-error"
                }
                style={{ marginTop: 16 }}
              >
                {status}
              </output>
            )}

            <button
              className="button button-primary"
              type="submit"
              disabled={saving}
              style={{ marginTop: 16, width: "100%" }}
            >
              {saving ? (isVi ? "Đang lưu…" : "Saving…") : isVi ? "Lưu cài đặt" : "Save settings"}
            </button>
          </form>
        </section>

        {/* DATA MANAGEMENT SECTION */}
        <section className="settings-section">
          <div className="section-header">
            <h2>{isVi ? "Quản lý dữ liệu" : "Data management"}</h2>
            <p className="section-description">
              {isVi ? "Sao lưu, xuất và khôi phục dữ liệu tài chính của bạn" : "Backup, export, and restore your financial data"}
            </p>
          </div>

          <div className="data-actions">
            <div className="action-card">
              <div className="action-header">
                <h3>{isVi ? "Xuất dữ liệu" : "Export data"}</h3>
                <p className="action-description">
                  {isVi ? "Tải xuống bản sao lưu JSON của toàn bộ dữ liệu" : "Download JSON backup of all your data"}
                </p>
              </div>
              <button
                type="button"
                className="button button-primary"
                onClick={() => void handleBackup()}
                disabled={exporting}
                style={{ width: "100%" }}
              >
                {exporting
                  ? isVi
                    ? "Đang tải…"
                    : "Downloading…"
                  : isVi
                    ? "⬇ Xuất"
                    : "⬇ Export"}
              </button>
            </div>

            <div className="action-card">
              <div className="action-header">
                <h3>{isVi ? "Khôi phục dữ liệu" : "Restore data"}</h3>
                <p className="action-description">
                  {isVi ? "Tải lên tập tin JSON từ bản sao lưu trước" : "Upload JSON file from a previous backup"}
                </p>
              </div>
              <button
                type="button"
                className="button button-ghost"
                onClick={() => fileRef.current?.click()}
                style={{ width: "100%" }}
              >
                {isVi ? "⬆ Chọn file" : "⬆ Choose file"}
              </button>
              <input
                ref={fileRef}
                type="file"
                accept="application/json,.json"
                hidden
                onChange={(e) => void handleRestore(e)}
              />
            </div>
          </div>

          <div className="data-notice">
            <p>
              {isVi
                ? "💡 Dữ liệu được lưu cục bộ trên thiết bị của bạn. Sao lưu thường xuyên để tránh mất dữ liệu."
                : "💡 Data is stored locally on your device. Backup regularly to prevent data loss."}
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
