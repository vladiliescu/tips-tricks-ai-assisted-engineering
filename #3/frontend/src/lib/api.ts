/**
 * API client for GitHub Predictive Analytics backend
 *
 * This module provides a typed interface for communicating with the FastAPI backend.
 * It handles request/response formatting, error handling, and type safety.
 */

import { browser } from '$app/environment';

// Configuration
const API_BASE_URL = browser ? 'http://localhost:8000' : 'http://localhost:8000';

// Types
export interface ApiError {
    message: string;
    detail?: string;
    status: number;
}

export interface Repository {
    id: number;
    github_id: number;
    name: string;
    full_name: string;
    description?: string;
    url: string;
    language?: string;
    stargazers_count: number;
    forks_count: number;
    open_issues_count: number;
    is_private: boolean;
    created_at: string;
    last_synced_at?: string;
}

export interface Issue {
    id: number;
    github_id: number;
    number: number;
    title: string;
    state: string;
    labels?: string;
    created_at: string;
    closed_at?: string;
    estimated_hours?: number;
    actual_hours?: number;
    story_points?: number;
    resolution_time_hours?: number;
}

export interface Team {
    id: number;
    name: string;
    description?: string;
    is_active: boolean;
    current_size: number;
    average_velocity?: number;
    average_cycle_time_hours?: number;
    estimation_accuracy_score?: number;
    created_at: string;
    updated_at: string;
}

export interface TeamMember {
    id: number;
    name: string;
    email?: string;
    github_username?: string;
    seniority_level: 'junior' | 'mid' | 'senior' | 'lead' | 'principal';
    years_of_experience?: number;
    is_active: boolean;
    tenure_months?: number;
    joined_team_at: string;
}

export interface Prediction {
    id: number;
    task_title: string;
    task_description?: string;
    prediction_type: 'story_points' | 'hours' | 'complexity' | 'risk_score';
    predicted_value: number;
    confidence_score?: number;
    confidence_interval_lower?: number;
    confidence_interval_upper?: number;
    status: 'pending' | 'completed' | 'validated' | 'failed';
    created_at: string;
    model_id: number;
    model_name?: string;
}

export interface PredictionRequest {
    task_title: string;
    task_description?: string;
    task_type?: string;
    team_id?: number;
    repository_id?: number;
    prediction_type?: 'story_points' | 'hours' | 'complexity' | 'risk_score';
    context?: Record<string, any>;
}

export interface ValidationRequest {
    actual_value: number;
    validation_source?: string;
    notes?: string;
}

export interface SyncRequest {
    repository_full_name: string;
    github_token?: string;
}

export interface DashboardSummary {
    period_days: number;
    period_start: string;
    period_end: string;
    team_metrics: {
        active_teams: number;
        total_members: number;
    };
    prediction_metrics: {
        recent_predictions: number;
        validated_predictions: number;
        validation_rate: number;
    };
    repository_metrics: {
        total_repositories: number;
        recent_issues: number;
        issues_closed: number;
        close_rate: number;
    };
    model_metrics: {
        active_models: number;
        total_models: number;
    };
}

// Base API client class
class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;

        const config: RequestInit = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw {
                    message: errorData.message || `HTTP ${response.status}`,
                    detail: errorData.detail || response.statusText,
                    status: response.status,
                } as ApiError;
            }

            return await response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                throw {
                    message: 'Network error - cannot connect to server',
                    detail: 'Please check if the backend server is running',
                    status: 0,
                } as ApiError;
            }
            throw error;
        }
    }

    async get<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'GET' });
    }

    async post<T>(endpoint: string, data?: any): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    async put<T>(endpoint: string, data?: any): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    async delete<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'DELETE' });
    }
}

// Create singleton instance
export const api = new ApiClient();

// API methods organized by domain

// Health check
export const healthApi = {
    check: () => api.get<{ status: string; version: string }>('/health'),
    github: () => api.get<{ status: string; github_api_url: string; has_token: boolean }>('/api/v1/github/health'),
    teams: () => api.get<{ status: string; service: string }>('/api/v1/teams/health'),
    predictions: () => api.get<{ status: string; service: string }>('/api/v1/predictions/health'),
    analytics: () => api.get<{ status: string; service: string }>('/api/v1/analytics/health'),
};

