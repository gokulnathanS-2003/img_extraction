"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { FileUp, FileText, AlertCircle, CheckCircle2 } from "lucide-react";

interface PDFUploaderProps {
    onUpload: (file: File) => void;
    isUploading: boolean;
    error?: string | null;
}

export default function PDFUploader({ onUpload, isUploading, error }: PDFUploaderProps) {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const onDrop = useCallback(
        (acceptedFiles: File[]) => {
            const file = acceptedFiles[0];
            if (file && file.type === "application/pdf") {
                setSelectedFile(file);
                onUpload(file);
            }
        },
        [onUpload]
    );

    const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
        onDrop,
        accept: {
            "application/pdf": [".pdf"],
            "image/png": [".png"],
            "image/jpeg": [".jpg", ".jpeg"],
            "image/gif": [".gif"],
            "image/bmp": [".bmp"],
        },
        maxFiles: 1,
        disabled: isUploading,
        noClick: true, // We want to handle click on the button specifically
    });

    return (
        <div className="w-full">
            {/* Main Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 sm:p-10">
                <h2 className="text-xl font-bold text-slate-900 mb-6">Upload Files</h2>

                {/* Dropzone Area */}
                <div
                    {...getRootProps()}
                    className={`
                        relative border-2 border-dashed rounded-xl p-12 transition-all duration-200
                        flex flex-col items-center justify-center text-center
                        ${isDragActive
                            ? "border-blue-500 bg-blue-50/50"
                            : "border-slate-200 hover:border-slate-300 hover:bg-slate-50/50"
                        }
                        ${isUploading ? "opacity-50 cursor-not-allowed" : ""}
                        ${error ? "border-red-300 bg-red-50/10" : ""}
                    `}
                >
                    <input {...getInputProps()} />

                    {/* Icon */}
                    <div className="w-16 h-16 rounded-2xl bg-white shadow-sm border border-slate-100 flex items-center justify-center mb-6">
                        <FileUp className="w-8 h-8 text-slate-400" strokeWidth={1.5} />
                    </div>

                    {/* Main Instructions */}
                    <p className="text-slate-900 text-lg font-semibold mb-2">
                        Drag and Drop files here
                    </p>
                    <p className="text-slate-500 text-sm mb-8">
                        Files Supported: PDF, Images (PNG, JPG) • Maximum size: 5MB
                    </p>

                    {/* Action Button */}
                    <button
                        type="button"
                        onClick={open}
                        disabled={isUploading}
                        className="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-lg text-sm transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Choose File
                    </button>

                    {/* Selected File State */}
                    {selectedFile && !error && (
                        <div className="mt-8 w-full max-w-md bg-white rounded-lg border border-slate-200 p-4 shadow-sm flex items-center justify-between animate-in fade-in slide-in-from-bottom-2">
                            <div className="flex items-center gap-3 overflow-hidden">
                                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
                                    <FileText className="w-5 h-5 text-blue-600" />
                                </div>
                                <div className="min-w-0 text-left">
                                    <p className="text-sm font-semibold text-slate-900 truncate">
                                        {selectedFile.name}
                                    </p>
                                    <p className="text-xs text-slate-500">
                                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                                    </p>
                                </div>
                            </div>
                            {isUploading ? (
                                <div className="w-5 h-5 rounded-full border-2 border-slate-200 border-t-blue-600 animate-spin" />
                            ) : (
                                <CheckCircle2 className="w-5 h-5 text-green-500" />
                            )}
                        </div>
                    )}

                    {/* Error State */}
                    {error && (
                        <div className="mt-8 w-full max-w-md bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3 text-left">
                            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                            <div>
                                <h4 className="text-sm font-semibold text-red-900">Upload Failed</h4>
                                <p className="text-sm text-red-700 mt-1">{error}</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
