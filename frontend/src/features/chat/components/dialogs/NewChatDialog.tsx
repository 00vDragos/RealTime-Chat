import { useEffect, useMemo, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageCirclePlus } from "lucide-react";

import { listMyFriends, type Friend } from "@/lib/api";

export default function NewChatDialog({ onSelect }: { onSelect: (contactIds: (number | string)[]) => void }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Array<string>>([]);
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // TODO: Replace with real authenticated user id from auth state
  const USER_ID = "1eb0fa76-fad3-4dd2-9536-ec257c29bba3";

  useEffect(() => {
    if (!open) return;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await listMyFriends(USER_ID);
        setFriends(res);
      } catch (e: any) {
        setError(e?.message ?? "Failed to load friends");
      } finally {
        setLoading(false);
      }
    })();
  }, [open]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return friends.filter(f => (f.display_name ?? f.email ?? "").toLowerCase().includes(q));
  }, [friends, search]);

  const toggleSelect = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter(cid => cid !== id) : [...prev, id]
    );
  };

  const handleStartChat = () => {
    if (selected.length > 0) {
      onSelect(selected);
      setOpen(false);
      setSelected([]);
      setSearch("");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>

      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Start new chat">
          <MessageCirclePlus className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-md bg-[rgb(var(--card))] text-[rgb(var(--card-foreground))]">

        <DialogHeader>
          <DialogTitle>Start a new chat</DialogTitle>
          <DialogDescription>
            Search and select one or more friends to start a conversation.
          </DialogDescription>
        </DialogHeader>

        <Input
          placeholder="Search contacts..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="mb-4 bg-[rgb(var(--input))] text-[rgb(var(--foreground))] placeholder-[rgb(var(--muted-foreground))] border border-[rgb(var(--border))]"
        />
        <ScrollArea className="max-h-60">
          <div className="flex flex-col gap-2 p-2">
            {loading && <div className="text-[rgb(var(--muted-foreground))] text-center">Loading...</div>}
            {error && <div className="text-[rgb(var(--destructive))] text-center">{error}</div>}
            {!loading && !error && filtered.length === 0 && <div className="text-[rgb(var(--muted-foreground))] text-center">No friends found</div>}
            {filtered.map(friend => {
              const isSelected = selected.includes(friend.id);
              const name = friend.display_name ?? friend.email;
              const initial = (name || "").trim().charAt(0).toUpperCase() || "?";
              return (
                <Button
                  key={friend.id}
                  variant={isSelected ? "secondary" : "ghost"}
                  className={`w-full flex items-center gap-3 justify-start ${isSelected ? 'ring-2 ring-[rgb(var(--primary))] ring-offset-2 ring-offset-[rgb(var(--card))]' : ''}`}
                  onClick={() => toggleSelect(friend.id)}
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    readOnly
                    className="mr-2 accent-[rgb(var(--primary))]"
                    tabIndex={-1}
                    style={{ pointerEvents: 'none' }}
                  />
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-[rgb(var(--primary))] text-white">
                      {initial}
                    </AvatarFallback>
                  </Avatar>
                  <span className="font-medium text-[rgb(var(--foreground))]">{name}</span>
                </Button>
              );
            })}
          </div>
        </ScrollArea>

        <Button
          className="mt-4 w-full bg-[rgb(var(--primary))] text-[rgb(var(--primary-foreground))] hover:bg-[rgb(var(--primary))]/90"
          disabled={selected.length === 0}
          onClick={handleStartChat}
        >
          Start Chat with {selected.length} friend{selected.length !== 1 ? 's' : ''}
        </Button>
        
      </DialogContent>
    </Dialog>
  );
}
