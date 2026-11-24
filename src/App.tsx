import { useState } from 'react';
import {
  CheckSquare,
  Download,
  FileArchive,
  GitBranch,
  Layers,
  Package,
  ShieldCheck,
  Smartphone,
  Square,
  Terminal,
} from 'lucide-react';

interface CheckItem {
  id: string;
  label: string;
  detail: string;
}

interface Artifact {
  filename: string;
  subtitle: string;
  size: string;
  primary?: boolean;
  pack?: boolean;
  icon: typeof Package;
}

const ANDROID_CHECKLIST: CheckItem[] = [
  {
    id: 'import',
    label: '1. Import & Pack Icons',
    detail:
      'Open Bearframe_Bedrock_0.4.2.mcaddon from Android Files -> choose Minecraft -> confirm both Bearframe | Behavior and Bearframe | Resources import with custom icons.',
  },
  {
    id: 'content-log',
    label: '2. World Load & Content Log',
    detail:
      'Enable Settings -> Creator -> Content Log File & GUI, load a Survival world (Infinity Sci-Fi stacked below if used), and note any warnings.',
  },
  {
    id: 'bearframes',
    label: '3. Bearframes (All 6 Departments)',
    detail:
      'Inspect farfield_surveyor, atlas_rigger, atlas_vanguard, city_watch, city_steward, city_engineer, vera_artisan. Verify player-scale height, chest core display, and dual side-head tech modules (no animal ears).',
  },
  {
    id: 'directorate',
    label: '4. Nullframes, Hollows & Hunters',
    detail:
      'Confirm hollow_scout is humanoid (not a quadruped), inspect hollow_breacher & nullframe_hunter, and hail directorate_officer twice to verify warning -> hostile escalation.',
  },
  {
    id: 'echoes',
    label: '5. Echo Frames & Nonviolent Stabilization',
    detail:
      'Check ward_resident, barter 3 copper ingots with echo_drifter for a legacy_cell, and Sneak-interact echo_sentinel with copper/redstone/legacy cell to calm permanently.',
  },
  {
    id: 'ghost-grid',
    label: '6. Nonhumanoid Ghost Grid Machines',
    detail:
      'Verify grid_walker (6-legged hexapod), grid_watcher (hover drone), grid_turret (non-griefing cyan grid_bolt), grid_hauler (treads + crane), and grid_guardian (2.6-block heavy rig).',
  },
  {
    id: 'tools',
    label: '7. Field Scanner & Repair Wrench',
    detail:
      'Craft bearframe:field_scanner and bearframe:repair_wrench; scan each faction (Ghost Grid reports unverified) and Sneak-interact wrench + iron nugget on a damaged Bearframe or Echo.',
  },
  {
    id: 'city',
    label: '8. Expanded Orbital Bearframe City (60x8x23)',
    detail:
      'Visit bearframe:city_orbit via a Farfield Surveyor, tour all 6 department bays and 7 staff (including Atlas Rigger alloy reclamation & Vera Artisan), and return via arrival bay lodestone.',
  },
  {
    id: 'android-perf',
    label: '9. Android 4 GB RAM Performance',
    detail:
      'Explore Overworld biomes for 10-15 minutes; check FPS stability, capped sparse ambient spawns, and natural survival mining/crafting.',
  },
];

const ARTIFACTS: Artifact[] = [
  {
    filename: 'Bearframe_Bedrock_0.4.2.mcaddon',
    subtitle: 'All-in-One Android .mcaddon (folder-based Behavior + Resources)',
    size: '238 KB',
    primary: true,
    icon: Package,
  },
  {
    filename: 'Bearframe_Behavior_0.4.0.mcpack',
    subtitle: 'Archived 0.4.0 Behavior Pack',
    size: '73 KB',
    pack: true,
    icon: Layers,
  },
  {
    filename: 'Bearframe_Resources_0.4.0.mcpack',
    subtitle: 'Archived 0.4.0 Resource Pack',
    size: '106 KB',
    pack: true,
    icon: Layers,
  },
  {
    filename: 'Bearframe_Bedrock_Source_0.4.0.zip',
    subtitle: 'Archived 0.4.0 Source Snapshot',
    size: '476 KB',
    icon: FileArchive,
  },
  {
    filename: 'Bearframe_Bedrock.gitbundle',
    subtitle: 'Archived Gemini Git Bundle',
    size: '232 KB',
    icon: GitBranch,
  },
];

