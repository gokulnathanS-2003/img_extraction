import axios from "axios";
import { ProcessingStatus } from "@/types";

const API_BASE_URL = "http://localhost:8000/api/pdf";

export const uploadPDF = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await axios.post(`${API_BASE_URL}/upload`, formData);
    return response.data;
};

export const uploadImage = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    // Use the correct endpoint for images
    // Note: The backend router prefix is /api/image, but our base is /api/pdf in this file
    // We should probably adjust the base url handling
    const response = await axios.post(`http://localhost:8000/api/image/upload`, formData);
    return response.data;
};

export const getStatus = async (taskId: string) => {
    const response = await axios.get(`${API_BASE_URL}/status/${taskId}`);
    return response.data;
};

export const getImageUrl = (imageId: string) => {
    return `${API_BASE_URL}/images/${imageId}`;
};

export const pollStatus = async (
    taskId: string,
    onUpdate: (status: ProcessingStatus) => void,
    intervalMs = 2000
) => {
    const checkStatus = async () => {
        try {
            const status = await getStatus(taskId);
            onUpdate(status);

            if (status.status === "processing") {
                setTimeout(checkStatus, intervalMs);
            }
        } catch (error) {
            console.error("Polling error:", error);
            onUpdate({
                task_id: taskId,
                status: "failed",
                progress: 0,
                message: "Failed to connect to server",
            });
        }
    };

    checkStatus();
};
