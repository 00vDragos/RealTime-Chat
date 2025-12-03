export type User = {
  id: string;
  email: string;
  name?: string;
  avatarUrl?: string | null;
};

export type AuthResult = {
  user: User;
  accessToken?: string;
};
