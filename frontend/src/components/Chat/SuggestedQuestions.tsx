'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

const SUGGESTED = [
  "What is the minimum PCM aggregate for B.Tech CSE?",
  "What are the hostel curfew timings on weekends?",
  "When are the Autumn 2026 Mid-Semester Examinations?",
  "What is the fee refund policy if withdrawn before session starts?"
];

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({ onSelect }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 max-w-2xl mx-auto text-center">
      <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-4">
        <Sparkles className="w-6 h-6" />
      </div>
      <h3 className="text-xl font-bold text-slate-800 mb-2">
        How can CampusMind help you today?
      </h3>
      <p className="text-sm text-slate-500 mb-6 max-w-md">
        Ask anything about admissions, fees, hostel rules, academic calendars, exams, and college policies.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
        {SUGGESTED.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(q)}
            className="p-3 bg-white border border-slate-200 rounded-xl text-xs font-medium text-slate-700 hover:border-blue-500 hover:bg-blue-50/50 hover:text-blue-700 shadow-sm transition"
          >
            💬 {q}
          </button>
        ))}
      </div>
    </div>
  );
};
