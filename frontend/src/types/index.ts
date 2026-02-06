export interface ProcessingStatus {
    task_id: string;
    status: "processing" | "completed" | "failed";
    progress: number;
    message: string;
    result?: PDFExtractionResult;
}

export interface PDFExtractionResult {
    task_id: string;
    pdf_name: string;
    total_pages: number;
    processed_at: string;
    extractions: ImageExtraction[];
}

export interface ImageExtraction {
    image_id: string;
    page_number: number;
    bbox: number[];
    type: "chart" | "graph" | "table" | "image" | "bar_chart" | "line_graph" | "pie_chart";
    confidence: number;
    ocr_data?: {
        text: string;
        title?: string;
        x_axis?: string;
        y_axis?: string;
        legend?: string[];
    };
    inference?: {
        summary: string;
        trend: "increasing" | "decreasing" | "stable" | "fluctuating" | null;
        anomalies: string[];
        key_points: string[];
        max_point?: { label: string; value: string };
        min_point?: { label: string; value: string };
    };
}
