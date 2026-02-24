const API_URL = import.meta.env.VITE_API_URL || 'https://isl-backend-4xfm.onrender.com';

export const predictVideo = async (videoBlob) => {
    const formData = new FormData();
    // Ensure the file has a .webm or .mp4 extension depending on recorder
    formData.append('file', videoBlob, 'recording.webm');

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Prediction failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};
