export type ApiUser = {
  id: string;
  email: string;
  display_name?: string | null;
  avatar_url?: string | null;
  provider?: string | null;
  provider_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type AuthResult = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: ApiUser;
};

export type SessionUser = {
  id: string;
  email: string;
  displayName?: string | null;
  avatarUrl?: string | null;
  provider?: string | null;
  providerSub?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
};

export type AuthSession = {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  user: SessionUser;
};
