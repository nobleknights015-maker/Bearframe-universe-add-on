# Bearframe Bedrock — Visual & Rig Style Guide (v0.4.0)

## 1. Minecraft-Native Silhouette + Sci-Fi Detail Density

- **Texture Atlas Standard:** Every entity uses a **128×128 RGBA PNG atlas** partitioned into a **4×4 grid of 32×32 pixel-art tiles** (matching Infinity Sci-Fi texture density while remaining lightweight on Android 4 GB RAM).
- **Android 4 GB RAM Geometry Budget:** Maximum **60 cubes per entity**, no high-frequency particle spam, and lightweight Molang expressions inside two shared animation controllers (`controller.animation.bearframe.locomotion` and `controller.animation.bearframe.turret`).

## 2. Faction Visual Identity Rules (Lore Bible Rev 4.10)

### Bearframes
- **Chassis:** Player-scale articulated humanoid androids (`29.4px–33.1px`, grounded at `y=0`), clean ceramic/composite armor plates over dark graphite mechanical joints.
- **Signature Hardware (Mandatory):**
  - **Immutable glowing chest core display** recessed/bezeled on the upper torso front.
  - **Dual circular technological side-head display modules** mounted on the left and right sides of the head (strictly technological hardware — **NEVER** animal/bear ears).
- **Canonical Department Palettes:**
  - **Mira (Farfield):** Light cool armor + teal glow (`#5de6cf`) + gold/brass trim.
  - **Penney (Commons):** Warm ivory armor + rose/pink glow (`#ff9fc6`).
  - **Auren (Systems):** Cool slate/white armor + blue glow (`#74b9ff`).
  - **Sentinel (Watchtower):** Dark tactical armor + red glow (`#f04c56`).
  - **Atlas (Production/Maintenance/Combat):** Heavy industrial build + amber/gold glow (`#ffb347` / `#ffc145`).
  - **Vera (Visual Production):** Clean light armor + violet/magenta glow (`#e278ff`).

### Nullframe Directorate, Hollows & Hunters
- **Nullframe Directorate Officers:** Tall, crisp pale-silver & obsidian humanoid silhouettes with stark red visor slits and command shoulder pauldrons.
- **Hollows (`hollow_scout`, `hollow_breacher`):** Mass-produced industrial humanoid drones (no quadrupeds!) with stark utility armor, dark joints, and crimson optical sensors.
- **Nullframe Hunters:** Lean, predatory Watchtower-defector silhouette with high collar/cowl and crimson-edged Terminus Blade forearm mount.

### Echo Frames
- **Chassis:** Older-generation weathered humanoid frames (`27.1px–33.1px`) showing patchwork weld seams, muted amber/violet/cyan optics, and asymmetrical repairs.
- **Restrictions:** Never look like Minecraft zombies; never have Bearframe chest core displays or side-head tech modules.

### Ghost Grid Machinery
- **Strict Nonhumanoid Rule:** Every Ghost Grid entity is an ancient autonomous sci-fi machine (6-legged hexapod walker, tri-thruster hover drone, 3-strut defense turret, tracked salvage hauler, or 2.6-block heavy colossus guardian) with weathered slate/bronze plating, grounded moss accents, and cold cyan optics.
