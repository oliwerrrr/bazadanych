-- =====================================================================
-- SKRYPT NAPRAWCZY: Nadanie uprawnienia ADVISOR
-- =====================================================================
--
-- Uruchom ten skrypt jako SYS lub SYSTEM połączony z XEPDB1,
-- aby nadać brakujące uprawnienie ADVISOR użytkownikowi COLUMNS_HOGWARD.
--
-- =====================================================================

PROMPT Nadaję uprawnienie 'ADVISOR' użytkownikowi COLUMNS_HOGWARD...
GRANT ADVISOR TO COLUMNS_HOGWARD;
PROMPT ✅ Uprawnienie nadane.

PROMPT
PROMPT Proszę uruchomić ponownie skrypt weryfikacyjny:
PROMPT @kolumny/verify_setup.sql
PROMPT aby potwierdzić, że wszystkie testy przechodzą pomyślnie. 