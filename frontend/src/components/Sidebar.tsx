import React from 'react';

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, onPageChange }) => {
  const menuItems = [
    { id: 'home', label: 'Home', icon: '🏠' },
    { id: 'story-creator', label: 'Story Creator', icon: '📝' },
    { id: 'code-documenter', label: 'Code Documenter', icon: '📋' },
    { id: 'code-tester', label: 'Code Tester', icon: '🧪' },
  ];

  return (
    <div className="bg-guardian-light-blue h-screen w-64 p-6 flex flex-col">
      {/* Header */}
      <div className="flex items-center mb-8">
        <div className="bg-white p-2 rounded-lg mr-3">
          <span className="text-2xl">🛡️</span>
        </div>
        <h1 className="text-xl font-semibold text-guardian-text">Code Guardian</h1>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => onPageChange(item.id)}
                className={`w-full flex items-center px-4 py-3 rounded-lg text-left transition-colors duration-200 ${
                  currentPage === item.id
                    ? 'bg-white text-guardian-text font-medium shadow-sm'
                    : 'text-guardian-text hover:bg-white hover:bg-opacity-50'
                }`}
              >
                <span className="mr-3 text-lg">{item.icon}</span>
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="mt-auto">
        <div className="text-sm text-guardian-dark-gray">
          <div className="font-medium">COE Qualidade</div>
          <div>Product</div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;

