"use client";

import { LOCAL_USER_ID } from "@/lib/constants";

/** No auth yet — always the local dev user. */
export function useSession() {
  return { userId: LOCAL_USER_ID, loading: false };
}
