"use client";

import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!url.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const trimmed = url.trim().replace(/\/$/, "");
      const parts = trimmed.split("/");
      const owner = parts[parts.length - 2];
      const repo = parts[parts.length - 1];

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/repos/generate-readme/${owner}/${repo}`,
        { method: "POST" }
      );

      if (!response.ok) throw new Error("Something went wrong");

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError("Failed to generate README. Check the URL and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-2xl">

        <div className="mb-10 text-center">
          <h1 className="text-4xl font-bold mb-3">README Generator</h1>
          <p className="text-gray-400 text-lg">
            Paste a public GitHub URL. We will rewrite your README using AI.
          </p>
        </div>

        <div className="flex gap-3">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900 disabled:cursor-not-allowed px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            {loading ? "Generating..." : "Generate"}
          </button>
        </div>

        {error && (
          <div className="mt-6 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-300">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-8 space-y-6">

            <div className="p-6 bg-gray-800 rounded-lg border border-gray-700">
              <h2 className="text-xl font-semibold mb-2">README Updated</h2>
              <p className="text-gray-400 mb-4">{result.message}</p>
              
              <a
                href={result.commit_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-green-700 hover:bg-green-600 px-5 py-2 rounded-lg font-medium transition-colors">
                View commit on GitHub
              </a>
            </div>

            <div className="p-6 bg-gray-800 rounded-lg border border-gray-700">
              <h2 className="text-xl font-semibold mb-2">DevOps Maturity</h2>
              <div className="flex items-center gap-4 mb-3">
                <span className="text-5xl font-bold text-blue-400">
                  {result.maturity_score}
                </span>
                <span className="text-gray-400">/ 100</span>
              </div>
              <p className="text-gray-300">{result.maturity_notes}</p>
            </div>

          </div>
        )}

      </div>
    </main>
  );
}