# Millionaire's Vault Cookie Requirements and Integration Notes

## Overview
To automate Millionaire's Vault donations on MyAnonamouse (MaM), the backend must mimic browser requests very closely. This requires sending both the `mam_id` and `uid` cookies from a valid browser session. The cookies used by seedbox services (like Prowlarr) are not sufficient for this endpoint. (All IDs and cookies in this doc are examples only.)

## Key Findings
- **mam_id (cookie):**
  - This is the session cookie from your browser. It changes frequently (often after each login or donation).
  - The backend must use the current browser `mam_id` for Millionaire's Vault donations. (e.g. `mam_id=EXAMPLE_MAMID`)
- **uid:**
  - This is a persistent user identifier cookie from your browser. It usually lasts for weeks (see its expiration in browser dev tools).
  - The `uid` does not change as often as `mam_id`. (e.g. `uid=EXAMPLE_UID`)
- **Seedbox mam_id:**
  - The `mam_id` used by your seedbox (for Prowlarr, etc.) is not valid for Millionaire's Vault donations.
  - For all other MaM automation, the seedbox `mam_id` is sufficient. (e.g. `mam_id=EXAMPLE_SEEDBOX_MAMID`)

## User Instructions
1. **How to Find Your Cookies:**
   - Log in to www.myanonamouse.net in your browser.
   - Use the provided MouseTrap bookmarklet (recommended):
     - **Chrome/Edge/Safari**: Drag the bookmarklet button to your bookmarks bar
     - **Firefox**: Right-click the bookmarklet button and select "Bookmark Link" (dragging may not work due to security restrictions)
   - Alternatively, manually extract cookies:
     - Open Dev Tools → Application/Storage tab → Cookies → `www.myanonamouse.net`.
     - Copy the values for both `mam_id` and `uid` (example: `mam_id=EXAMPLE_MAMID`, `uid=EXAMPLE_UID`).
2. **How to Use in Mousetrap:**
   - **Recommended:** Use the bookmarklet which automatically includes browser detection for proper headers
   - **Manual:** Paste cookie values as: `mam_id=yourvalue; uid=yourvalue; browser=firefox` (specify your browser)
   - **Legacy:** Just `mam_id=yourvalue; uid=yourvalue` (defaults to Chrome headers)
   - These are only required for Millionaire's Vault donations.
   - If not provided, Millionaire's Vault automation will not work, but other perks will.
3. **Important for Firefox Users:**
   - Always use the bookmarklet or manually specify `browser=firefox` to avoid session invalidation
   - Chrome headers with Firefox cookies will cause MAM to invalidate your session
   - Use right-click → "Bookmark Link" instead of dragging to save the bookmarklet

**Important for Firefox users:** The browser detection ensures MouseTrap sends Firefox-compatible headers when using Firefox cookies, preventing MAM from invalidating your session due to browser mismatch.

## Backend/Config/UI Design
- Add two optional fields to session config and UI:
  - `mam_id_cookie` (string): The browser's current `mam_id` cookie value. (example: `EXAMPLE_MAMID`)
  - `uid` (string): The browser's current `uid` cookie value.
- Backend logic:
  - If both are present, use them for Millionaire's Vault requests.
  - Otherwise, fall back to the seedbox's `mam_id` for other automation. (example: `EXAMPLE_SEEDBOX_MAMID`)

## Cookie Expiration and Maintenance
  - The `uid` cookie is long-lived (weeks), but the `mam_id` cookie may need to be refreshed more often. (example: `uid=EXAMPLE_UID`)
- Users may need to update these fields periodically, especially if they log out or the session expires.
- If a donation fails with a login error, update the cookies from your browser.

## Example curl Command for Testing
```
# Chrome headers
curl 'https://www.example.com/millionaires/donate.php' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' \
  -H 'Referer: https://www.example.com/millionaires/donate.php' \
  -H 'Origin: https://www.example.com' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: mam_id=EXAMPLE_MAMID; uid=EXAMPLE_UID' \
  --data 'Donation=100&time=EXAMPLE_TIMESTAMP&submit=Donate+Points'

# Firefox headers
curl 'https://www.example.com/millionaires/donate.php' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0' \
  -H 'Referer: https://www.example.com/millionaires/donate.php' \
  -H 'Origin: https://www.example.com' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: mam_id=EXAMPLE_MAMID; uid=EXAMPLE_UID' \
  --data 'Donation=100&time=EXAMPLE_TIMESTAMP&submit=Donate+Points'
```

## Future UI/Backend Enhancements
- Add optional fields for `mam_id_cookie` and `uid` in the UI, only required for Millionaire's Vault.
- Add user-facing documentation and tooltips in the UI.
- Consider a helper to check cookie validity or automate refresh if possible.

---

**Summary:**
- Millionaire's Vault automation requires both `mam_id` and `uid` from a browser session (example values only).
- These should be entered as optional fields in the config/UI.
- Users must update them periodically as sessions expire.
- All other MaM automation works with the seedbox's `mam_id` only.