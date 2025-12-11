import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export type RenameGroupDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  value: string;
  onChange: (value: string) => void;
  error: string | null;
  loading: boolean;
  onSubmit: () => void;
};

export default function RenameGroupDialog({
  open,
  onOpenChange,
  value,
  onChange,
  error,
  loading,
  onSubmit,
}: RenameGroupDialogProps) {
  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
    >
      <DialogContent className="bg-[rgb(var(--card))] text-[rgb(var(--card-foreground))]">
        <DialogHeader>
          <DialogTitle>Edit group</DialogTitle>
          <DialogDescription>
            Update this conversation&apos;s name for all participants.
          </DialogDescription>
        </DialogHeader>
        <Input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Group name"
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button onClick={onSubmit} disabled={loading}>
            {loading ? "Saving..." : "Save"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
