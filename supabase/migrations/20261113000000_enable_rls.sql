-- Enable Row Level Security on every table the bot uses.
--
-- STATUS: NOT APPLIED. Review before running it in the Supabase SQL editor.
--
-- Why: the tables hold supplier phone numbers, CNPJ and contact data. They were
-- created without RLS and the bot talks to them with the anon key, which is
-- public by design, so anyone holding the project URL and that key can read and
-- change every row.
--
-- Effect: no policy is created for the anon or authenticated roles, so both are
-- denied by default; their table privileges are revoked as well. The
-- service_role key bypasses RLS and keeps working.
--
-- Required before applying:
--   1. Set SUPABASE_KEY to the service_role key on the server (Render) and in the
--      Manager's local .env. Keep it server-side only: never in a browser, a
--      distributed build or the repository.
--   2. Apply this file during a quiet window and send one test message.
--
-- Rollback (restores the previous, insecure state):
--   alter table public.perguntas disable row level security;
--   alter table public.cadastros disable row level security;
--   alter table public.sessions  disable row level security;
--   grant select, insert, update, delete on public.perguntas, public.cadastros,
--     public.sessions to anon, authenticated;

begin;

alter table public.perguntas enable row level security;
alter table public.cadastros enable row level security;
alter table public.sessions  enable row level security;

revoke all on table public.perguntas from anon, authenticated;
revoke all on table public.cadastros from anon, authenticated;
revoke all on table public.sessions  from anon, authenticated;

commit;
