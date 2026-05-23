// Default image size for collection-mode image tools and rendered image hints.
//
// Historically this was 512x256, which made Omni image replies look fixed to a
// wide/short canvas and made missing tool arguments fall back to that shape.
// The tool executor now resolves size from explicit tool args first and falls
// back to a neutral square default.

export const COLLECTION_IMAGE_SIZE = '512x256';

const [w, h] = COLLECTION_IMAGE_SIZE.split('x').map(Number);
export const COLLECTION_IMAGE_WIDTH = w;
export const COLLECTION_IMAGE_HEIGHT = h;
