"use client";

import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"sign_in" | "sign_up">("sign_in");
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setInfo(null);
    setLoading(true);

    try {
      const supabase = createClient();
      const result =
        mode === "sign_in"
          ? await supabase.auth.signInWithPassword({ email, password })
          : await supabase.auth.signUp({ email, password });

      if (result.error) {
        setError(result.error.message);
        return;
      }

      router.push("/chat");
      router.refresh();
    } catch (err) {
      const detail = err instanceof Error ? err.message : "Sign in failed.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <h1 className="login-title">Finguard</h1>
      <p className="login-subtitle">Sign in to sync your transactions securely.</p>

      <label className="login-label" htmlFor="email">
        Email
      </label>
      <input
        id="email"
        className="login-input"
        type="email"
        autoComplete="email"
        required
        value={email}
        onChange={(event) => setEmail(event.target.value)}
      />

      <label className="login-label" htmlFor="password">
        Password
      </label>
      <input
        id="password"
        className="login-input"
        type="password"
        autoComplete={mode === "sign_in" ? "current-password" : "new-password"}
        required
        minLength={8}
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />

      {error && (
        <p className="login-error" role="alert">
          {error}
        </p>
      )}

      <button className="button button-primary login-submit" type="submit" disabled={loading}>
        {loading ? "Please wait…" : mode === "sign_in" ? "Sign in" : "Create account"}
      </button>

      <button
        type="button"
        className="button button-ghost login-toggle"
        onClick={() => setMode((current) => (current === "sign_in" ? "sign_up" : "sign_in"))}
      >
        {mode === "sign_in" ? "Need an account? Sign up" : "Already have an account? Sign in"}
      </button>

      {mode === "sign_in" && (
        <button
          type="button"
          className="button button-ghost login-toggle"
          onClick={async () => {
            if (!email.trim()) {
              setError("Enter your email first.");
              return;
            }
            setError(null);
            setInfo(null);
            const supabase = createClient();
            const { error: resetError } = await supabase.auth.resetPasswordForEmail(email.trim(), {
              redirectTo: `${window.location.origin}/auth/callback`,
            });
            if (resetError) setError(resetError.message);
            else setInfo("Check your email for a password reset link.");
          }}
        >
          Forgot password?
        </button>
      )}

      {info && <output className="login-info">{info}</output>}
    </form>
  );
}
