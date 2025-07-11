import React from 'react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  label: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ value, onChange, label }) => {
  return (
    <div className="flex flex-col h-full">
      <label className="mb-2 text-sm font-semibold text-gray-700">{label}</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="flex-1 p-2 border rounded-md resize-y font-mono text-gray-800"
        placeholder="Type your code here..."
      />
    </div>
  );
};

export default CodeEditor;

