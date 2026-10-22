import axios from 'axios';
import {
  User,
  Company,
  CreditProduct,
  ApplicationListItem,
  ApplicationDetail,
  CreditDecision,
  DocumentItem,
  InAppNotification,
  DemoScenario,
} from '../types';

const API_BASE = '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach token if present in localStorage
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('alfa_token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Handle 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't auto-redirect on login check
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('alfa_token');
        localStorage.removeItem('alfa_user');
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (username: string, password: string) => {
    const res = await apiClient.post<{ token: string; user: User; message: string }>('/auth/login/', {
      username,
      password,
    });
    return res.data;
  },
  register: async (data: any) => {
    const res = await apiClient.post<{ token: string; user: User; message: string }>('/auth/register/', data);
    return res.data;
  },
  getMe: async () => {
    const res = await apiClient.get<User>('/auth/me/');
    return res.data;
  },
  logout: async () => {
    try {
      await apiClient.post('/auth/logout/');
    } finally {
      localStorage.removeItem('alfa_token');
      localStorage.removeItem('alfa_user');
    }
  },
};

// Companies API
export const companyApi = {
  list: async () => {
    const res = await apiClient.get<Company[]>('/companies/');
    return res.data;
  },
  get: async (id: number) => {
    const res = await apiClient.get<Company>(`/companies/${id}/`);
    return res.data;
  },
  lookupByInn: async (inn: string) => {
    const res = await apiClient.get<Partial<Company>>(`/companies/lookup/?inn=${encodeURIComponent(inn)}`);
    return res.data;
  },
  create: async (data: Partial<Company>) => {
    const res = await apiClient.post<Company>('/companies/', data);
    return res.data;
  },
  updateFinancials: async (companyId: number, data: any) => {
    const res = await apiClient.post(`/companies/${companyId}/financials/`, data);
    return res.data;
  },
};

// Products API
export const productApi = {
  list: async () => {
    const res = await apiClient.get<CreditProduct[]>('/products/');
    return res.data;
  },
  get: async (id: number) => {
    const res = await apiClient.get<CreditProduct>(`/products/${id}/`);
    return res.data;
  },
  calculate: async (productId: number, amount: number, termMonths: number) => {
    const res = await apiClient.post('/products/calculate/', {
      product_id: productId,
      amount,
      term_months: termMonths,
    });
    return res.data;
  },
};

// Applications API
export const applicationApi = {
  list: async (params?: { status?: string; search?: string }) => {
    const res = await apiClient.get<{ results: ApplicationListItem[]; count: number } | ApplicationListItem[]>(
      '/applications/',
      { params }
    );
    // DRF may paginate
    if (Array.isArray(res.data)) return res.data;
    return res.data.results || [];
  },
  get: async (id: number) => {
    const res = await apiClient.get<ApplicationDetail>(`/applications/${id}/`);
    return res.data;
  },
  create: async (data: {
    company: number;
    product: number;
    requested_amount: number;
    term_months: number;
    purpose: string;
    additional_comments?: string;
    auto_submit?: boolean;
  }) => {
    const res = await apiClient.post('/applications/', data);
    return res.data;
  },
  update: async (id: number, data: any) => {
    const res = await apiClient.patch(`/applications/${id}/`, data);
    return res.data;
  },
  submit: async (id: number) => {
    const res = await apiClient.post<ApplicationDetail>(`/applications/${id}/submit/`);
    return res.data;
  },
  provideInfo: async (id: number, comment: string) => {
    const res = await apiClient.post<ApplicationDetail>(`/applications/${id}/provide-info/`, { comment });
    return res.data;
  },
  getQueue: async (statusGroup = 'all') => {
    const res = await apiClient.get<{
      counts: {
        total: number;
        manual_review: number;
        additional_info: number;
        offer_ready: number;
        completed: number;
        rejected: number;
        drafts: number;
      };
      applications: ApplicationListItem[];
    }>('/applications/queue/', { params: { status_group: statusGroup } });
    return res.data;
  },
};

// Decisions API
export const decisionApi = {
  get: async (appId: number) => {
    const res = await apiClient.get<CreditDecision>(`/decisions/application/${appId}/`);
    return res.data;
  },
  applyManual: async (
    appId: number,
    data: {
      decision_type: 'APPROVED' | 'COUNTER_OFFER' | 'ADDITIONAL_INFO_REQUIRED' | 'REJECTED';
      approved_amount?: number;
      approved_term_months?: number;
      approved_rate?: number;
      notes?: string;
      reasons?: string[];
    }
  ) => {
    const res = await apiClient.post<CreditDecision>(`/decisions/application/${appId}/manual/`, data);
    return res.data;
  },
  clientRespond: async (appId: number, accept: boolean) => {
    const res = await apiClient.post(`/decisions/application/${appId}/respond/`, { accept });
    return res.data;
  },
};

// Documents API
export const documentApi = {
  list: async (applicationId?: number) => {
    const res = await apiClient.get<DocumentItem[]>('/documents/', {
      params: applicationId ? { application_id: applicationId } : {},
    });
    return Array.isArray(res.data) ? res.data : (res.data as any).results || [];
  },
  upload: async (formData: FormData) => {
    const res = await apiClient.post<DocumentItem>('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  verify: async (docId: number, isVerified: boolean, notes: string) => {
    const res = await apiClient.post<DocumentItem>(`/documents/${docId}/verify/`, {
      is_verified: isVerified,
      verification_notes: notes,
    });
    return res.data;
  },
};

// Notifications API
export const notificationApi = {
  list: async () => {
    const res = await apiClient.get<InAppNotification[]>('/notifications/');
    return Array.isArray(res.data) ? res.data : (res.data as any).results || [];
  },
  markRead: async (id: number) => {
    await apiClient.post(`/notifications/${id}/read/`);
  },
  markAllRead: async () => {
    await apiClient.post('/notifications/read-all/');
  },
};

// Demo API
export const demoApi = {
  getScenarios: async () => {
    const res = await apiClient.get<{ scenarios: DemoScenario[] }>('/demo/scenarios/');
    return res.data.scenarios;
  },
  reset: async () => {
    const res = await apiClient.post<{ message: string; users: string[]; applications: string[] }>('/demo/reset/');
    return res.data;
  },
  quickLogin: async (username: string) => {
    const res = await apiClient.post<{ token: string; user: User; message: string }>('/demo/quick-login/', {
      username,
    });
    return res.data;
  },
};