export default function App() {
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const [downloading, setDownloading] = useState<string | null>(null);
  const [lastSaved, setLastSaved] = useState<string | null>(null);

  const toggle = (id: string) =>
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }));

  const triggerDownload = async (filename: string) => {
    setDownloading(filename);
    try {
      const res = await fetch(`/api/download/${encodeURIComponent(filename)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const buffer = await res.arrayBuffer();
      const blob = new Blob([buffer], { type: 'application/octet-stream' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 10000);
      setLastSaved(filename);
    } catch {
      window.location.href = `/api/download/${encodeURIComponent(filename)}`;
    } finally {
      setDownloading(null);
    }
  };

  const doneCount = Object.values(checked).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <header className="border-b border-slate-800 pb-6">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="font-mono text-xs uppercase tracking-widest text-teal-400">
              Minecraft Bedrock Add-on · Android Import Build
            </span>
            <span className="font-mono text-xs text-slate-400">
              Frontier Recovery
            </span>
          </div>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
            Bearframe Universe — v0.4.2
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-slate-300">
            Download one file with both packs. This release adds dry terrain placement,
            a rebuilt Directorate checkpoint, and seven original Frontier roles.
          </p>
        </header>

        <section className="mt-6 rounded-xl border border-teal-500/30 bg-teal-950/20 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-teal-300">
            <Smartphone className="h-4 w-4" />
            How to Import Into Minecraft on Android
          </div>
          <ol className="mt-2 list-decimal space-y-1.5 pl-5 text-xs leading-relaxed text-slate-200">
            <li>
              Tap <strong>Bearframe_Bedrock_0.4.2.mcaddon</strong> below to
              save it to your phone&apos;s <strong>Downloads</strong> folder.
            </li>
            <li>
              Open your Android <strong>Files</strong> app (or{' '}
              <strong>CX File Explorer</strong> / <strong>ZArchiver</strong>)
              and go to <strong>Downloads</strong> — do <em>not</em> tap
              &ldquo;Open&rdquo; inside Chrome&apos;s bar if Chrome blocks
              unknown file types.
            </li>
            <li>
              If Android appended <code className="text-amber-300">.zip</code>{' '}
              to the end, rename it back to{' '}
              <code className="text-teal-300">
                Bearframe_Bedrock_0.4.2.mcaddon
              </code>
              , then tap it and choose <strong>Minecraft</strong> to import both
              packs automatically.
            </li>
          </ol>
        </section>

        <section className="mt-6">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              Minecraft Add-on Downloads
            </h2>
            {lastSaved && (
              <span className="font-mono text-xs text-emerald-400">
                Saved: {lastSaved}
              </span>
            )}
          </div>
          <div className="mt-3 space-y-3">
            {ARTIFACTS.map((item) => {
              const Icon = item.icon;
              const isBusy = downloading === item.filename;
              return (
                <button
                  key={item.filename}
                  type="button"
                  onClick={() => triggerDownload(item.filename)}
                  disabled={isBusy}
                  className={
                    item.primary
                      ? 'flex w-full items-center justify-between gap-4 rounded-xl border border-teal-500/70 bg-teal-950/45 p-4 text-left transition hover:border-teal-400 hover:bg-teal-950/70'
                      : item.pack
                        ? 'flex w-full items-center justify-between gap-4 rounded-xl border border-slate-700 bg-slate-900/75 p-4 text-left transition hover:border-teal-500/50 hover:bg-slate-900'
                        : 'flex w-full items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/50 p-4 text-left transition hover:border-slate-700 hover:bg-slate-900'
                  }
                >
                  <div className="flex items-start gap-3">
                    <Icon
                      className={
                        item.primary
                          ? 'mt-0.5 h-5 w-5 shrink-0 text-teal-400'
                          : item.pack
                            ? 'mt-0.5 h-5 w-5 shrink-0 text-sky-400'
                            : 'mt-0.5 h-5 w-5 shrink-0 text-slate-400'
                      }
                    />
                    <div>
                      <div className="font-mono text-sm font-semibold text-white">
                        {item.filename}
                      </div>
                      <div className="mt-0.5 text-xs text-slate-400">
                        {item.subtitle}
                      </div>
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <span className="font-mono text-xs text-slate-400">
                      {isBusy ? 'Saving...' : item.size}
                    </span>
                    <Download
                      className={
                        item.primary
                          ? 'h-4 w-4 text-teal-300'
                          : 'h-4 w-4 text-slate-300'
                      }
                    />
                  </div>
                </button>
              );
            })}
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Direct link fallback:{' '}
            <a
              href="/api/download/Bearframe_Bedrock_0.4.2.mcaddon"
              download="Bearframe_Bedrock_0.4.2.mcaddon"
              className="text-teal-400 underline hover:text-teal-300"
            >
              /api/download/Bearframe_Bedrock_0.4.2.mcaddon
            </a>
          </p>
        </section>

        <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-white">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            Verification (31 Automated Tests Passed)
          </div>
          <p className="mt-2 text-xs leading-relaxed text-slate-300">
            Bedrock Dedicated Server verified a dry naturally generated checkpoint,
            rejection of unsafe terrain, the repair and salvage sequence, and save reload.
            The Android import and client rendering checks are pending.
          </p>
        </section>

        <section className="mt-8">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              Android Bedrock In-Game Checklist
            </h2>
            <span className="font-mono text-xs text-slate-400">
              {doneCount} / {ANDROID_CHECKLIST.length} checked
            </span>
          </div>
          <div className="mt-3 space-y-2">
            {ANDROID_CHECKLIST.map((item) => {
              const isDone = !!checked[item.id];
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => toggle(item.id)}
                  className="flex w-full items-start gap-3 rounded-lg border border-slate-800 bg-slate-900/60 p-3.5 text-left transition hover:border-slate-700"
                >
                  {isDone ? (
                    <CheckSquare className="mt-0.5 h-4 w-4 shrink-0 text-teal-400" />
                  ) : (
                    <Square className="mt-0.5 h-4 w-4 shrink-0 text-slate-500" />
                  )}
                  <div>
                    <div
                      className={
                        isDone
                          ? 'text-sm font-medium text-slate-400 line-through'
                          : 'text-sm font-medium text-white'
                      }
                    >
                      {item.label}
                    </div>
                    <p className="mt-1 text-xs leading-relaxed text-slate-400">
                      {item.detail}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </section>

        <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-white">
            <Terminal className="h-4 w-4 text-slate-400" />
            Pushing Branch to GitHub (Optional)
          </div>
          <pre className="mt-2 overflow-x-auto rounded bg-slate-950 p-3 font-mono text-xs text-slate-300">
{`git fetch Bearframe_Bedrock.gitbundle gemini-dev:gemini-dev
git push origin gemini-dev --tags`}
          </pre>
        </section>
      </div>
    </div>
  );
}
