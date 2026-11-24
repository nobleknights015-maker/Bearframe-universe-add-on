import { useState } from 'react';
import {
  CheckSquare,
  Download,
  FileArchive,
  GitBranch,
  Package,
  ShieldCheck,
  Square,
  Terminal,
} from 'lucide-react';

interface CheckItem {
  id: string;
  label: string;
  detail: string;
}

const ANDROID_CHECKLIST: CheckItem[] = [
  {
    id: 'import',
    label: '1. Import & Pack Icons',
    detail:
      'Tap Bearframe_Bedrock_0.4.0.mcaddon on Android -> confirm both Bearframe | Behavior and Bearframe | Resources import with custom Bearframe icons.',
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

const DOWNLOADS = [
  {
    title: 'Bearframe_Bedrock_0.4.0.mcaddon',
    subtitle: 'Android Bedrock Installable Package (Behavior + Resource Packs)',
    href: '/downloads/Bearframe_Bedrock_0.4.0.mcaddon',
    size: '157 KB',
    primary: true,
    icon: Package,
  },
  {
    title: 'Bearframe_Bedrock_Source_0.4.0.zip',
    subtitle: 'Full Repository Source, Docs, Tests, Tools & .gitbundle',
    href: '/downloads/Bearframe_Bedrock_Source_0.4.0.zip',
    size: '471 KB',
    primary: false,
    icon: FileArchive,
  },
  {
    title: 'Bearframe_Bedrock.gitbundle',
    subtitle: 'Git Bundle (main 6f4fbb8 + gemini-dev 7739835 + tags)',
    href: '/downloads/Bearframe_Bedrock.gitbundle',
    size: '228 KB',
    primary: false,
    icon: GitBranch,
  },
];

export default function App() {
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  const toggle = (id: string) =>
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }));

  const doneCount = Object.values(checked).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <header className="border-b border-slate-800 pb-6">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="font-mono text-xs uppercase tracking-widest text-teal-400">
              Minecraft Bedrock Add-on · Release Portal
            </span>
            <span className="font-mono text-xs text-slate-400">
              branch: gemini-dev · commit 7739835
            </span>
          </div>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
            Bearframe Universe — v0.4.0
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-slate-300">
            Installable Android Bedrock build (4 GB RAM target). This utility
            page serves the real packaged{' '}
            <code className="text-teal-300">.mcaddon</code> and git deliverables
            directly from the repository workspace—no PC or paid server
            required.
          </p>
        </header>

        <section className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
            <div className="font-mono text-xs text-slate-400">Entities</div>
            <div className="mt-1 text-lg font-semibold text-white">19 + 1</div>
            <div className="text-xs text-slate-400">Living + bolt</div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
            <div className="font-mono text-xs text-slate-400">Structures</div>
            <div className="mt-1 text-lg font-semibold text-white">11</div>
            <div className="text-xs text-slate-400">10 surface + orbit</div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
            <div className="font-mono text-xs text-slate-400">Unit Tests</div>
            <div className="mt-1 text-lg font-semibold text-emerald-400">
              20 / 20
            </div>
            <div className="text-xs text-slate-400">Static passed</div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
            <div className="font-mono text-xs text-slate-400">Bedrock QA</div>
            <div className="mt-1 text-lg font-semibold text-amber-300">
              Pending
            </div>
            <div className="text-xs text-slate-400">Ready on Android</div>
          </div>
        </section>

        <section className="mt-8">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
            Release Artifacts
          </h2>
          <div className="mt-3 space-y-3">
            {DOWNLOADS.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.title}
                  href={item.href}
                  download={item.title}
                  className={
                    item.primary
                      ? 'flex items-center justify-between gap-4 rounded-xl border border-teal-500/60 bg-teal-950/40 p-4 transition hover:border-teal-400 hover:bg-teal-950/60'
                      : 'flex items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4 transition hover:border-slate-700 hover:bg-slate-900'
                  }
                >
                  <div className="flex items-start gap-3">
                    <Icon
                      className={
                        item.primary
                          ? 'mt-0.5 h-5 w-5 shrink-0 text-teal-400'
                          : 'mt-0.5 h-5 w-5 shrink-0 text-slate-400'
                      }
                    />
                    <div>
                      <div className="font-mono text-sm font-semibold text-white">
                        {item.title}
                      </div>
                      <div className="mt-0.5 text-xs text-slate-400">
                        {item.subtitle}
                      </div>
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <span className="font-mono text-xs text-slate-400">
                      {item.size}
                    </span>
                    <Download
                      className={
                        item.primary
                          ? 'h-4 w-4 text-teal-300'
                          : 'h-4 w-4 text-slate-300'
                      }
                    />
                  </div>
                </a>
              );
            })}
          </div>
        </section>

        <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-white">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            Static Validation Summary
          </div>
          <p className="mt-2 text-xs leading-relaxed text-slate-300">
            Verified in workspace: 20 entities, 6 items, 4 survival recipes, 4
            Android-capped spawn rules, 20 geometries (UV bounds, bone parents,
            &le;60 cubes/entity), 72 animations, 2 animation controllers, 11
            Bedrock NBT structures, all PNG headers/dimensions, JS syntax (
            <code className="text-slate-200">node --check</code>), and Lore
            Bible Rev 4.10 guardrails. Live in-game Bedrock verification awaits
            your Android test below.
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
