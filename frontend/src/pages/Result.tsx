import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getJobStatus, subscribeJobEvents, type JobEventSnapshot } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { SOPReport } from "../types";

const STEP_LABELS: Record<string, string> = {
  pending: "Waiting to start…",
  alignment: "Analyzing alignment…",
  alignment_summary: "Summarizing alignment…",
  positioning_brief: "Building positioning…",
  positioning_insight: "Refining insight…",
  architecture: "Structuring your SoP…",
  drafting_intro: "Drafting introduction…",
  drafting_why_program: "Drafting why program…",
  drafting_why_you: "Drafting why you…",
  drafting_closing: "Drafting closing…",
  combining: "Combining sections…",
  completed: "Done",
};

export default function Result() {
  const { jobId } = useParams<{ jobId: string }>();
  const { token } = useAuth();
  const [snapshot, setSnapshot] = useState<JobEventSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const apply = (data: JobEventSnapshot) => setSnapshot(data);

    const unsubscribe = subscribeJobEvents(
      jobId,
      apply,
      () => {
        setError("Connection lost. Falling back to polling.");
      },
      token
    );

    getJobStatus(jobId, token)
      .then(apply)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load job"));

    return unsubscribe;
  }, [jobId, token]);

  if (!jobId) {
    return (
      <div className="min-h-screen bg-slate-50 p-8 text-center">
        <p className="text-slate-600">Missing job ID.</p>
        <Link to="/create" className="mt-4 inline-block text-indigo-600 hover:underline">
          Create a new SoP
        </Link>
      </div>
    );
  }

  if (error && !snapshot) {
    return (
      <div className="min-h-screen bg-slate-50 p-8 text-center">
        <p className="text-red-600">{error}</p>
        <Link to="/create" className="mt-4 inline-block text-indigo-600 hover:underline">
          Create a new SoP
        </Link>
      </div>
    );
  }

  const status = snapshot?.status ?? "pending";
  const stepLabel = STEP_LABELS[snapshot?.current_step ?? ""] ?? snapshot?.current_step ?? "Loading…";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4">
          <Link to="/" className="text-lg font-semibold text-slate-900">
            MentorSOP
          </Link>
          <Link to="/create" className="text-sm text-indigo-600 hover:text-indigo-700">
            Create another
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8">
        {status === "failed" && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            <p className="font-medium">Generation failed</p>
            <p className="mt-1 text-sm">{snapshot?.error ?? "Unknown error"}</p>
            <Link to="/create" className="mt-3 inline-block text-sm font-medium text-red-700 hover:underline">
              Try again
            </Link>
          </div>
        )}

        {status !== "completed" && status !== "failed" && (
          <div className="mb-6 rounded-lg border border-slate-200 bg-white p-6 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
            <p className="mt-3 font-medium text-slate-700">{stepLabel}</p>
            {error && <p className="mt-1 text-sm text-amber-700">{error}</p>}
          </div>
        )}

        {status === "completed" && snapshot?.result && (
          <ResultContent result={snapshot.result} />
        )}
      </main>
    </div>
  );
}

function ResultContent({ result }: { result: SOPReport }) {
  const [copied, setCopied] = useState(false);
  const text = result.master_sop ?? result.sections?.join("\n\n") ?? "";

  const handleCopy = async () => {
    if (!text) return;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!text) return;
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "statement-of-purpose.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={handleCopy}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          {copied ? "Copied!" : "Copy to clipboard"}
        </button>
        <button
          type="button"
          onClick={handleDownload}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Download .txt
        </button>
      </div>

      {result.research_alignment_summary && (
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="text-lg font-medium text-slate-900">Research alignment summary</h2>
          {(result.research_alignment_summary.why_school_fits_you || result.research_alignment_summary.why_you_fit_lab) && (
            <div className="mt-2 space-y-2 text-sm text-slate-600">
              {result.research_alignment_summary.why_school_fits_you && (
                <p>{result.research_alignment_summary.why_school_fits_you}</p>
              )}
              {result.research_alignment_summary.why_you_fit_lab && (
                <p>{result.research_alignment_summary.why_you_fit_lab}</p>
              )}
            </div>
          )}
        </div>
      )}

      {result.strategic_positioning_insight && (
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="text-lg font-medium text-slate-900">Strategic positioning</h2>
          <div className="mt-2 space-y-2 text-sm text-slate-600">
            {result.strategic_positioning_insight.differentiation_angle && (
              <p><strong>Angle:</strong> {result.strategic_positioning_insight.differentiation_angle}</p>
            )}
            {result.strategic_positioning_insight.intellectual_identity && (
              <p><strong>Identity:</strong> {result.strategic_positioning_insight.intellectual_identity}</p>
            )}
            {result.strategic_positioning_insight.strength_profile && (
              <p><strong>Strengths:</strong> {result.strategic_positioning_insight.strength_profile}</p>
            )}
          </div>
        </div>
      )}

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-medium text-slate-900">Your Statement of Purpose</h2>
        <div className="mt-4 whitespace-pre-wrap text-slate-700">
          {text || "No content generated."}
        </div>
      </div>
    </div>
  );
}
