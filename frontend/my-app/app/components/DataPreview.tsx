"use client";

interface DataPreviewProps {
  data: any[];
  fileName: string;
}

export default function DataPreview({ data, fileName }: DataPreviewProps) {
  if (!data.length) return null;

  const columns = Object.keys(data[0]);
  const previewData = data.slice(0, 100);

  return (
    <div className="w-full mt-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">
          Preview: {fileName}
        </h3>
        <span className="text-sm text-gray-500">
          Showing {previewData.length} of {data.length} rows
        </span>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <div className="max-h-[500px] overflow-y-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50 w-16"
                >
                  #
                </th>
                {columns.map((column) => (
                  <th
                    key={column}
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {previewData.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-medium">
                    {rowIndex + 1}
                  </td>
                  {columns.map((column) => (
                    <td
                      key={`${rowIndex}-${column}`}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                    >
                      {row[column]?.toString() || ""}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