// GitHub API
export const githubApi = {
    listRepositories: (skip = 0, limit = 100) =>
        api.get<Repository[]>(`/api/v1/github/repositories?skip=${skip}&limit=${limit}`),

    getRepository: (id: number) =>
        api.get<Repository>(`/api/v1/github/repositories/${id}`),

    listRepositoryIssues: (repoId: number, skip = 0, limit = 100, state?: string) => {
        const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
        if (state) params.append('state', state);
        return api.get<Issue[]>(`/api/v1/github/repositories/${repoId}/issues?${params}`);
    },

    syncRepository: (data: SyncRequest) =>
        api.post<{ message: string; repository_id: number; issues_synced: number; pull_requests_synced: number; commits_synced: number }>('/api/v1/github/repositories/sync', data),

    getRepositoryAnalytics: (repoId: number) =>
        api.get<{
            repository_name: string;
            total_issues: number;
            open_issues: number;
            closed_issues: number;
            open_percentage: number;
            average_resolution_time_hours?: number;
            last_synced_at?: string;
        }>(`/api/v1/github/repositories/${repoId}/analytics`),
};

// Teams API
export const teamsApi = {
    listTeams: (skip = 0, limit = 100, activeOnly = true) =>
        api.get<Team[]>(`/api/v1/teams?skip=${skip}&limit=${limit}&active_only=${activeOnly}`),

    createTeam: (data: { name: string; description?: string }) =>
        api.post<Team>('/api/v1/teams', data),

    getTeam: (id: number) =>
        api.get<Team>(`/api/v1/teams/${id}`),

    updateTeam: (id: number, data: Partial<Pick<Team, 'name' | 'description' | 'is_active'>>) =>
        api.put<Team>(`/api/v1/teams/${id}`, data),

    deleteTeam: (id: number) =>
        api.delete<{ message: string }>(`/api/v1/teams/${id}`),

    listTeamMembers: (teamId: number, activeOnly = true) =>
        api.get<TeamMember[]>(`/api/v1/teams/${teamId}/members?active_only=${activeOnly}`),

    addTeamMember: (teamId: number, data: {
        name: string;
        email?: string;
        github_username?: string;
        seniority_level?: TeamMember['seniority_level'];
        years_of_experience?: number;
        hourly_rate?: number;
    }) => api.post<TeamMember>(`/api/v1/teams/${teamId}/members`, data),

    getTeamMember: (teamId: number, memberId: number) =>
        api.get<TeamMember>(`/api/v1/teams/${teamId}/members/${memberId}`),

    updateTeamMember: (teamId: number, memberId: number, data: Partial<TeamMember>) =>
        api.put<TeamMember>(`/api/v1/teams/${teamId}/members/${memberId}`, data),

    removeTeamMember: (teamId: number, memberId: number) =>
        api.delete<{ message: string }>(`/api/v1/teams/${teamId}/members/${memberId}`),

    getTeamAnalytics: (teamId: number) =>
        api.get<{
            team_name: string;
            team_size: number;
            seniority_distribution: Record<string, number>;
            average_years_experience?: number;
            average_velocity?: number;
            average_cycle_time_hours?: number;
            estimation_accuracy_score?: number;
            technology_summary: Record<string, any>;
            is_active: boolean;
        }>(`/api/v1/teams/${teamId}/analytics`),
};

