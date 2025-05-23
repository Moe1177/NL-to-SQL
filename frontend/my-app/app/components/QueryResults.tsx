"use client";

interface QueryResultsProps {
  results: any[];
  columns: string[];
  generatedSql: string;
  rowCount: number;
}

export default function QueryResults({
  results,
  columns,
  generatedSql,
  rowCount,
}: QueryResultsProps) {
  if (!results.length) {
    return (
      <div className="w-full mt-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Query Results</h3>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600 font-medium">No results found</p>
          <p className="text-sm text-red-500 mt-1">
            Generated SQL: {generatedSql}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full mt-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Query Results</h3>
        <span className="text-sm text-gray-500">
          Showing {results.length} of {rowCount} rows
        </span>
      </div>

      <div className="mb-4 p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">
          <span className="font-medium">Generated SQL:</span> {generatedSql}
        </p>
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
              {results.map((row, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {index + 1}
                  </td>
                  {columns.map((column) => (
                    <td
                      key={column}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
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
    </div>
  );
}
