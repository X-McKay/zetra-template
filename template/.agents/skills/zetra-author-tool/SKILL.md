---
name: zetra-author-tool
description: Use when adding or changing a Zetra agent tool, including its arguments, declared effect, failure behavior, or contract tests.
---

Read [current SDK boundaries](../../../docs/development.md). Inspect the factory's
registration and the tool's callers before choosing its contract.

Specify typed inputs, bounded outputs, resource scope, timeout/error behavior and
actual effect. Register the tool through the existing context and match the effect
to what the implementation does. For example, reading deployment history may fit
an approved `remote_read` integration; restarting pods is a remote write and is
not admitted by this starter. Do not describe a write as a read to pass admission.

Use synthetic local fixtures to test accepted inputs, invalid/out-of-scope inputs,
empty/malformed upstream results, failures and output limits. Test that rejected
inputs cannot invoke the real operation. Add selection and trajectory cases where
the model's decision to use the tool matters; direct function tests prove only the
function contract.

Prefer an existing approved transport and credential mechanism. Keep secrets out
of source, prompts and fixtures. When an upstream operation has ambiguous effects,
preserve uncertainty and use the supported reconciliation path; a timeout does not
establish that nothing happened. Report unsupported effects or missing integration
as concrete platform requirements.