// Predictions API
export const predictionsApi = {
    createPrediction: (data: PredictionRequest) =>
        api.post<Prediction>('/api/v1/predictions/predict', data),

    listPredictions: (params?: {
        skip?: number;
        limit?: number;
        team_id?: number;
        repository_id?: number;
        status?: string;
        prediction_type?: string;
    }) => {
        const queryParams = new URLSearchParams();
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) {
                    queryParams.append(key, value.toString());
                }
            });
        }
        const query = queryParams.toString();
        return api.get<Prediction[]>(`/api/v1/predictions${query ? `?${query}` : ''}`);
    },

    getPrediction: (id: number) =>
        api.get<Prediction>(`/api/v1/predictions/${id}`),

    validatePrediction: (id: number, data: ValidationRequest) =>
        api.post<{
            message: string;
            prediction_id: number;
            predicted_value: number;
            actual_value: number;
            accuracy_percentage?: number;
            absolute_error?: number;
        }>(`/api/v1/predictions/${id}/validate`, data),

    getAccuracyAnalytics: (params?: {
        team_id?: number;
        prediction_type?: string;
        days?: number;
    }) => {
        const queryParams = new URLSearchParams();
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) {
                    queryParams.append(key, value.toString());
                }
            });
        }
        const query = queryParams.toString();
        return api.get<{
            period_days: number;
            total_predictions: number;
            validated_predictions: number;
            average_accuracy_percentage?: number;
            average_absolute_error?: number;
            predictions_within_10_percent: number;
            predictions_within_25_percent: number;
            predictions_within_50_percent: number;
            accuracy_distribution: {
                within_10_percent_rate: number;
                within_25_percent_rate: number;
                within_50_percent_rate: number;
            };
        }>(`/api/v1/predictions/analytics/accuracy${query ? `?${query}` : ''}`),
};

// Analytics API
export const analyticsApi = {
    getDashboardSummary: (teamId?: number, days = 7) => {
        const params = new URLSearchParams({ days: days.toString() });
        if (teamId) params.append('team_id', teamId.toString());
        return api.get<DashboardSummary>(`/api/v1/analytics/dashboard/summary?${params}`);
    },

    getTeamVelocity: (teamId?: number, days = 30) => {
        const params = new URLSearchParams({ days: days.toString() });
        if (teamId) params.append('team_id', teamId.toString());
        return api.get<Array<{
            team_id: number;
            team_name: string;
            period_start: string;
            period_end: string;
            total_story_points_completed?: number;
            total_hours_logged?: number;
            velocity_per_day?: number;
            estimation_accuracy?: number;
        }>>(`/api/v1/analytics/teams/velocity?${params}`);
    },

    getRepositoryInsights: (repositoryId?: number, days = 30) => {
        const params = new URLSearchParams({ days: days.toString() });
        if (repositoryId) params.append('repository_id', repositoryId.toString());
        return api.get<Array<{
            repository_id: number;
            repository_name: string;
            total_issues: number;
            open_issues: number;
            closed_issues: number;
            average_resolution_time_hours?: number;
            most_common_labels: Array<{ label: string; count: number }>;
            contributor_count: number;
        }>>(`/api/v1/analytics/repositories/insights?${params}`);
    },

    getPredictionAnalytics: (teamId?: number, days = 30) => {
        const params = new URLSearchParams({ days: days.toString() });
        if (teamId) params.append('team_id', teamId.toString());
        return api.get<{
            total_predictions: number;
            validated_predictions: number;
            average_accuracy?: number;
            accuracy_by_type: Record<string, number>;
            accuracy_trends: Array<{
                week_start: string;
                week_end: string;
                predictions_count: number;
                average_accuracy?: number;
            }>;
        }>(`/api/v1/analytics/predictions/analytics?${params}`);
    },

    getTeamPerformance: (teamId: number, days = 30) =>
        api.get<{
            team_name: string;
            team_id: number;
            period_start: string;
            period_end: string;
            prediction_metrics: {
                total_predictions: number;
                validated_predictions: number;
                validation_rate: number;
                average_accuracy?: number;
                prediction_distribution: Record<string, number>;
            };
            sprint_metrics: Array<{
                sprint_name: string;
                start_date: string;
                end_date: string;
                planned_story_points?: number;
                completed_story_points?: number;
                completion_percentage?: number;
                velocity?: number;
                estimation_accuracy?: number;
            }>;
            team_composition: {
                total_members: number;
                seniority_distribution: Record<string, number>;
            };
        }>(`/api/v1/analytics/teams/${teamId}/performance?days=${days}`),
};

// Utility functions
export function isApiError(error: unknown): error is ApiError {
    return typeof error === 'object' && error !== null && 'message' in error && 'status' in error;
}

export function formatApiError(error: unknown): string {
    if (isApiError(error)) {
        return error.detail || error.message;
    }
    if (error instanceof Error) {
        return error.message;
    }
    return 'An unknown error occurred';
}

export function handleApiError(error: unknown): never {
    console.error('API Error:', error);
    throw error;
}
