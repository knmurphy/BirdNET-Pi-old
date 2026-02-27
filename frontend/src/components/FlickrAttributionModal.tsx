/**
 * Flickr Attribution Modal Component
 * Displays photo attribution with blacklist option
 */

import type { FlickrImage } from '../types';
import './FlickrAttributionModal.css';

interface FlickrAttributionModalProps {
  isOpen: boolean;
  onClose: () => void;
  image: FlickrImage | null;
}

export function FlickrAttributionModal({
  isOpen,
  onClose,
  image,
}: FlickrAttributionModalProps) {
  if (!isOpen || !image) {
    return null;
  }

  const handleBlacklist = async () => {
    if (!image?.image_id) return;

    try {
      const response = await fetch('/api/flickr/blacklist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_id: image.image_id, reason: 'User blacklisted' }),
      });

      if (response.ok) {
        window.location.reload();
      } else {
        const error = await response.text();
        console.error('Failed to blacklist image:', error);
      }
    } catch (error) {
      console.error('Error blacklisting image:', error);
    }
  };

  return (
    <div className="flickr-modal-overlay" onClick={onClose}>
      <div
        className="flickr-modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="flickr-modal__close"
          onClick={onClose}
          aria-label="Close modal"
        >
          X
        </button>

        <div className="flickr-modal__header">
          <h3 className="flickr-modal__title">Photo Attribution</h3>
        </div>

        <div className="flickr-modal__body">
          {image.image_url && (
            <img
              src={image.image_url}
              alt={image.title || 'Flickr photo'}
              className="flickr-modal__image"
            />
          )}

          <div className="flickr-modal__info">
            {image.title && (
              <div className="flickr-modal__info-item">
                <span className="flickr-modal__label">Title:</span>
                <span className="flickr-modal__value">{image.title}</span>
              </div>
            )}

            {image.image_url && (
              <div className="flickr-modal__info-item">
                <span className="flickr-modal__label">Image link:</span>
                <a
                  href={image.image_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flickr-modal__link"
                >
                  {image.image_url}
                </a>
              </div>
            )}

            {image.author_url && (
              <div className="flickr-modal__info-item">
                <span className="flickr-modal__label">Author link:</span>
                <a
                  href={image.author_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flickr-modal__link"
                >
                  {image.author_url}
                </a>
              </div>
            )}

            {image.license_url && (
              <div className="flickr-modal__info-item">
                <span className="flickr-modal__label">License URL:</span>
                <a
                  href={image.license_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flickr-modal__link"
                >
                  {image.license_url}
                </a>
              </div>
            )}
          </div>
        </div>

        <div className="flickr-modal__footer">
          <button
            type="button"
            className="flickr-modal__blacklist"
            onClick={handleBlacklist}
          >
            Blacklist this image
          </button>
        </div>
      </div>
    </div>
  );
}
