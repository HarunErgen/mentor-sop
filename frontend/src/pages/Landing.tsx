import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getUserJobs } from "../api/client";
import type { JobSummary } from "../types";

export default function Landing() {
  const { isAuthenticated, logout } = useAuth();
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <span className="text-xl font-semibold text-slate-900">
            MentorSOP
          </span>
          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              <Link
                to="/create"
                className="font-medium text-indigo-600 hover:text-indigo-500"
              >
                Dashboard
              </Link>
              <button
                onClick={logout}
                className="rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200"
              >
                Sign out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="font-medium text-slate-600 hover:text-slate-900"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </header>

      <main>
        <section className="px-4 py-20 text-center sm:py-28">
          <h1 className="mx-auto max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            AI-powered Statements of Purpose for graduate school
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
            Share your background and goals. We draft a tailored, compelling SoP
            that highlights your fit for your target program.
          </p>
          <div className="mt-10">
            <Link
              to="/create"
              className="inline-flex items-center rounded-lg bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700"
            >
              Create your SoP
            </Link>
          </div>
        </section>

        {isAuthenticated && <RecentReports />}

        <section className="border-t border-slate-200 bg-white px-4 py-16">
          <div className="mx-auto max-w-5xl">
            <h2 className="text-center text-2xl font-semibold text-slate-900">
              How it works
            </h2>
            <div className="mt-12 grid gap-10 sm:grid-cols-3">
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 text-indigo-600">
                  1
                </div>
                <h3 className="mt-4 font-medium text-slate-900">
                  Fill in your details
                </h3>
                <p className="mt-2 text-sm text-slate-600">
                  Target program, research interests, academic background, and
                  optional experience and preferences.
                </p>
              </div>
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 text-indigo-600">
                  2
                </div>
                <h3 className="mt-4 font-medium text-slate-900">
                  We draft your SoP
                </h3>
                <p className="mt-2 text-sm text-slate-600">
                  Our AI aligns your profile with the program and produces a
                  structured, school-specific draft.
                </p>
              </div>
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 text-indigo-600">
                  3
                </div>
                <h3 className="mt-4 font-medium text-slate-900">
                  Review and refine
                </h3>
                <p className="mt-2 text-sm text-slate-600">
                  Download or copy your SoP and edit as needed before
                  submitting.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 py-8 text-center text-sm text-slate-500">
        Start whenever you’re ready.
      </footer>
    </div>
  );
}

function RecentReports() {
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUserJobs()
      .then((res) => setJobs(res.jobs))
      .catch((err) => console.error("Failed to fetch jobs:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <section className="border-t border-slate-200 bg-slate-50/50 px-4 py-12">
        <div className="mx-auto max-w-5xl">
          <div className="h-8 w-48 animate-pulse rounded bg-slate-200"></div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 animate-pulse rounded-xl bg-white shadow-sm"></div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (jobs.length === 0) return null;

  return (
    <section className="border-t border-slate-200 bg-slate-50/50 px-4 py-16">
      <div className="mx-auto max-w-5xl">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900">Your Reports</h2>
          <Link to="/create" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
            Create New +
          </Link>
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job) => (
            <Link
              key={job.job_id}
              to={`/result/${job.job_id}`}
              className="group flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-indigo-300 hover:shadow-md"
            >
              <div>
                <div className="flex items-start justify-between">
                  <span className="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                    {job.degree_type}
                  </span>
                  <StatusBadge status={job.status} />
                </div>
                <h3 className="mt-3 font-semibold text-slate-900 group-hover:text-indigo-600">
                  {job.university_name}
                </h3>
                {job.status === "running" && (
                  <p className="mt-1 text-xs text-indigo-600 animate-pulse">
                    {job.current_step.replace(/_/g, " ")}...
                  </p>
                )}
              </div>
              <div className="mt-4 flex items-center justify-between text-xs text-slate-500">
                <span>{new Date(job.created_at).toLocaleDateString()}</span>
                <span className="font-medium text-indigo-600 opacity-0 transition-opacity group-hover:opacity-100">
                  View Report →
                </span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

function StatusBadge({ status }: { status: string }) {
  switch (status) {
    case "completed":
      return (
        <span className="inline-flex items-center gap-1 text-emerald-600">
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span className="text-xs font-medium">Ready</span>
        </span>
      );
    case "running":
    case "pending":
      return (
        <span className="inline-flex items-center gap-1 text-indigo-600">
          <div className="h-2 w-2 animate-bounce rounded-full bg-indigo-600"></div>
          <span className="text-xs font-medium">Generating</span>
        </span>
      );
    case "failed":
      return (
        <span className="inline-flex items-center gap-1 text-red-600">
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <span className="text-xs font-medium">Failed</span>
        </span>
      );
    default:
      return null;
  }
}
