"use client";

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
}

export default function PromptInput({
  onSubmit,
  disabled = false,
}: PromptInputProps) {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const prompt = formData.get("prompt") as string;
    if (prompt.trim()) {
      onSubmit(prompt.trim());
      e.currentTarget.reset();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <input
          type="text"
          name="prompt"
          placeholder="Enter your prompt here..."
          disabled={disabled}
          className="w-full px-4 py-3 pr-12 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed text-black placeholder-gray-500"
        />
        <button
          type="submit"
          disabled={disabled}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-blue-500 hover:text-blue-600 disabled:text-gray-400 disabled:cursor-not-allowed"
        >
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
        </button>
      </div>
    </form>
  );
}
