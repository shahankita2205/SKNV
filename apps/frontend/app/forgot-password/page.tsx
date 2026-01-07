"use client";

import { useState, FormEvent } from "react";
import Image from "next/image";

import Logo from "@/assets/logo.svg";
import { apiRequest } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState<string>("");
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    try {
      await apiRequest("post", "/forgot-password/", { email });
      setSubmitted(true);
    } catch {
      setError("Something went wrong. Please try again.");
    }
  };

  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col gap-6">
          <Image src={Logo} alt="Logo" className="mb-2 h-10 w-auto" />
          <Card>
            <CardHeader>
              <CardTitle>Forgot your password?</CardTitle>
              <CardDescription>
                Enter your email and we&apos;ll send you a link to reset your
                password.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {submitted ? (
                <div className="text-sm text-green-700">
                  If an account with that email exists, a reset link has been
                  sent.
                </div>
              ) : (
                <form onSubmit={handleSubmit}>
                  <div className="flex flex-col gap-6">
                    {error && (
                      <div
                        className="bg-red-100 border-l-4 border-red-500 text-red-700 py-2 px-4 mb-4"
                        role="alert"
                      >
                        <p>{error}</p>
                      </div>
                    )}
                    <div className="grid gap-3">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="me@sknv.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>
                    <Button type="submit" className="w-full cursor-pointer">
                      Send Reset Link
                    </Button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
