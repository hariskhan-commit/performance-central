# Performance Central v25 Runbook

## Deployment

- Use blue/green with rolling updates.
- For Celery, use --pool solo for async tasks compatibility.

## Monitoring

- Health: /api/v1/healthz
- Version: /api/v1/version

## Key Rotation

- Run /admin/api_keys/<id>/rotate and verify grace period.

## Recovery

- MFA: Admin can re-enroll for users.
- Lost keys: Generate new via admin API.