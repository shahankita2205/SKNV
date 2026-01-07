"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { logout } from "@/lib/api";

export default function Page() {
  const router = useRouter();

  useEffect(() => {
    const doLogout = async () => {
      await logout();
      router.replace("/login");
    };

    doLogout();
  }, [router]);

  return <p>Logging out...</p>;
}
