import React from 'react';

interface CodeOutputProps {
  value: string;
  label: string;
}

const CodeOutput: React.FC<CodeOutputProps> = ({ value, label }) => {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-semibold text-gray-700">{label}</label>
        {value && (
          <button
            onClick={handleCopy}
            className="text-sm text-guardian-blue hover:text-guardian-blue/80 transition-colors"
          >
            📋 Copy
          </button>
        )}
      </div>
      <pre className="flex-1 p-2 border rounded-md bg-gray-50 font-mono text-sm text-gray-800 overflow-auto resize-y">
        {value || 'Generated tests will appear here...'}
      </pre>
    </div>
  );
};

export default CodeOutput;
