import { useEffect, useMemo, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { UserPlus, Mail, Check, X } from "lucide-react";
import { toast } from "sonner";
import { ScrollArea } from "@/components/ui/scroll-area";
import { listFriendRequests, respondToFriendRequest, sendFriendRequest, type FriendRequest } from "@/lib/api";
import { useAuthUserId } from "@/features/auth/useAuthSession";

export default function ManageFriendshipDialog() {

    const [open, setOpen] = useState(false);
    const [email, setEmail] = useState("");
    const [requests, setRequests] = useState<FriendRequest[]>([]);
    const [loadingRequests, setLoadingRequests] = useState(false);
    const [requestsError, setRequestsError] = useState<string | null>(null);
    const [isSending, setIsSending] = useState(false);
    const userId = useAuthUserId();

    const pendingRequests = useMemo(() => requests.filter((req) => req.status === "pending"), [requests]);

    useEffect(() => {
        if (!open) {
            return;
        }
        if (!userId) {
            setRequests([]);
            setRequestsError("You must be signed in to see requests.");
            return;
        }
        let cancelled = false;
        (async () => {
            setLoadingRequests(true);
            setRequestsError(null);
            try {
                const data = await listFriendRequests(userId, "in");
                if (!cancelled) {
                    setRequests(data);
                }
            } catch (error: any) {
                if (!cancelled) {
                    const message = error?.message ?? "Failed to load requests";
                    setRequestsError(message);
                    toast.error(message);
                }
            } finally {
                if (!cancelled) {
                    setLoadingRequests(false);
                }
            }
        })();
        return () => {
            cancelled = true;
        };
    }, [open, userId]);

    const getRequesterDetails = (req: FriendRequest) => {
        const requester = req.from_user;
        const displayName = requester?.display_name || requester?.email || "Unknown user";
        const emailAddress = requester?.email || "No email available";
        const avatarUrl = requester?.avatar_url || null;
        const fallback = displayName.trim().charAt(0)?.toUpperCase() || "U";
        return { displayName, emailAddress, avatarUrl, fallback };
    };

    const handleSendRequest = () => {
        if (!email || !userId) {
            toast.error("Enter an email and ensure you are signed in.");
            return;
        }
        (async () => {
            setIsSending(true);
            try {
                await sendFriendRequest(email, userId);
                toast.success(`Invitation sent to ${email}`);
                setEmail("");
            } catch (error: any) {
                const message = error?.message ?? "Failed to send request";
                toast.error(message);
            } finally {
                setIsSending(false);
                setOpen(false);
            }
        })();
    };

    const handleRespond = (id: string, status: "accepted" | "declined") => {
        if (!userId) {
            toast.error("You must be signed in to manage requests.");
            return;
        }
        (async () => {
            try {
                await respondToFriendRequest(id, status, userId);
                setRequests((prev) => prev.filter((r) => r.id !== id));
                toast.success(status === "accepted" ? "Friend request accepted" : "Friend request declined");
            } catch (error: any) {
                const message = error?.message ?? "Failed to update request";
                toast.error(message);
            }
        })();
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Manage friendships">
                    <UserPlus className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
                </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md bg-[rgb(var(--card))] text-[rgb(var(--card-foreground))] max-h-[80vh] overflow-hidden">
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
                            disabled={!email || !userId || isSending}
                            className="shrink-0"
                        >
                            <Mail className="h-4 w-4 mr-1" />
                            {isSending ? "Sending..." : "Send"}
                        </Button>
                    </div>
                    {!userId && (
                        <p className="text-xs text-[rgb(var(--muted-foreground))] mt-1">
                            Sign in to send friend requests.
                        </p>
                    )}
                </div>

                <Separator />

                {/* Incoming Friend Requests */}
                <div className="mt-4">
                    <div className="font-medium mb-2">Incoming Friend Requests</div>
                    {!userId ? (
                        <div className="text-[rgb(var(--muted-foreground))] text-sm">Sign in to view requests.</div>
                    ) : loadingRequests ? (
                        <div className="text-[rgb(var(--muted-foreground))] text-sm">Loading requests...</div>
                    ) : requestsError ? (
                        <div className="text-[rgb(var(--destructive))] text-sm">{requestsError}</div>
                    ) : pendingRequests.length === 0 ? (
                        <div className="text-[rgb(var(--muted-foreground))] text-sm">No pending requests.</div>
                    ) : (
                        <ScrollArea className="w-full h-64" type="always">
                            <div className="flex flex-col gap-3 pr-2">
                                {pendingRequests.map((req) => {
                                    const details = getRequesterDetails(req);
                                    return (
                                        <div key={req.id} className="flex items-center justify-between bg-[rgb(var(--muted))] rounded-md px-3 py-2">
                                            <div className="flex items-center gap-3">
                                                <Avatar>
                                                    {details.avatarUrl && (
                                                        <AvatarImage src={details.avatarUrl} alt={details.displayName} />
                                                    )}
                                                    <AvatarFallback className="bg-[rgb(var(--primary))] text-white">
                                                        {details.fallback}
                                                    </AvatarFallback>
                                                </Avatar>
                                                <div className="flex flex-col">
                                                    <Badge variant="secondary">{details.displayName}</Badge>
                                                    <span className="text-[rgb(var(--muted-foreground))] text-xs">{details.emailAddress}</span>
                                                </div>
                                            </div>
                                        <div className="flex gap-1">
                                            <Button size="icon-sm" variant="default" onClick={() => handleRespond(req.id, "accepted")} aria-label="Accept">
                                                <Check className="h-4 w-4" />
                                            </Button>
                                            <Button size="icon-sm" variant="destructive" onClick={() => handleRespond(req.id, "declined")} aria-label="Decline">
                                                <X className="h-4 w-4" />
                                            </Button>
                                        </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </ScrollArea>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
