import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageCirclePlus } from "lucide-react";

import { contacts } from "../../mockData";

export default function NewChatDialog({ onSelect }: { onSelect: (contactIds: number[]) => void }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<number[]>([]);

  const filtered = contacts.filter(c => c.name.toLowerCase().includes(search.toLowerCase()));

  const toggleSelect = (id: number) => {
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
        </DialogHeader>

        <Input
          placeholder="Search contacts..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="mb-4 bg-[rgb(var(--input))] text-[rgb(var(--foreground))] placeholder-[rgb(var(--muted-foreground))] border border-[rgb(var(--border))]"
        />
        <ScrollArea className="max-h-60">
          <div className="flex flex-col gap-2 p-2">
            {filtered.length === 0 && <div className="text-[rgb(var(--muted-foreground))] text-center">No contacts found</div>}
            {filtered.map(contact => {
              const isSelected = selected.includes(contact.id);
              return (
                <Button
                  key={contact.id}
                  variant={isSelected ? "secondary" : "ghost"}
                  className={`w-full flex items-center gap-3 justify-start ${isSelected ? 'ring-2 ring-[rgb(var(--primary))] ring-offset-2 ring-offset-[rgb(var(--card))]' : ''}`}
                  onClick={() => toggleSelect(contact.id)}
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
                    <AvatarFallback className="bg-[rgb(var(--primary))] text-[rgb(var(--primary-foreground))]">
                      {contact.avatar}
                    </AvatarFallback>
                  </Avatar>
                  <span className="font-medium text-[rgb(var(--foreground))]">{contact.name}</span>
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
          Start Chat with {selected.length} contact{selected.length !== 1 ? 's' : ''}
        </Button>
        
      </DialogContent>
    </Dialog>
  );
}
