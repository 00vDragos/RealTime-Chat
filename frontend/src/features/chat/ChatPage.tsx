import { useState } from "react";
import SideBar from "./components/layout/SideBar";
import Navbar from "./components/layout/NavBar";
import MessagesList from "./components/ui/MessagesList";
import MessagesInput from "./components/ui/MessagesInput";
import TypingIndicator from "./components/ui/TypingIndicator";
import { useChatMessages } from "../../hooks/useChatMessages";
import { useConversations } from "../../hooks/useConversations";
import RenameGroupDialog from "./components/dialogs/RenameGroupDialog";
import DeleteConversationDialog from "./components/dialogs/DeleteConversationDialog";

export default function ChatPage() {
    const { conversations, refetch } = useConversations([]);
    const {
        chatsState,
        selectedChatId,
        setSelectedChatId,
        selectedChat,
        messageInput,
        setMessageInput,
        editingMessageId,
        handleEditStart,
        handleSend,
        handleDelete,
        handleReaction,
        renameConversation,
        deleteConversation,
        typingParticipants,
    } = useChatMessages(conversations);

    const [renameDialogOpen, setRenameDialogOpen] = useState(false);
    const [renameValue, setRenameValue] = useState("");
    const [renameError, setRenameError] = useState<string | null>(null);
    const [renameLoading, setRenameLoading] = useState(false);

    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [deleteError, setDeleteError] = useState<string | null>(null);
    const [deleteLoading, setDeleteLoading] = useState(false);

    const openRenameDialog = () => {
        if (!selectedChat || selectedChat.friendId !== null) return;
        setRenameValue(selectedChat.name ?? "");
        setRenameError(null);
        setRenameDialogOpen(true);
    };

    const handleRenameSubmit = async () => {
        if (!selectedChatId) return;
        setRenameLoading(true);
        setRenameError(null);
        try {
            await renameConversation(selectedChatId, renameValue);
            setRenameDialogOpen(false);
        } catch (error: any) {
            setRenameError(error?.message ?? "Failed to update conversation");
        } finally {
            setRenameLoading(false);
        }
    };

    const openDeleteDialog = () => {
        if (!selectedChatId) return;
        setDeleteError(null);
        setDeleteDialogOpen(true);
    };

    const handleDeleteConversation = async () => {
        if (!selectedChatId) return;
        setDeleteLoading(true);
        setDeleteError(null);
        try {
            await deleteConversation(selectedChatId);
            setDeleteDialogOpen(false);
        } catch (error: any) {
            setDeleteError(error?.message ?? "Failed to delete conversation");
        } finally {
            setDeleteLoading(false);
        }
    };

    return (
        <div className="flex h-screen">
            {/* Sidebar */}
            <SideBar
                chats={chatsState}
                selectedChatId={selectedChatId}
                setSelectedChatId={setSelectedChatId}
                onConversationCreated={async () => {
                    // Refresh the conversation list when a new chat is created
                    await refetch();
                }}
            />

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col bg-[rgb(var(--sidebar))]">
                <Navbar
                    name={selectedChat?.name}
                    avatar={selectedChat?.avatar ?? null}
                    isOnline={selectedChat?.isOnline}
                    lastSeen={selectedChat?.lastSeen ?? null}
                    canEdit={selectedChat?.friendId === null}
                    hasConversation={Boolean(selectedChat)}
                    onEditConversation={openRenameDialog}
                    onDeleteConversation={openDeleteDialog}
                />

                <div className="flex-1 flex flex-col p-6 pb-1 overflow-y-auto">
                    {selectedChat ? (
                        <MessagesList
                            messages={selectedChat.messages}
                            onEdit={handleEditStart}
                            onDelete={handleDelete}
                            onReact={handleReaction}
                        />
                    ) : (
                        <div className="flex-1 flex items-center justify-center text-[rgb(var(--muted-foreground))]">
                            <p className="text-lg">Select a chat to start messaging</p>
                        </div>
                    )}
                </div>

                {/* Message Input */}
                {selectedChat && typingParticipants.length > 0 && (
                    <div className="px-6 pb-2 text-sm text-[rgb(var(--muted-foreground))]">
                        <TypingIndicator
                            label={`${typingParticipants
                                .map((entry) => entry.userName || "Someone")
                                .join(", ")}${typingParticipants.length > 1 ? " are" : " is"} typing`}
                            avatarUrl={selectedChat.avatar}
                            fallbackInitial={(selectedChat.name || "").trim().charAt(0)?.toUpperCase() || "U"}
                        />
                    </div>
                )}
                {selectedChat && (
                    <MessagesInput
                        value={messageInput}
                        setValue={setMessageInput}
                        onSend={handleSend}
                        isEditing={!!editingMessageId}
                        cancelEdit={() => { setMessageInput(""); }}
                    />
                )}

                <RenameGroupDialog
                    open={renameDialogOpen}
                    onOpenChange={(open) => {
                        setRenameDialogOpen(open);
                        if (!open) {
                            setRenameError(null);
                            setRenameLoading(false);
                        }
                    }}
                    value={renameValue}
                    onChange={setRenameValue}
                    error={renameError}
                    loading={renameLoading}
                    onSubmit={handleRenameSubmit}
                />

                <DeleteConversationDialog
                    open={deleteDialogOpen}
                    onOpenChange={(open) => {
                        setDeleteDialogOpen(open);
                        if (!open) {
                            setDeleteError(null);
                            setDeleteLoading(false);
                        }
                    }}
                    error={deleteError}
                    loading={deleteLoading}
                    onConfirm={handleDeleteConversation}
                />
            </div>
        </div>
    );
}