"use client";

import { FormEvent, useState } from "react";

import { requestSchoolMatches, type RankedSchool } from "../lib/api";

const DEFAULT_STATES = "NY, CA, IL";
const DEFAULT_GOALS = "BigLaw, Public Interest";

function parseList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function ScorePill({ score }: { score: number }) {
  return (
    <div className="rounded-full bg-slate-950 px-3 py-1 text-sm font-semibold text-white">
      {score.toFixed(2)}
    </div>
  );
}

function RankedSchoolCard({ school }: { school: RankedSchool }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-950">{school.name}</h3>
          <p className="mt-1 text-sm text-slate-600">
            {school.city}, {school.state} · School ID {school.school_id}
          </p>
        </div>
        <ScorePill score={school.match_score} />
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl bg-slate-50 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Classification</p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-slate-950 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
              {school.classification}
            </span>
            <span className="text-sm text-slate-600">Admissions fit: {school.admissions_fit.toFixed(1)}</span>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-slate-700">
            <div className="rounded-lg bg-white px-3 py-2">Geo {school.geographic_fit.toFixed(1)}</div>
            <div className="rounded-lg bg-white px-3 py-2">Career {school.career_fit.toFixed(1)}</div>
            <div className="rounded-lg bg-white px-3 py-2">Cost {school.cost_fit.toFixed(1)}</div>
            <div className="rounded-lg bg-white px-3 py-2">Score {school.match_score.toFixed(1)}</div>
          </div>
        </div>

        <div className="rounded-xl bg-amber-50 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-amber-900">Why it was recommended</p>
          <p className="mt-2 text-sm leading-6 text-amber-950">{school.explanation}</p>
          {school.matched_career_goals.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {school.matched_career_goals.map((goal) => (
                <span key={goal} className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-950">
                  {goal}
                </span>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </article>
  );
}

export default function HomePage() {
  const [gpa, setGpa] = useState("3.70");
  const [lsatScore, setLsatScore] = useState("168");
  const [preferredLocations, setPreferredLocations] = useState(DEFAULT_STATES);
  const [careerGoals, setCareerGoals] = useState(DEFAULT_GOALS);
  const [costSensitivity, setCostSensitivity] = useState("5");
  const [rankedSchools, setRankedSchools] = useState<RankedSchool[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const result = await requestSchoolMatches({
        gpa: Number(gpa),
        lsat_score: Number(lsatScore),
        preferred_states: parseList(preferredLocations),
        career_goals: parseList(careerGoals),
        cost_sensitivity: Number(costSensitivity),
      });
      setRankedSchools(result.ranked_schools);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to fetch ranked schools.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.18),_transparent_32%),radial-gradient(circle_at_top_right,_rgba(15,23,42,0.12),_transparent_28%),linear-gradient(180deg,_#fffdf7_0%,_#f8fafc_100%)] text-slate-900">
      <div className="mx-auto grid min-h-screen max-w-7xl gap-10 px-6 py-10 lg:grid-cols-[0.95fr_1.05fr] lg:px-10 lg:py-14">
        <section className="flex flex-col justify-between rounded-[2rem] border border-slate-200/80 bg-white/80 p-8 shadow-[0_20px_80px_rgba(15,23,42,0.08)] backdrop-blur">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-amber-700">Law School Match</p>
            <h1 className="mt-4 max-w-lg text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
              Rank law schools from admissions, location, career, and cost signals.
            </h1>
            <p className="mt-4 max-w-xl text-base leading-7 text-slate-600">
              Enter your GPA, LSAT, preferred locations, career goals, and cost sensitivity. The form sends a request to the
              FastAPI backend and renders the top 10 matches.
            </p>
          </div>

          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl bg-slate-950 p-4 text-white">
              <div className="text-xs uppercase tracking-[0.25em] text-slate-400">Inputs</div>
              <div className="mt-3 text-2xl font-semibold">5</div>
            </div>
            <div className="rounded-2xl bg-amber-400 p-4 text-slate-950">
              <div className="text-xs uppercase tracking-[0.25em] text-amber-950/70">API</div>
              <div className="mt-3 text-2xl font-semibold">FastAPI</div>
            </div>
            <div className="rounded-2xl bg-slate-100 p-4 text-slate-950">
              <div className="text-xs uppercase tracking-[0.25em] text-slate-500">Output</div>
              <div className="mt-3 text-2xl font-semibold">Top 10 matches</div>
            </div>
          </div>
        </section>

        <section className="space-y-6 rounded-[2rem] border border-slate-200 bg-slate-950 p-6 text-white shadow-[0_20px_80px_rgba(15,23,42,0.12)] sm:p-8">
          <form className="grid gap-5" onSubmit={handleSubmit}>
            <div className="grid gap-5 sm:grid-cols-2">
              <label className="grid gap-2">
                <span className="text-sm font-medium text-slate-200">GPA</span>
                <input
                  type="number"
                  min="0"
                  max="4"
                  step="0.01"
                  value={gpa}
                  onChange={(event) => setGpa(event.target.value)}
                  className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none ring-0 transition placeholder:text-slate-500 focus:border-amber-400"
                  placeholder="3.70"
                />
              </label>

              <label className="grid gap-2">
                <span className="text-sm font-medium text-slate-200">LSAT</span>
                <input
                  type="number"
                  min="120"
                  max="180"
                  step="1"
                  value={lsatScore}
                  onChange={(event) => setLsatScore(event.target.value)}
                  className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none ring-0 transition placeholder:text-slate-500 focus:border-amber-400"
                  placeholder="168"
                />
              </label>
            </div>

            <label className="grid gap-2">
              <span className="text-sm font-medium text-slate-200">Preferred locations</span>
              <input
                type="text"
                value={preferredLocations}
                onChange={(event) => setPreferredLocations(event.target.value)}
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none ring-0 transition placeholder:text-slate-500 focus:border-amber-400"
                placeholder="NY, CA, IL"
              />
              <span className="text-xs text-slate-400">Enter state abbreviations separated by commas.</span>
            </label>

            <label className="grid gap-2">
              <span className="text-sm font-medium text-slate-200">Career goals</span>
              <input
                type="text"
                value={careerGoals}
                onChange={(event) => setCareerGoals(event.target.value)}
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none ring-0 transition placeholder:text-slate-500 focus:border-amber-400"
                placeholder="biglaw, public interest"
              />
              <span className="text-xs text-slate-400">Use commas to list one or more goals.</span>
            </label>

            <label className="grid gap-2">
              <span className="text-sm font-medium text-slate-200">Cost sensitivity</span>
              <select
                value={costSensitivity}
                onChange={(event) => setCostSensitivity(event.target.value)}
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none ring-0 transition focus:border-amber-400"
              >
                <option value="1">1 - Least sensitive</option>
                <option value="2">2</option>
                  <option value="3">3</option>
                <option value="4">4</option>
                  <option value="5">5 - Balanced</option>
                  <option value="6">6</option>
                  <option value="7">7</option>
                  <option value="8">8</option>
                  <option value="9">9</option>
                  <option value="10">10 - Most sensitive</option>
              </select>
            </label>

            <button
              type="submit"
              disabled={isLoading}
              className="inline-flex items-center justify-center rounded-xl bg-amber-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? "Ranking schools..." : "Rank schools"}
            </button>
          </form>

          {errorMessage ? (
            <div className="rounded-2xl border border-red-400/40 bg-red-500/10 p-4 text-sm text-red-100">
              {errorMessage}
            </div>
          ) : null}

          <div className="space-y-4">
            <div className="flex items-end justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold text-white">Ranked schools</h2>
                <p className="mt-1 text-sm text-slate-300">Results returned from the FastAPI backend, capped at the top 10.</p>
              </div>
              <span className="text-sm text-slate-400">{rankedSchools.length} results</span>
            </div>

            {rankedSchools.length > 0 ? (
              <div className="grid gap-4">
                {rankedSchools.map((school) => (
                  <RankedSchoolCard key={school.school_id} school={school} />
                ))}
              </div>
            ) : (
              <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/50 p-6 text-sm leading-6 text-slate-300">
                Submit the form to see the top 10 ranked schools. The backend currently uses realistic sample data and a
                weighted scoring algorithm.
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
