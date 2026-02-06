"use client";

import React from "react";
import { ImageExtraction } from "@/types";
import { getImageUrl } from "@/hooks/useAPI";
import {
    TrendingUp,
    TrendingDown,
    Minus,
    Maximize2,
    Minimize2,
    AlertTriangle,
    BarChart3,
    X,
} from "lucide-react";

interface InferenceDisplayProps {
    extraction: ImageExtraction;
    onClose?: () => void;
}

export default function InferenceDisplay({
    extraction,
    onClose,
}: InferenceDisplayProps) {
    const { ocr_data, inference, type, image_id, page_number } = extraction;

    const getTrendIcon = (trend: string | null) => {
        if (!trend) return <Minus className="w-4 h-4 text-slate-400" />;
        const t = trend.toLowerCase();
        if (t.includes("increas") || t.includes("up")) return <TrendingUp className="w-4 h-4 text-emerald-600" />;
        if (t.includes("decreas") || t.includes("down")) return <TrendingDown className="w-4 h-4 text-rose-600" />;
        return <Minus className="w-4 h-4 text-slate-400" />;
    };

    return (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden h-fit sticky top-6">
            {/* Header */}
            <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-white relative">
                <div>
                    <h3 className="text-lg font-bold text-slate-900 capitalize">
                        Analysis Details
                    </h3>
                    <p className="text-sm text-slate-500 flex items-center gap-2">
                        <span className="capitalize">{type.replace("_", " ")}</span>
                        <span className="w-1 h-1 rounded-full bg-slate-300" />
                        <span>Page {page_number}</span>
                    </p>
                </div>
                {onClose && (
                    <button
                        onClick={onClose}
                        className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}
            </div>

            <div className="p-6 space-y-8">
                {/* Image & Key Metrics Row */}
                <div className="grid grid-cols-1 gap-6">
                    <div className="bg-slate-50 rounded-xl border border-slate-100 p-4 flex items-center justify-center min-h-[200px]">
                        <img
                            src={getImageUrl(image_id)}
                            alt="Analyzed content"
                            className="max-h-[300px] w-auto object-contain mix-blend-multiply"
                        />
                    </div>

                    {inference ? (
                        <div className="space-y-6">
                            {/* Stats Grid */}
                            <div className="grid grid-cols-3 gap-3">
                                <div className="p-3 rounded-xl border border-slate-100 bg-white shadow-sm">
                                    <div className="flex items-center gap-2 mb-1.5">
                                        {getTrendIcon(inference.trend)}
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Trend</span>
                                    </div>
                                    <p className="font-semibold text-slate-900 text-sm capitalize">{inference.trend || "Neutral"}</p>
                                </div>
                                <div className="p-3 rounded-xl border border-slate-100 bg-white shadow-sm">
                                    <div className="flex items-center gap-2 mb-1.5">
                                        <Maximize2 className="w-3.5 h-3.5 text-slate-400" />
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Max</span>
                                    </div>
                                    <p className="font-semibold text-slate-900 text-sm truncate" title={inference.max_point?.value}>
                                        {inference.max_point?.value || "-"}
                                    </p>
                                </div>
                                <div className="p-3 rounded-xl border border-slate-100 bg-white shadow-sm">
                                    <div className="flex items-center gap-2 mb-1.5">
                                        <Minimize2 className="w-3.5 h-3.5 text-slate-400" />
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Min</span>
                                    </div>
                                    <p className="font-semibold text-slate-900 text-sm truncate" title={inference.min_point?.value}>
                                        {inference.min_point?.value || "-"}
                                    </p>
                                </div>
                            </div>

                            {/* Summary */}
                            <div>
                                <h4 className="text-sm font-bold text-slate-900 mb-3">Executive Summary</h4>
                                <div className="text-slate-600 text-sm leading-relaxed p-4 bg-slate-50/50 rounded-xl border border-slate-100/50">
                                    {inference.summary}
                                </div>
                            </div>

                            {/* Anomalies */}
                            {inference.anomalies.length > 0 && (
                                <div className="p-4 bg-amber-50/50 border border-amber-100 rounded-xl">
                                    <div className="flex items-center gap-2 mb-3">
                                        <AlertTriangle className="w-4 h-4 text-amber-600" />
                                        <h4 className="text-sm font-bold text-amber-900">Anomalies Detected</h4>
                                    </div>
                                    <ul className="space-y-2">
                                        {inference.anomalies.map((anomaly, idx) => (
                                            <li key={idx} className="text-xs text-amber-800 flex items-start gap-2">
                                                <span className="mt-1.5 w-1 h-1 rounded-full bg-amber-400 flex-shrink-0" />
                                                <span className="leading-relaxed">{anomaly}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="text-center py-12 text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                            <BarChart3 className="w-10 h-10 mx-auto mb-3 opacity-30" />
                            <p className="text-sm">No analysis data available</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
