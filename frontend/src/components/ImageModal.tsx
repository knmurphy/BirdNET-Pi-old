/**
 * Image Modal Component
 * Displays a larger version of an image with an obvious close button
 */

interface ImageModalProps {
	isOpen: boolean;
	onClose: () => void;
	imageUrl?: string;
	altText?: string;
}

export function ImageModal({ isOpen, onClose, imageUrl, altText }: ImageModalProps) {
	if (!isOpen || !imageUrl) {
		return null;
	}

	return (
		<div className="image-modal-overlay" onClick={onClose}>
			<div
				className="image-modal-content"
				onClick={(e) => e.stopPropagation()}
			>
				<button
					className="image-modal__close"
					onClick={onClose}
					aria-label="Close image modal"
				>
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
						<line x1="18" y1="6" x2="6" y2="18" />
						<line x1="6" y1="6" x2="18" y2="18" />
					</svg>
				</button>
				<img
					src={imageUrl}
					alt={altText}
					className="image-modal__image"
				/>
			</div>
		</div>
	);
}
