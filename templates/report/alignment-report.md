# Alignment Report

## Project

- **Reference:** `{{REFERENCE_VIDEO}}`
- **Candidate:** `{{CANDIDATE_VIDEO}}`
- **Fidelity level:** `{{PIXEL|VISUAL|STYLE}}`
- **Renderer / stack:** `{{HyperFrames|Remotion|CSS/SVG|Other}}`
- **Sampling interval:** `{{INTERVAL}}s`
- **Generated:** `{{DATE}}`

## Summary

<!-- Pass / fail / partial. If it fails, name the first failing timestamp. -->

Status: `{{PASS|FAIL|PARTIAL}}`

{{SUMMARY_PARAGRAPH}}

## Motion Profile Notes

<!-- Inspect motion-profile.json and note hard cuts, static segments, and mutations. -->

- Hard cuts: {{LIST}}
- Static segments: {{LIST}}
- Significant mutations: {{LIST}}

## Mismatches

| Timestamp | Type | Severity | Description | Status |
|----------:|------|----------|-------------|--------|
| `{{T}}s` | `{{TYPE}}` | [HIGH] high / [MED] medium / [LOW] low | {{DESCRIPTION}} | {{open|fixed|accepted}} |

## Acceptance Evidence

- [ ] Side-by-side contact sheets reviewed
- [ ] Component / region crops reviewed
- [ ] PSNR / SSIM logs attached (when applicable)
- [ ] Patch log updated with each verified fix
- [ ] Regression timestamps rechecked after the last fix

## Decisions

<!-- Which differences are accepted and why? Do not mark accepted without a reason. -->
