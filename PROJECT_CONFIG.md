# Project Configuration

Edit this file when spinning this template up for a new OutSystems app or tenant.
Replace every `<placeholder>` with your actual values.

| Key | Value |
|---|---|
| **App Name** | `<YourAppName>` |
| **App Key** | `<your-app-key-uuid>` |
| **Tenant** | `<your-tenant>.outsystems.dev` |
| **Development Runtime URL** | `https://<your-tenant>-dev.outsystems.app/<YourAppName>` |

## How this is used

- `skills/odc-catchup/SKILL.md` — reads app name and key when calling `context_actions` / `context_entities`
- `skills/odc-ship/SKILL.md` — reads app key for `env_app` call after publish
- `hooks/session-start.sh` — reads tenant and app key to inject session context
- `README.md` — links here for the live app reference

## Finding your app key

In Claude Code, run:
```
List my OutSystems apps
```
The app key is the UUID shown next to your app name.
