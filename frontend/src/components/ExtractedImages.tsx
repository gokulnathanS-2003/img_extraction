"use client";

import React, { useState } from "react";
import { ImageExtraction } from "@/types";
import { getImageUrl } from "@/hooks/useAPI";
import { Image as ImageIcon, BarChart3, LineChart, PieChart, Table, Eye, Filter } from "lucide-react";

interface ExtractedImagesProps {
    extractions: ImageExtraction[];
    onSelectImage: (extraction: ImageExtraction) => void;
    selectedId?: string;
}

const typeIcons: Record<string, React.ReactNode> = {
    bar_chart: <BarChart3 className="w-4 h-4" />,
    line_graph: <LineChart className="w-4 h-4" />,
    pie_chart: <PieChart className="w-4 h-4" />,
    table: <Table className="w-4 h-4" />,
    chart: <BarChart3 className="w-4 h-4" />,
    graph: <LineChart className="w-4 h-4" />,
    image: <ImageIcon className="w-4 h-4" />,
};

const typeColors: Record<string, string> = {
    bar_chart: "bg-blue-50 text-blue-600",
    line_graph: "bg-emerald-50 text-emerald-600",
    pie_chart: "bg-purple-50 text-purple-600",
    table: "bg-orange-50 text-orange-600",
    chart: "bg-blue-50 text-blue-600",
    graph: "bg-emerald-50 text-emerald-600",
    image: "bg-slate-50 text-slate-600",
};

export default function ExtractedImages({
    extractions,
    onSelectImage,
    selectedId,
}: ExtractedImagesProps) {
    const [filter, setFilter] = useState<string>("all");

    const chartExtractions = extractions.filter((e) => e.type !== "image");
    const filteredExtractions =
        filter === "all"
            ? extractions
            : filter === "charts"
                ? chartExtractions
                : extractions.filter((e) => e.type === "image");

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="text-lg font-bold text-slate-900">Extracted Content</h2>
                    <p className="text-slate-500 text-sm mt-1">
                        Found {chartExtractions.length} charts & {extractions.length - chartExtractions.length} images
                    </p>
                </div>

                {/* Filter */}
                <div className="flex gap-1 bg-slate-50 p-1 rounded-lg border border-slate-200">
                    {["all", "charts", "images"].map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`
                                px-3 py-1.5 rounded-md text-xs font-medium transition-all
                                ${filter === f
                                    ? "bg-white text-slate-900 shadow-sm"
                                    : "text-slate-500 hover:text-slate-700"
                                }
                            `}
                        >
                            {f.charAt(0).toUpperCase() + f.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* Grid */}
            <div className="p-6">
                {filteredExtractions.length === 0 ? (
                    <div className="text-center py-16 border-2 border-dashed border-slate-100 rounded-xl bg-slate-50/50">
                        <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mx-auto mb-3 shadow-sm border border-slate-100">
                            <ImageIcon className="w-5 h-5 text-slate-300" />
                        </div>
                        <p className="text-slate-900 font-medium text-sm">No images found</p>
                        <p className="text-slate-500 text-xs mt-1">Try uploading a different PDF</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                        {filteredExtractions.map((extraction) => (
                            <div
                                key={extraction.image_id}
                                onClick={() => onSelectImage(extraction)}
                                className={`
                                    group relative rounded-xl overflow-hidden border cursor-pointer
                                    transition-all duration-200
                                    ${selectedId === extraction.image_id
                                        ? "ring-2 ring-blue-600 border-transparent shadow-md"
                                        : "border-slate-200 hover:border-slate-300 hover:shadow-sm"
                                    }
                                `}
                            >
                                {/* Image Container */}
                                <div className="aspect-square bg-slate-50 relative border-b border-slate-100">
                                    <img
                                        src={getImageUrl(extraction.image_id)}
                                        alt={extraction.type}
                                        className="w-full h-full object-contain p-4 mix-blend-multiply"
                                        loading="lazy"
                                    />

                                    {/* Hover Overlay */}
                                    <div className="absolute inset-0 bg-slate-900/0 group-hover:bg-slate-900/10 transition-colors flex items-center justify-center group-hover:opacity-100">
                                        <div className="opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all duration-200 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-full shadow-sm">
                                            <span className="text-xs font-semibold text-slate-900 flex items-center gap-1.5">
                                                <Eye className="w-3.5 h-3.5" />
                                                View Analysis
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Info Footer */}
                                <div className="p-3 bg-white">
                                    <div className="flex items-center gap-2 mb-1">
                                        <div className={`p-1.5 rounded-md ${typeColors[extraction.type] || typeColors.image}`}>
                                            {typeIcons[extraction.type] || typeIcons.image}
                                        </div>
                                        <div className="min-w-0">
                                            <p className="text-xs font-semibold text-slate-900 capitalize truncate">
                                                {extraction.type.replace("_", " ")}
                                            </p>
                                            <p className="text-[10px] text-slate-500">
                                                Page {extraction.page_number}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Status Indicator */}
                                {extraction.inference && (
                                    <div className="absolute top-2 right-2 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-white shadow-sm" />
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
