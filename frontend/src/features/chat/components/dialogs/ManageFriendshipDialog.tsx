import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { UserPlus, Mail, Check, X } from "lucide-react";
import { toast } from "sonner";

import { initialFriendRequests } from "@/features/chat/mockData";

export default function ManageFriendshipDialog() {

    const [open, setOpen] = useState(false);
    const [email, setEmail] = useState("");
    const [requests, setRequests] = useState(initialFriendRequests);

    const handleSendRequest = () => {
        if (!email) return;
        setOpen(false);
        toast.success(`Invitation sent to ${email}`);
        setEmail("");
    };

    const handleAccept = (id: number) => {
        setRequests((prev) => prev.filter((r) => r.id !== id));
        // Here you would call your API to accept the request
    };

    const handleDecline = (id: number) => {
        setRequests((prev) => prev.filter((r) => r.id !== id));
        // Here you would call your API to decline the request
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Manage friendships">
                    <UserPlus className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
                </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md bg-[rgb(var(--card))] text-[rgb(var(--card-foreground))]">
                <DialogHeader>
                    <DialogTitle>Manage Friendships</DialogTitle>
                </DialogHeader>

                {/* Send Friend Request */}
                <div className="mb-4">
                    <div className="font-medium mb-2">Send Friend Request</div>
                    <div className="flex gap-2">
                        <Input
                            type="email"
                            placeholder="Enter email address"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            className="bg-[rgb(var(--input))] text-[rgb(var(--foreground))] placeholder-[rgb(var(--muted-foreground))] border border-[rgb(var(--border))]"
                        />
                        <Button
                            variant="default"
                            onClick={handleSendRequest}
                            disabled={!email}
                            className="shrink-0"
                        >
                            <Mail className="h-4 w-4 mr-1" /> Send
                        </Button>
                    </div>
                </div>

                <Separator />

                {/* Incoming Friend Requests */}
                <div className="mt-4">
                    <div className="font-medium mb-2">Incoming Friend Requests</div>
                    {requests.length === 0 ? (
                        <div className="text-[rgb(var(--muted-foreground))] text-sm">No pending requests.</div>
                    ) : (
                        <div className="flex flex-col gap-3">
                            {requests.map((req) => (
                                <div key={req.id} className="flex items-center justify-between bg-[rgb(var(--muted))] rounded-md px-3 py-2">
                                    <div className="flex items-center gap-3">
                                        <Avatar>
                                            <AvatarFallback className="bg-[rgb(var(--primary))] text-white">{req.avatar}</AvatarFallback>
                                        </Avatar>
                                        <Badge variant="secondary">{req.name}</Badge>
                                        <span className="text-[rgb(var(--muted-foreground))] text-xs">{req.email}</span>
                                    </div>
                                    <div className="flex gap-1">
                                        <Button size="icon-sm" variant="default" onClick={() => handleAccept(req.id)} aria-label="Accept">
                                            <Check className="h-4 w-4" />
                                        </Button>
                                        <Button size="icon-sm" variant="destructive" onClick={() => handleDecline(req.id)} aria-label="Decline">
                                            <X className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
