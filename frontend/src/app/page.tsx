"use client";

import React, { useState, useCallback } from "react";
import PDFUploader from "@/components/PDFUploader";
import ExtractedImages from "@/components/ExtractedImages";
import InferenceDisplay from "@/components/InferenceDisplay";
import LoadingSpinner from "@/components/LoadingSpinner";
import { uploadPDF, uploadImage, pollStatus } from "@/hooks/useAPI";
import { ProcessingStatus, ImageExtraction, PDFExtractionResult } from "@/types";
import { ArrowLeft, FileText, Image as ImageIcon, Brain, CheckCircle2 } from "lucide-react";

type AppState = "upload" | "processing" | "results";

export default function Home() {
    const [appState, setAppState] = useState<AppState>("upload");
    const [status, setStatus] = useState<ProcessingStatus | null>(null);
    const [result, setResult] = useState<PDFExtractionResult | null>(null);
    const [selectedExtraction, setSelectedExtraction] = useState<ImageExtraction | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleUpload = useCallback(async (file: File) => {
        setError(null);
        setAppState("processing");

        try {
            // Check file type to determine upload method
            let uploadResponse;
            if (file.type === "application/pdf") {
                uploadResponse = await uploadPDF(file);
            } else {
                uploadResponse = await uploadImage(file);
            }

            // Poll for status
            await pollStatus(uploadResponse.task_id, (status) => {
                setStatus(status);

                if (status.status === "completed" && status.result) {
                    setResult(status.result);
                    setAppState("results");
                } else if (status.status === "failed") {
                    setError(status.message);
                    setAppState("upload");
                }
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : "Upload failed");
            setAppState("upload");
        }
    }, []);

    const handleSelectImage = useCallback((extraction: ImageExtraction) => {
        setSelectedExtraction(extraction);
    }, []);

    const handleReset = useCallback(() => {
        setAppState("upload");
        setStatus(null);
        setResult(null);
        setSelectedExtraction(null);
        setError(null);
    }, []);

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">

            {/* Upload State */}
            {appState === "upload" && (
                <div className="max-w-3xl mx-auto mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <PDFUploader
                        onUpload={handleUpload}
                        isUploading={false}
                        error={error}
                    />
                </div>
            )}

            {/* Processing State */}
            {appState === "processing" && (
                <div className="max-w-md mx-auto mt-20 animate-in fade-in zoom-in-95 duration-300">
                    <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
                        <div className="flex flex-col items-center text-center mb-8">
                            <LoadingSpinner
                                size="lg"
                                progress={status?.progress || 0}
                                message={status?.message || "Starting..."}
                            />
                        </div>

                        {/* Progress steps */}
                        <div className="space-y-4">
                            {[
                                { icon: FileText, label: "Extracting content", threshold: 10 },
                                { icon: ImageIcon, label: "Detecting visuals", threshold: 30 },
                                { icon: Brain, label: "AI Analysis", threshold: 60 },
                            ].map((step, idx) => (
                                <div
                                    key={idx}
                                    className={`
                                        flex items-center gap-3 p-3 rounded-xl transition-all duration-300
                                        ${(status?.progress || 0) >= step.threshold
                                            ? "bg-slate-900 text-white shadow-md"
                                            : "bg-slate-50 text-slate-400"
                                        }
                                    `}
                                >
                                    <step.icon className="w-5 h-5" />
                                    <span className="text-sm font-medium">{step.label}</span>
                                    {(status?.progress || 0) >= step.threshold && (
                                        <CheckCircle2 className="ml-auto w-4 h-4 text-emerald-400" />
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Results State */}
            {appState === "results" && result && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* Navigation Bar */}
                    <div className="flex items-center justify-between mb-8">
                        <button
                            onClick={handleReset}
                            className="group flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 hover:border-slate-300 transition-all text-slate-700"
                        >
                            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                            <span className="text-sm font-medium">Upload New</span>
                        </button>

                        <div className="flex items-center gap-4">
                            <div className="text-right hidden sm:block">
                                <h2 className="text-sm font-bold text-slate-900">{result.pdf_name}</h2>
                                <p className="text-xs text-slate-500">
                                    Processed {new Date(result.processed_at).toLocaleDateString()}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Main content grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                        {/* Left Column: Image Grid */}
                        <div className={`transition-all duration-500 ${selectedExtraction ? 'lg:col-span-8' : 'lg:col-span-12'}`}>
                            <ExtractedImages
                                extractions={result.extractions}
                                onSelectImage={handleSelectImage}
                                selectedId={selectedExtraction?.image_id}
                            />
                        </div>

                        {/* Right Column: Inference Panel - Only visible when selected */}
                        {selectedExtraction && (
                            <div className="lg:col-span-4 animate-in fade-in slide-in-from-right-4 duration-300">
                                <InferenceDisplay
                                    extraction={selectedExtraction}
                                    onClose={() => setSelectedExtraction(null)}
                                />
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
