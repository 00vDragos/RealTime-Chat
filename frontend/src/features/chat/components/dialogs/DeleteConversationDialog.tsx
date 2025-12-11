import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export type DeleteConversationDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  error: string | null;
  loading: boolean;
  onConfirm: () => void;
};

export default function DeleteConversationDialog({
  open,
  onOpenChange,
  error,
  loading,
  onConfirm,
}: DeleteConversationDialogProps) {
  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
    >
      <DialogContent className="bg-[rgb(var(--card))] text-[rgb(var(--card-foreground))]">
        <DialogHeader>
          <DialogTitle>Delete conversation</DialogTitle>
          <DialogDescription>
            This permanently removes the conversation and all of its messages for every participant.
          </DialogDescription>
        </DialogHeader>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
