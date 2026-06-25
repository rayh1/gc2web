# Workspace Notes

- This workspace runs inside a dev container.
- When starting a local dev server for testing, bind it to `localhost` and use the forwarded host port rather than the container-internal address.
- If you launch something like `npm run dev`, verify which port it listens on, then test it through the forwarded port from the host/browser side.
- Do not assume that an internal browser or Playwright session can reach the container-only address directly.
