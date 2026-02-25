# CreateOS Computing Templates

Production-ready **Computing** templates for the [CreateOS Template Marketplace](https://createos.nodeops.network/templates?categories=Computing). Each template is focused, documented, and includes a one-click run script. License: MIT.

## Templates

| Template | Description |
|----------|-------------|
| [**Batch Compute Runner**](./batch-compute-runner) | Run CPU-bound batch jobs via REST API. Submit jobs, poll status, get results. Configurable workers and limits via env vars. |
| [**CPU Pipeline**](./cpu-pipeline) | Run multi-step CPU pipelines via API. Configure steps and work per step; get results in one request. |

## Quick start

1. Pick a template and open its folder.
2. Run: `./run.sh` (or see the template’s README).
3. Use the API examples in the README to submit work and fetch results.

## Publishing to CreateOS

Each template follows the [CreateOS publish guidelines](https://createos.nodeops.network):

- Clear README with setup and examples
- One-click deploy/run script (`run.sh`)
- MIT license
- Configuration via environment variables (no hardcoded secrets)

To publish:

1. Deploy the template as a project on CreateOS and confirm the build is stable.
2. Go to **My Templates → Publish Template**.
3. Select the project, set template name, upload a 1200×630px thumbnail (PNG/JPEG, max 5MB), and optionally add a demo video URL.

## Explore

Browse [CreateOS templates](https://createos.nodeops.network/templates) for more categories and examples.
