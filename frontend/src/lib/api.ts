const getBase = () =>
  typeof window !== 'undefined'
    ? '' // use Next.js rewrite: /api -> backend
    : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

export async function login(username: string, password: string): Promise<{ access_token: string }> {
  const res = await fetch(`${getBase()}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Login failed');
  }
  return res.json();
}

export async function getCars(token: string): Promise<Car[]> {
  const res = await fetch(`${getBase()}/api/cars`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    if (res.status === 401) throw new Error('Unauthorized');
    throw new Error('Failed to load cars');
  }
  return res.json();
}

export interface Car {
  id: number;
  make: string | null;
  model: string | null;
  year: number | null;
  price: number | null;
  color: string | null;
  link: string;
}
