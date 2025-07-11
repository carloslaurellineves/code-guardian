import axios from 'axios';
import { 
  TestGenerationRequest, 
  GitLabTestGenerationRequest, 
  TestGenerationResponse, 
  FileUploadResponse 
} from '../types/api';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Service class using OOP approach
export class ApiService {
  /**
   * Generate tests from text input
   */
  async generateFromText(request: TestGenerationRequest): Promise<TestGenerationResponse> {
    try {
      const response = await apiClient.post('/generate/from-text', request);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Generate tests from file upload
   */
  async generateFromFile(file: File, language?: string): Promise<TestGenerationResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (language) {
        formData.append('language', language);
      }

      const response = await apiClient.post('/upload/generate-tests', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Generate tests from GitLab repository
   */
  async generateFromGitlab(request: GitLabTestGenerationRequest): Promise<TestGenerationResponse> {
    try {
      const response = await apiClient.post('/generate/from-gitlab', request);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Validate uploaded file
   */
  async validateFile(file: File): Promise<FileUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/upload/validate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Handle API errors
   */
  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Server responded with error status
        const message = error.response.data?.error || error.response.data?.message || 'API Error';
        return new Error(`${message} (Status: ${error.response.status})`);
      } else if (error.request) {
        // Request was made but no response received
        return new Error('Network error - please check your connection');
      }
    }
    return new Error('An unexpected error occurred');
  }
}

// Export singleton instance
export const apiService = new ApiService();
