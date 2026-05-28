import { redirect } from "next/navigation";

/** Auth deferred — send straight to chat. */
export default function LoginPage() {
  redirect("/chat");
}
