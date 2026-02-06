import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { FileText } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "PDF Chart Extractor | AI-Powered Analysis",
    description: "Extract and analyze charts, graphs, and tables from PDF documents using AI",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <div className="min-h-screen flex flex-col bg-slate-50">
                    {/* Header */}
                    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm backdrop-blur-md bg-white/80 supports-[backdrop-filter]:bg-white/60">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center flex-shrink-0 shadow-sm">
                                    <FileText className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h1 className="text-lg font-bold text-slate-900 leading-none">PDF Extractor</h1>
                                    <p className="text-[10px] font-medium text-slate-500 uppercase tracking-widest mt-1">AI Analysis</p>
                                </div>
                            </div>
                            <div className="hidden sm:block text-xs font-medium text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full">
                                v1.0.0
                            </div>
                        </div>
                    </header>

                    {/* Main content */}
                    <main className="flex-grow">
                        {children}
                    </main>
                </div>
            </body>
        </html>
    );
}
