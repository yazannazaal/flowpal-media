# لوحة المشتركين (Subscribers dashboard)

Internal page for Flowpal's tech team and management: every subscriber, its systems, contacts, the log of
issues / requests / changes / notes, and (phase 2) daily bot activity and health.
**No money here, ever:** no prices, payments, invoices, AI cost, tokens or margins (Yazan, 2026-11-13).

- Page: `subscribers/index.html` (one static file, Arabic RTL, `noindex`).
- Data: Supabase project `kltkjkraevxltmxfetng`, tables from `ops/subscribers/001-init.sql` in `flowpal-agency`.
- Access: Supabase Auth (email + password) **and** an active row in `subscriber_staff`. RLS gives `anon` nothing.
- Demo with fake data (no login, nothing saved): open the page with `?demo`, e.g. `.../subscribers/?demo`.

## Connect the page (once)

In `index.html`, set the anon (publishable) key:

```js
const SUPABASE_URL = "https://kltkjkraevxltmxfetng.supabase.co";
const SUPABASE_ANON_KEY = "PASTE_ANON_KEY_HERE";   // anon / publishable key ONLY
```

The anon key is public by design. **Never** put the `service_role` key or any other secret in this file:
the repo is public. Until the key is set, the page shows "اللوحة غير مربوطة بعد" and no data.

## Add a staff member (who can log in)

Two steps, both by the tech team (service key stays on the server / in `.env`, never in the page):

1. Allowlist row (SQL editor, or REST with the service key):
   ```sql
   insert into subscriber_staff (email, name, role) values ('person@example.com', 'الاسم', 'tech');
   -- role: 'admin' (can delete) or 'tech'
   ```
   The email must be lower case.
2. Auth user (no email confirmation needed):
   ```bash
   curl -X POST "$SUPABASE_URL/auth/v1/admin/users" \
     -H "apikey: $SUPABASE_SERVICE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
     -H "Content-Type: application/json" \
     -d '{"email":"person@example.com","password":"<temporary password>","email_confirm":true}'
   ```
   Send the temporary password privately; the person changes it on first login with "تغيير كلمة المرور".

**Remove access:** `update subscriber_staff set active = false where email = 'person@example.com';`
(effective at once, even if they are still logged in). Optionally delete the Auth user too.

If someone logs in but is not on the active list, the page says "حسابك غير مفعّل على اللوحة" and shows no data.

## Add a subscriber

SQL editor (or REST with the service key). `id` is a slug: lower case letters, digits and `-`.

```sql
insert into subscribers (id, name, sector, city, channels, status, start_date, golive_date,
                         contract_version, contacts, systems, links, health)
values (
  'new-client', 'اسم المشترك', 'clinic', 'رام الله',
  array['whatsapp'],                 -- instagram | messenger | whatsapp | web_chat
  'onboarding',                      -- onboarding | live | paused | ended
  date '2026-12-01', null,
  'v1',                              -- contract version LABEL only, never terms or amounts
  '[{"role":"owner","name":"...","channel":"whatsapp","value":"+970..."}]'::jsonb,
  '{"n8n":{"host":"<n8n host>","workflows":[{"id":"<workflow id>","name":"...","role":"AI agent"}]},
    "bot_db":"...","dashboard":"..."}'::jsonb,
  '{"dashboard":"https://..."}'::jsonb,
  'unknown'                          -- green | yellow | red | unknown
);
```

- Workflow ids under `systems.n8n.workflows` become links to `https://<host>/workflow/<id>` on the page.
- Any other key in `systems` (e.g. `bot_db`, `meta`, `dashboard`) is shown as a line of text.
- `links` values must be full `https://` URLs to be clickable.
- When the bot goes live: `update subscribers set status='live', golive_date=current_date where id='new-client';`

Notes (issues, requests, changes, notes) are added from the page itself by any staff member.
Deleting a subscriber or a note is admin-only (RLS).

## Daily activity (phase 2)

The chart reads `subscriber_metrics_daily` (last 30 days). Only n8n (service key) writes it.
While it is empty the page shows "لا بيانات بعد".

## Deploy

This repo's Pages deploy runs on pushes to the default branch only. Work on a branch, get هبة's test and
Asmaa's OK, then merge.
