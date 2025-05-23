"use client";

import { useState, useRef } from "react";

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
  tableName: string;
  onQueryResult: (result: any) => void;
}

export default function PromptInput({
  onSubmit,
  disabled = false,
  tableName,
  onQueryResult,
}: PromptInputProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const formRef = useRef<HTMLFormElement>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const prompt = formData.get("prompt") as string;

    if (prompt.trim()) {
      setIsLoading(true);
      setError("");

      try {
        console.log("Sending query with table name:", tableName);
        const response = await fetch("http://localhost:8000/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: prompt.trim(),
            table_name: tableName,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          console.error("Query error response:", errorData);
          throw new Error(errorData.detail || "Failed to process query");
        }

        const result = await response.json();
        console.log("Query result:", result);
        if (result.success) {
          onQueryResult(result);
          onSubmit(prompt.trim());
          // Reset form using the ref
          if (formRef.current) {
            formRef.current.reset();
          }
        } else {
          throw new Error(result.error_message || "Failed to process query");
        }
      } catch (error) {
        setError(
          error instanceof Error ? error.message : "Error processing query"
        );
        console.error("Query error:", error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="w-full">
      <form ref={formRef} onSubmit={handleSubmit} className="w-full">
        <div className="relative">
          <input
            type="text"
            name="prompt"
            placeholder="Enter your prompt here..."
            disabled={disabled || isLoading}
            className="w-full px-4 py-3 pr-12 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed text-black placeholder-gray-500"
          />
          <button
            type="submit"
            disabled={disabled || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-blue-500 hover:text-blue-600 disabled:text-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <svg
                className="animate-spin h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
                className="w-5 h-5"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
                />
              </svg>
            )}
          </button>
        </div>
      </form>
      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
    </div>
  );
}
