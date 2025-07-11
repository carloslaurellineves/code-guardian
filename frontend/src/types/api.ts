export interface TestGenerationRequest {
  code: string;
  language: string;
}

export interface GitLabTestGenerationRequest {
  repo_url: string;
  access_token?: string;
  branch?: string;
  max_files?: number;
}

export interface TestGenerationMetadata {
  input_type: 'TEXT' | 'FILE' | 'GITLAB';
  detected_language?: string;
  test_framework?: string;
  processing_time_ms?: number;
  lines_of_code?: number;
  files_processed?: number;
}

export interface TestGenerationResponse {
  success: boolean;
  generated_tests: string;
  metadata: TestGenerationMetadata;
  coverage_notes?: string;
  suggestions?: string[];
  processing_messages?: string[];
}

export interface TestGenerationErrorResponse {
  success: false;
  error: string;
  error_code: string;
  processing_messages?: string[];
}

export interface FileUploadResponse {
  filename: string;
  size: number;
  content_type: string;
  language_detected?: string;
  valid: boolean;
  message: string;
}

export type InputType = 'text' | 'file' | 'gitlab';

export interface AppState {
  currentInputType: InputType;
  isLoading: boolean;
  error: string | null;
  result: TestGenerationResponse | null;
  codeInput: string;
  isFileUploadModalOpen: boolean;
  isGitLabModalOpen: boolean;
  gitlabUrl?: string;
  selectedFiles?: File[];
}
