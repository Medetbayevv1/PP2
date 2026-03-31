-- 1. Search contacts by pattern (name or phone)
CREATE OR REPLACE FUNCTION search_contacts(p TEXT)
RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT c.id, c.first_name, c.last_name, c.phone
        FROM phonebook c
        WHERE c.first_name ILIKE '%' || p || '%'
           OR c.last_name  ILIKE '%' || p || '%'
           OR c.phone      ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;


-- 2. Get contacts with pagination
CREATE OR REPLACE FUNCTION get_contacts_paged(lim INT, off INT)
RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT c.id, c.first_name, c.last_name, c.phone
        FROM phonebook c
        ORDER BY c.id
        LIMIT lim OFFSET off;
END;
$$ LANGUAGE plpgsql;