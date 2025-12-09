import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import type { Friend } from "@/lib/api";

type Props = {
  friend: Friend;
  selected: boolean;
  onToggle: (id: string) => void;
};

export function FriendListItem({ friend, selected, onToggle }: Props) {
  const name = friend.display_name ?? friend.email;
  const initial = (name || "").trim().charAt(0).toUpperCase() || "?";
  return (
    <Button
      key={friend.id}
      variant={selected ? "secondary" : "ghost"}
      className={`w-full flex items-center gap-3 justify-start ${selected ? 'ring-2 ring-[rgb(var(--primary))] ring-offset-2 ring-offset-[rgb(var(--card))]' : ''}`}
      onClick={() => onToggle(friend.id)}
    >
      <input
        type="checkbox"
        checked={selected}
        readOnly
        className="mr-2 accent-[rgb(var(--primary))]"
        tabIndex={-1}
        style={{ pointerEvents: 'none' }}
      />
      <Avatar className="h-8 w-8">
        <AvatarFallback className="bg-[rgb(var(--primary))] text-white">{initial}</AvatarFallback>
      </Avatar>
      <span className="font-medium text-[rgb(var(--foreground))]">{name}</span>
    </Button>
  );
}
