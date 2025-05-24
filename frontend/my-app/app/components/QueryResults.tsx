"use client";

interface QueryResultsProps {
  results: any[];
  columns: string[];
  generatedSql: string;
  rowCount: number;
  tableName: string;
  onReset: () => void;
}

export default function QueryResults({
  results,
  columns,
  generatedSql,
  rowCount,
  tableName,
  onReset,
}: QueryResultsProps) {
  if (!results || results.length === 0) {
    return (
      <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4">Query Results</h2>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600 font-medium">No results found</p>
          <p className="text-red-500 mt-2 text-sm">Generated SQL:</p>
          <pre className="mt-2 p-2 bg-red-50 rounded text-red-700 text-sm overflow-x-auto">
            {generatedSql}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Query Results</h2>
        <button
          onClick={onReset}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors flex items-center gap-2"
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
              d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
            />
          </svg>
          Reset View
        </button>
      </div>

      <div className="mb-4">
        <p className="text-gray-800 mb-2 font-medium">Generated SQL:</p>
        <pre className="p-3 bg-gray-50 rounded text-sm overflow-x-auto text-gray-900">
          {generatedSql}
        </pre>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <div className="max-h-[500px] overflow-y-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-16">
                  #
                </th>
                {columns.map((column) => (
                  <th
                    key={column}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {results.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {rowIndex + 1}
                  </td>
                  {columns.map((column) => (
                    <td
                      key={`${rowIndex}-${column}`}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                    >
                      {row[column]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Showing {results.length} of {rowCount} rows
      </div>
    </div>
  );
}
