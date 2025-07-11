import React, { useState } from 'react';
import { apiService } from '../services/api';
import { AppState, InputType } from '../types/api';
import CodeEditor from '../components/CodeEditor';
import CodeOutput from '../components/CodeOutput';
import Modal from '../components/Modal';

const CodeTester: React.FC = () => {
  const [state, setState] = useState<AppState>({
    currentInputType: 'text',
    isLoading: false,
    error: null,
    result: null,
    codeInput: '',
    isFileUploadModalOpen: false,
    isGitLabModalOpen: false,
  });

  const handleInputTypeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newInputType = event.target.value as InputType;
    setState({ ...state, currentInputType: newInputType });
    
    // Open appropriate modal for file upload or GitLab
    if (newInputType === 'file') {
      setState(prev => ({ ...prev, currentInputType: newInputType, isFileUploadModalOpen: true }));
    } else if (newInputType === 'gitlab') {
      setState(prev => ({ ...prev, currentInputType: newInputType, isGitLabModalOpen: true }));
    }
  };

  const handleInputChange = (value: string) => {
    setState({ ...state, codeInput: value });
  };

  const handleFileUploadModalToggle = () => {
    setState({ ...state, isFileUploadModalOpen: !state.isFileUploadModalOpen });
  };

  const handleGitLabModalToggle = () => {
    setState({ ...state, isGitLabModalOpen: !state.isGitLabModalOpen });
  };
  
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      setState({ ...state, selectedFiles: Array.from(files) });
    }
  };
  
  const handleGitLabUrlChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setState({ ...state, gitlabUrl: event.target.value });
  };
  
  const handleGitLabSubmit = () => {
    if (state.gitlabUrl) {
      setState({ ...state, isGitLabModalOpen: false });
      // Here you would typically trigger the GitLab processing
    }
  };
  
  const handleFileUploadSubmit = () => {
    if (state.selectedFiles && state.selectedFiles.length > 0) {
      setState({ ...state, isFileUploadModalOpen: false });
      // Here you would typically trigger the file processing
    }
  };

  const handlePreview = async () => {
    setState({ ...state, isLoading: true, error: null });
    try {
      let response;
      switch (state.currentInputType) {
        case 'text':
          response = await apiService.generateFromText({
            code: state.codeInput,
            language: 'javascript',
          });
          break;
        case 'file':
          // Note: Placeholder for file upload logic
          throw new Error('File upload not implemented yet');
        case 'gitlab':
          // Note: Placeholder for GitLab logic
          throw new Error('GitLab integration not implemented yet');
        default:
          throw new Error('Invalid input type');
      }
      setState({ ...state, isLoading: false, result: response || null });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      setState({ ...state, isLoading: false, error: errorMessage });
    }
  };

  return (
    <div className="p-6 flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Code Tester</h2>
        <div>
          <select className="border rounded p-2" onChange={handleInputTypeChange}>
            <option value="text">Direct Input</option>
            <option value="file">File Upload</option>
            <option value="gitlab">GitLab Repository</option>
          </select>
        </div>
      </div>
      {/* Direct Input Layout */}
      {state.currentInputType === 'text' && (
        <div className="flex flex-col gap-4 h-[calc(100vh-200px)]">
          <div className="flex-1 bg-white p-4 shadow-md rounded-lg">
            <CodeEditor
              value={state.codeInput}
              onChange={handleInputChange}
              label="Input Code"
            />
          </div>
          
          {/* Preview button positioned between the text areas */}
          <div className="flex justify-center items-center gap-4">
            <button 
              onClick={handlePreview} 
              className="bg-guardian-blue text-white px-8 py-3 rounded-lg hover:bg-guardian-blue/80 transition-colors"
              disabled={state.isLoading}
            >
              {state.isLoading ? 'Generating...' : 'Preview ➔'}
            </button>
            
            {state.isLoading && (
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-guardian-blue"></div>
                <span className="text-sm text-gray-600">Loading...</span>
              </div>
            )}
          </div>
          
          <div className="flex-1 bg-white p-4 shadow-md rounded-lg">
            <CodeOutput
              value={state.result?.generated_tests || ''}
              label="Generated Tests"
            />
          </div>
          
          {/* Error message below the output */}
          {state.error && (
            <div className="flex justify-center">
              <p className="text-red-500 text-sm bg-red-50 px-4 py-2 rounded-lg">Error: {state.error}</p>
            </div>
          )}
        </div>
      )}
      
      {/* File Upload and GitLab placeholders */}
      {state.currentInputType === 'file' && (
        <div className="flex items-center justify-center h-64 bg-gray-100 rounded-lg">
          <p className="text-gray-500">File upload mode selected. Use the modal to upload files.</p>
        </div>
      )}
      
      {state.currentInputType === 'gitlab' && (
        <div className="flex items-center justify-center h-64 bg-gray-100 rounded-lg">
          <p className="text-gray-500">GitLab repository mode selected. Use the modal to enter repository URL.</p>
        </div>
      )}
      

      {/* File Upload Modal */}
      <Modal
        isOpen={state.isFileUploadModalOpen}
        onClose={handleFileUploadModalToggle}
        title="Upload Files"
        className="max-w-lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select files to upload
            </label>
            <input
              type="file"
              multiple
              accept=".js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.cs,.php,.rb,.go,.rs,.swift,.kt"
              onChange={handleFileUpload}
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          {state.selectedFiles && state.selectedFiles.length > 0 && (
            <div className="bg-gray-50 p-3 rounded-md">
              <p className="text-sm font-medium text-gray-700 mb-1">Selected files:</p>
              <ul className="text-sm text-gray-600">
                {state.selectedFiles.map((file, index) => (
                  <li key={index} className="flex justify-between">
                    <span>{file.name}</span>
                    <span className="text-gray-400">({(file.size / 1024).toFixed(1)} KB)</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="flex justify-end gap-2 pt-4">
            <button
              onClick={handleFileUploadModalToggle}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleFileUploadSubmit}
              disabled={!state.selectedFiles || state.selectedFiles.length === 0}
              className="px-4 py-2 bg-guardian-blue text-white rounded-md hover:bg-guardian-blue/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Upload
            </button>
          </div>
        </div>
      </Modal>

      {/* GitLab Modal */}
      <Modal
        isOpen={state.isGitLabModalOpen}
        onClose={handleGitLabModalToggle}
        title="GitLab Repository"
        className="max-w-lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              GitLab Repository URL
            </label>
            <input
              type="url"
              value={state.gitlabUrl || ''}
              onChange={handleGitLabUrlChange}
              placeholder="https://gitlab.com/username/repository"
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <div className="text-sm text-gray-600">
            <p>Make sure the repository is publicly accessible or you have appropriate permissions.</p>
          </div>
          
          <div className="flex justify-end gap-2 pt-4">
            <button
              onClick={handleGitLabModalToggle}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleGitLabSubmit}
              disabled={!state.gitlabUrl || state.gitlabUrl.trim() === ''}
              className="px-4 py-2 bg-guardian-blue text-white rounded-md hover:bg-guardian-blue/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Submit
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default CodeTester;
