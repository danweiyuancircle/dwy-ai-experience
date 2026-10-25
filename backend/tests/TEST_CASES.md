# Backend integration test inventory

Existing package-wide inventory: `../TEST_CASES.md`. Provider-specific inventory: `providers/TEST_CASES.md`.

## Email language integration (`test_auth_runtime.py`)

- Optional bounded `Accept-Language`: Chinese and Chinese variants select `zh`; missing/other/excluded ranges select `en`; over 512 characters is rejected before delivery.
- Registration and password-reset HTTP requests pass language through AuthRuntime and EapiEmailCodeSender into the Resend subject, HTML, and text payload; SDK delivery is captured without network calls.
- Changing language cannot bypass the same mailbox/purpose resend cooldown.
