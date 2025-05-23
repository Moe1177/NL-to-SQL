"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import * as XLSX from "xlsx";

interface FileUploadProps {
  onFileUpload: (data: any[], fileName: string, tableName: string) => void;
}

export default function FileUpload({ onFileUpload }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);

  const processFile = async (file: File) => {
    try {
      setIsUploading(true);
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data);
      const worksheet = workbook.Sheets[workbook.SheetNames[0]];
      const jsonData = XLSX.utils.sheet_to_json(worksheet);

      console.log("Sending data:", {
        json_data: jsonData,
        filename: file.name,
      }); // Debug log

      // Send data to backend
      const response = await fetch("http://localhost:8000/upload-json", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          json_data: jsonData,
          filename: file.name,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to upload data to server");
      }

      const result = await response.json();
      if (result.success) {
        onFileUpload(jsonData, file.name, result.table_name);
      } else {
        throw new Error(result.error_message || "Failed to process file");
      }
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Error processing file. Please try again."
      );
      console.error("Upload error:", error);
    } finally {
      setIsUploading(false);
    }
  };

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      setError("");
      const uploadedFile = acceptedFiles[0];

      // Check file type
      const validTypes = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      ];

      if (!validTypes.includes(uploadedFile.type)) {
        setError("Please upload only CSV or Excel files");
        return;
      }

      setFile(uploadedFile);
      processFile(uploadedFile);
    },
    [onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.ms-excel": [".xls"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ],
    },
    maxFiles: 1,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${
            isDragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 hover:border-blue-400"
          }
          ${error ? "border-red-500" : ""}
          ${isUploading ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <input {...getInputProps()} disabled={isUploading} />
        <div className="space-y-4">
          <div className="text-4xl mb-4">📁</div>
          {isDragActive ? (
            <p className="text-blue-500">Drop the file here...</p>
          ) : (
            <div className="space-y-2">
              <p className="text-gray-600">
                {isUploading
                  ? "Uploading..."
                  : "Drag and drop your file here, or click to select"}
              </p>
              <p className="text-sm text-gray-500">
                Supported formats: CSV, XLS, XLSX
              </p>
            </div>
          )}
        </div>
      </div>

      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}

      {file && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <p className="text-green-700">
            File selected:{" "}
            <span className="font-medium text-green-800">{file.name}</span>
          </p>
          <p className="text-sm text-green-600 mt-1">
            Size: {(file.size / 1024).toFixed(2)} KB
          </p>
        </div>
      )}
    </div>
  );
}
