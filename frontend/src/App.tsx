import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import CodeTester from './pages/CodeTester';

function App() {
  const [currentPage, setCurrentPage] = useState('code-tester');

  const renderPage = () => {
    switch (currentPage) {
      case 'code-tester':
        return <CodeTester />;
      case 'home':
        return <div className="p-6"><h2 className="text-2xl font-semibold">Home Page</h2><p>Welcome to Code Guardian!</p></div>;
      case 'story-creator':
        return <div className="p-6"><h2 className="text-2xl font-semibold">Story Creator</h2><p>Coming soon...</p></div>;
      case 'code-documenter':
        return <div className="p-6"><h2 className="text-2xl font-semibold">Code Documenter</h2><p>Coming soon...</p></div>;
      default:
        return <CodeTester />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar currentPage={currentPage} onPageChange={setCurrentPage} />
      <div className="flex-1 overflow-y-auto">
        {renderPage()}
      </div>
    </div>
  );
}

export default App;
