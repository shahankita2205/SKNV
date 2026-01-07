"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getToken, removeToken } from "@/utils/auth";
import { apiRequest } from "@/lib/api";
import { User } from "@/lib/types";

const AuthContext = createContext<User | null>(null);

export function useAuth() {
  return useContext(AuthContext);
}

type RequireAuthProps = {
  children: React.ReactNode;
};

export default function RequireAuth({ children }: RequireAuthProps) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = getToken();
      if (!token) {
        router.push("/login");
        return;
      }

      try {
        const data = await apiRequest("get", "/me/");
        setUser(data as User);
      } catch {
        removeToken();
        router.push("/login");
        return;
      }

      setIsChecking(false);
    };

    checkAuth();
  }, [router]);

  if (isChecking) return null;

  return <AuthContext.Provider value={user}>{children}</AuthContext.Provider>;
}
