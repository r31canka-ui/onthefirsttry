-- Trigram (not tsvector) GIN index: contact search needs to match partial
-- phone numbers and email fragments ("0692..." or "@gmail"), which
-- token-based tsvector search handles poorly. pg_trgm's similarity/ILIKE
-- support is the better fit for this use case.
CREATE INDEX contacts_search_trgm_idx ON contacts
  USING gin (
    (
      coalesce(first_name, '') || ' ' ||
      coalesce(last_name, '') || ' ' ||
      coalesce(email, '') || ' ' ||
      coalesce(phone, '')
    ) gin_trgm_ops
  );
