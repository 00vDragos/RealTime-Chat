import { useState } from "react";
import { Button } from "@/components/ui/button";


export default function MessagesInput() {
	const [message, setMessage] = useState("");

	const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();

			// Submit the form
			const form = e.currentTarget.form;
			if (form) {
				form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
			}
		}
	};

	return (
		<form
			className="flex items-center gap-2 p-6 border-t bg-white"
			onSubmit={e => {
				e.preventDefault();
			}}
		>
			<textarea
				placeholder="Type your message..."
				value={message}
				onChange={e => setMessage(e.target.value)}
				onKeyDown={handleKeyDown}
				className="flex-1 text-md h-12 px-5 py-2 resize-none rounded-md border border-input bg-background shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 min-h-[3.5rem] max-h-40"
				rows={1}
			/>
			<Button type="submit" size="lg" className="h-10 px-8 text-md" disabled={!message.trim()}>
				Send
			</Button>
		</form>
	);
}
