"use client";

import { useState } from "react";
import FileUpload from "./components/FileUpload";
import PromptInput from "./components/PromptInput";
import DataPreview from "./components/DataPreview";

export default function Home() {
  const [data, setData] = useState<any[]>([]);
  const [fileName, setFileName] = useState<string>("");

  const handleFileUpload = (newData: any[], newFileName: string) => {
    setData(newData);
    setFileName(newFileName);
  };

  const handlePromptSubmit = (prompt: string) => {
    // TODO: Handle prompt submission
    console.log("Prompt submitted:", prompt);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            NL to SQL Converter
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Upload your data and ask questions in natural language
          </p>
        </div>

        <div className="space-y-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
            <FileUpload onFileUpload={handleFileUpload} />
          </div>

          {data.length > 0 && (
            <>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
                <PromptInput onSubmit={handlePromptSubmit} />
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
                <DataPreview data={data} fileName={fileName} />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
