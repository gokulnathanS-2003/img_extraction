import React from "react";

interface LoadingSpinnerProps {
    size?: "sm" | "md" | "lg";
    progress?: number;
    message?: string;
}

export default function LoadingSpinner({
    size = "md",
    progress = 0,
    message,
}: LoadingSpinnerProps) {
    const sizeClasses = {
        sm: "w-5 h-5",
        md: "w-8 h-8",
        lg: "w-12 h-12",
    };

    return (
        <div className="flex flex-col items-center justify-center p-4">
            <div className={`relative ${sizeClasses[size]}`}>
                {/* Background circle */}
                <div className="absolute inset-0 rounded-full border-4 border-slate-100"></div>
                {/* Spinning circle */}
                <div className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>
            </div>

            {(message || progress > 0) && (
                <div className="mt-4 text-center">
                    {message && (
                        <p className="text-slate-600 font-medium text-sm mb-2">{message}</p>
                    )}
                    {progress > 0 && (
                        <div className="w-48 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-blue-600 transition-all duration-300 ease-out"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
