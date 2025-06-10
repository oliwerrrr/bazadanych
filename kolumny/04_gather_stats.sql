-- =====================================================================
-- ZBIERANIE STATYSTYK DLA SCHEMATU HOGWARTS
-- =====================================================================
--
-- Ten skrypt aktualizuje statystyki optymalizatora dla wszystkich tabel
-- w schemacie COLUMNS_HOGWARD. Jest to kluczowy krok po załadowaniu
-- dużej ilości danych, aby zapewnić optymalną wydajność zapytań.
--
-- Uruchom go jako użytkownik z uprawnieniami do zarządzania statystykami
-- (np. SYSTEM lub sam użytkownik COLUMNS_HOGWARD, jeśli ma odpowiednie granty).
-- =====================================================================

SET SERVEROUTPUT ON;

PROMPT
PROMPT 🚀 Rozpoczynam zbieranie statystyk dla schematu COLUMNS_HOGWARD...
PROMPT

BEGIN
    DBMS_STATS.GATHER_SCHEMA_STATS(
        ownname => 'COLUMNS_HOGWARD',
        estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
        method_opt => 'FOR ALL COLUMNS SIZE AUTO',
        degree => DBMS_STATS.AUTO_DEGREE,
        cascade => TRUE
    );
    DBMS_OUTPUT.PUT_LINE('✅ Statystyki dla schematu COLUMNS_HOGWARD zostały pomyślnie zebrane.');
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('❌ Wystąpił błąd podczas zbierania statystyk:');
        DBMS_OUTPUT.PUT_LINE(SQLERRM);
END;
/

PROMPT
PROMPT =====================================================================
PROMPT                   ZAKOŃCZONO ZBIERANIE STATYSTYK
PROMPT =====================================================================
PROMPT
PROMPT 💡 Weryfikacja: Uruchom ponownie skrypt `03_verify_setup.sql`,
PROMPT    aby zobaczyć zaktualizowaną liczbę wierszy (NUM_ROWS).
PROMPT ===================================================================== 