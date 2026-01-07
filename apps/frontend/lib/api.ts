import axios from "axios";

import { setToken, getToken, removeToken } from "@/utils/auth";
import { User } from "@/lib/types";

const API_HOST = process.env.NEXT_PUBLIC_API_HOST as string;

export const apiRequest = async <T>(
  method: "get" | "post" | "put" | "delete",
  path: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any = null
): Promise<T> => {
  const token = getToken();
  const config = {
    method,
    url: `${API_HOST}${path}`,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Token ${token}` }),
    },
    ...(data && { data }),
  };

  const response = await axios(config);
  return response.data;
};

export const login = async (
  email: string,
  password: string
): Promise<string> => {
  const data = await apiRequest<{ token: string }>("post", "/login/", {
    email,
    password,
  });
  setToken(data.token);
  return data.token;
};

export const register = async (
  firstName: string,
  lastName: string,
  email: string,
  password: string
): Promise<string> => {
  const data = await apiRequest<{ token: string }>("post", "/register/", {
    first_name: firstName,
    last_name: lastName,
    email,
    password,
  });
  setToken(data.token);
  return data.token;
};

export const getProfile = async (): Promise<User> => {
  return await apiRequest<User>("get", "/me/");
};

export const logout = async (): Promise<void> => {
  try {
    await apiRequest("post", "/logout/");
  } catch (err) {
    console.error("Logout failed:", err);
  }

  removeToken();
};
