'use client';

import React from 'react';
import { SourceMetadata } from '@/types';
import { BookOpen, Percent } from 'lucide-react';

interface SourceCardProps {
  sources: SourceMetadata[];
}

export const SourceCard: React.FC<SourceCardProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-200/80">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 mb-2">
        <BookOpen className="w-3.5 h-3.5" />
        Retrieved Document Sources ({sources.length}):
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {sources.map((src, idx) => (
          <div
            key={idx}
            className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs flex flex-col justify-between hover:bg-slate-100/70 transition"
          >
            <div className="font-semibold text-slate-800 flex items-center justify-between mb-1">
              <span className="truncate pr-2">{src.document_title}</span>
              {src.page_number && (
                <span className="text-[10px] px-1.5 py-0.5 bg-white border border-slate-300 rounded text-slate-600">
                  Page {src.page_number}
                </span>
              )}
            </div>
            <p className="text-slate-600 text-[11px] line-clamp-3 mb-1.5 italic bg-white p-1.5 rounded border border-slate-100">
              "{src.snippet}"
            </p>
            <div className="flex items-center justify-end text-[10px] text-blue-600 font-medium">
              <Percent className="w-3 h-3 mr-0.5" />
              Relevance: {Math.round(src.relevance_score * 100)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
