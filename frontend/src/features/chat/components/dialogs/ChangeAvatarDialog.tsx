import { useState } from 'react';
import { getStoredAccessToken, updateSessionAvatarUrl, updateSessionUserFromApi } from '@/features/auth/storage';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from '@/components/ui/dialog';

type ChangeAvatarDialogProps = {
  triggerLabel?: string;
};

export default function ChangeAvatarDialog({ triggerLabel = 'Settings' }: ChangeAvatarDialogProps) {
  const [open, setOpen] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const token = getStoredAccessToken() || '';
  const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const cacheBusted = avatarUrl ? `${avatarUrl}${avatarUrl.includes('?') ? '&' : '?'}t=${Date.now()}` : avatarUrl;
      const res = await fetch(`${apiBase}/api/users/me/avatar`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ avatar_url: cacheBusted }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || 'Failed to update avatar');
      }
      const user = await res.json();
      updateSessionAvatarUrl(user.avatar_url || cacheBusted);
      // Also refresh current user from API to align all fields
      const meRes = await fetch(`${apiBase}/api/auth/me`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (meRes.ok) {
        const me = await meRes.json();
        updateSessionUserFromApi(me);
      }
      setSuccess('Avatar updated successfully.');
      // optionally close after short delay
      setTimeout(() => setOpen(false), 800);
    } catch (e: any) {
      setError(e?.message || 'Failed to update avatar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm">{triggerLabel}</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>Change your avatar URL.</DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <label className="text-sm">Avatar URL</label>
          <input
            type="url"
            value={avatarUrl}
            onChange={(e) => setAvatarUrl(e.target.value)}
            placeholder="https://example.com/avatar.png"
            className="w-full border rounded px-3 py-2"
            required
          />
          {error && <p className="text-red-600 text-sm">{error}</p>}
          {success && <p className="text-green-600 text-sm">{success}</p>}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSave} disabled={loading}>
            {loading ? 'Saving…' : 'Save'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
