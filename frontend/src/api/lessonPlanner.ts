// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Types
export interface GenerateLessonPlanRequest {
  grade_level: string;
  topic: string;
  additional_criteria: string;
  standards: string;
}

export interface LessonPlanResponse {
  id: string;
  response: string;
}

export interface ExpandLessonPlanRequest {
  id: string;
  query: string;
}

export interface ExpandLessonPlanResponse {
  id: string;
  expanded_response: string;
}

export interface LessonPlanHistoryItem {
  lesson_plan_id: string;
  created_at: string;
  user_query_title: string;
  is_favorite: boolean;
}

export interface LessonPlanDetail {
  lesson_plan_id: string;
  user_query: string;
  lesson_plan: string;
  created_at: string;
  is_favorite: boolean;
  expanded_sections?: Array<{
    query: string;
    response: string;
  }>;
}

export interface FeedbackRequest {
  feedback: string;
  feedback_description: string;
}

export interface TranslateRequest {
  target_language: string;
}

export interface InteractionResponse {
  user_id: string;
  lesson_plan_interaction: number;
}

// SSE Event types
export type SSEEvent = 
  | { type: 'id'; id: string }
  | { type: 'chunk'; chunk: string }
  | { type: 'suggested_prompts'; suggested_prompts: string[] }
  | { type: 'error'; error: string }
  | { type: 'complete' };

// Generic fetch with auth
async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)['token'] = token;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// API Functions
export const lessonPlannerApi = {
  // Generate lesson plan via SSE
  generateLessonPlan: async (
    request: GenerateLessonPlanRequest,
    token: string,
    onEvent: (event: SSEEvent) => void
  ): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/lesson_planner/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'token': token,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to generate lesson plan' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    if (!reader) throw new Error('No response body');

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') continue;
            
            try {
              const parsed = JSON.parse(data);
              onEvent(parsed);
            } catch (e) {
              console.warn('Failed to parse SSE event:', data);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },

  // Expand a lesson plan section
  expandSection: (request: ExpandLessonPlanRequest, token: string) =>
    fetchWithAuth<ExpandLessonPlanResponse>('/api/lesson_planner/expand_section', {
      method: 'POST',
      body: JSON.stringify(request),
    }, token),

  // Get lesson plan history
  getHistory: (token: string) =>
    fetchWithAuth<LessonPlanHistoryItem[]>('/api/lesson_planner/history', {}, token),

  // Get specific lesson plan
  getLessonPlan: (id: string, token: string) =>
    fetchWithAuth<LessonPlanDetail>(`/api/lesson_planner/history_list/${id}`, {}, token),

  // Update feedback
  updateFeedback: (id: string, feedback: FeedbackRequest, token: string) =>
    fetchWithAuth<{ message: string }>(`/api/lesson_planner/update_feedback/${id}`, {
      method: 'PUT',
      body: JSON.stringify(feedback),
    }, token),

  // Edit history title
  editTitle: (id: string, title: string, token: string) =>
    fetchWithAuth<{ message: string }>(`/api/lesson_planner/edit_history_title/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ edited_query: title }),
    }, token),

  // Delete history
  deleteHistory: (id: string, token: string) =>
    fetchWithAuth<{ message: string }>(`/api/lesson_planner/delete_history/${id}`, {
      method: 'DELETE',
    }, token),

  // Clear all history
  clearAllHistory: (token: string) =>
    fetchWithAuth<{ message: string }>('/api/lesson_planner/clear_all_history', {
      method: 'DELETE',
    }, token),

  // Favorite/Unfavorite
  favorite: (id: string, token: string) =>
    fetchWithAuth<{ message: string }>(`/api/lesson_planner/favorite/${id}`, {
      method: 'PUT',
    }, token),

  unfavorite: (id: string, token: string) =>
    fetchWithAuth<{ message: string }>(`/api/lesson_planner/unfavorite/${id}`, {
      method: 'PUT',
    }, token),

  // Get favorites
  getFavorites: (token: string) =>
    fetchWithAuth<LessonPlanHistoryItem[]>('/api/lesson_planner/retrieve_favorites', {}, token),

  // Translate
  translate: (id: string, request: TranslateRequest, token: string, onEvent: (event: SSEEvent) => void) =>
    new Promise<void>((resolve, reject) => {
      fetch(`${API_BASE_URL}/api/lesson_planner/translate_message/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'token': token,
        },
        body: JSON.stringify(request),
      })
        .then(response => {
          if (!response.ok) throw new Error('Translation failed');
          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          
          if (!reader) throw new Error('No response body');
          
          const read = async () => {
            try {
              while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';
                
                for (const line of lines) {
                  if (line.startsWith('data: ')) {
                    const data = line.slice(6).trim();
                    if (data === '[DONE]') continue;
                    try {
                      onEvent(JSON.parse(data));
                    } catch {}
                  }
                }
              }
              resolve();
            } catch (e) {
              reject(e);
            } finally {
              reader.releaseLock();
            }
          };
          read();
        })
        .catch(reject);
    }),

  // Quick actions (summarize, simplify, etc.)
  quickAction: (id: string, action: string, token: string, onEvent: (event: SSEEvent) => void) =>
    new Promise<void>((resolve, reject) => {
      fetch(`${API_BASE_URL}/api/lesson_planner/${action}/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'token': token,
        },
      })
        .then(response => {
          if (!response.ok) throw new Error(`${action} failed`);
          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          
          if (!reader) throw new Error('No response body');
          
          const read = async () => {
            try {
              while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';
                
                for (const line of lines) {
                  if (line.startsWith('data: ')) {
                    const data = line.slice(6).trim();
                    if (data === '[DONE]') continue;
                    try {
                      onEvent(JSON.parse(data));
                    } catch {}
                  }
                }
              }
              resolve();
            } catch (e) {
              reject(e);
            } finally {
              reader.releaseLock();
            }
          };
          read();
        })
        .catch(reject);
    }),

  // Downloads
  downloadMarkdown: (id: string, token: string) =>
    fetch(`${API_BASE_URL}/api/lesson_planner/download/${id}`, {
      headers: { 'token': token || '' },
    }).then(r => r.blob()),

  downloadPdf: (id: string, token: string) =>
    fetch(`${API_BASE_URL}/api/lesson_planner/download_pdf/${id}`, {
      headers: { 'token': token || '' },
    }).then(r => r.blob()),

  downloadDocx: (id: string, token: string) =>
    fetch(`${API_BASE_URL}/api/lesson_planner/download_docx/${id}`, {
      headers: { 'token': token || '' },
    }).then(r => r.blob()),

  // Get interactions count
  getInteractions: (token: string) =>
    fetchWithAuth<InteractionResponse>('/api/lesson_planner/interactions_lesson_planner', {}, token),

  // Get input data for editing
  getInputData: (token: string) =>
    fetchWithAuth<any>('/api/lesson_planner/edit_input_data', {}, token),
};

// Helper to trigger download
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}