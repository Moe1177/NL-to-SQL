"use client";

import { useState } from "react";
import FileUpload from "./components/FileUpload";
import PromptInput from "./components/PromptInput";
import DataPreview from "./components/DataPreview";
import QueryResults from "./components/QueryResults";

export default function Home() {
  const [data, setData] = useState<any[]>([]);
  const [fileName, setFileName] = useState<string>("");
  const [tableName, setTableName] = useState<string>("");
  const [queryResult, setQueryResult] = useState<any>(null);

  const handleFileUpload = (
    newData: any[],
    newFileName: string,
    newTableName: string
  ) => {
    console.log("handleFileUpload called with:", {
      dataLength: newData.length,
      fileName: newFileName,
      tableName: newTableName,
    }); // Debug log

    setData(newData);
    setFileName(newFileName);
    setTableName(newTableName);
    setQueryResult(null); // Clear previous query results
  };

  const handlePromptSubmit = (prompt: string) => {
    console.log("Submitted prompt:", prompt);
  };

  const handleQueryResult = (result: any) => {
    console.log("Query result received:", result); // Debug log
    setQueryResult(result);
  };

  const handleReset = async () => {
    try {
      console.log("Resetting view for table:", tableName); // Debug log

      const response = await fetch("http://localhost:8000/reset", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ table_name: tableName }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to reset view");
      }

      const result = await response.json();
      console.log("Reset successful:", result); // Debug log
      setQueryResult(result);
    } catch (error) {
      console.error("Error resetting view:", error);
      // You might want to show an error message to the user here
    }
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

          {tableName && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
              <PromptInput
                onSubmit={handlePromptSubmit}
                tableName={tableName}
                onQueryResult={handleQueryResult}
              />
            </div>
          )}

          {queryResult ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
              <QueryResults
                results={queryResult.results}
                columns={queryResult.columns}
                generatedSql={queryResult.generated_sql}
                rowCount={queryResult.row_count}
                tableName={tableName}
                onReset={handleReset}
              />
            </div>
          ) : (
            data.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
                <DataPreview data={data} fileName={fileName} />
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}
