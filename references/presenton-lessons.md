# Presenton Case Notes

These notes capture the failure pattern from the Presenton reference-video task.
Use them as reminders, not as a universal template.

## What Went Wrong

- The first HyperFrames rebuild began before the reference had a strict 0.5s
  timeline.
- "Opening black + type changes" was added, but the actual 0.5s/1.0s/1.5s
  reference states were still not matched.
- A persistent horizontal neon-line background appeared in the remake even
  though the reference mostly used black star grain plus a weak bottom purple
  glow.
- Several subjects were rendered as far-view miniatures while the reference used
  large close-up hero subjects.
- Solid purple/pink flash frames appeared at timestamps where the reference had
  no such frames.
- The final "pixel-level" solution was not a hand-authored rebuild; it was a
  bit-exact source-stream version verified by hash, `cmp`, PSNR, and SSIM.

## Durable Rule

For reference-video work, never start with "can I recreate this in HyperFrames?"
Start with "what level of fidelity is being requested, and what evidence will
prove it?"
