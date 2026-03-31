-- 1. Upsert: insert a contact, or update phone if name already exists
CREATE OR REPLACE PROCEDURE upsert_contact(p_first VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_first) THEN
        UPDATE phonebook SET phone = p_phone WHERE first_name = p_first;
    ELSE
        INSERT INTO phonebook (first_name, phone) VALUES (p_first, p_phone);
    END IF;
END;
$$;


-- 2. Bulk insert from a list; validates phone (must start with + and be 10-15 chars)
--    Returns invalid rows via a temp table
CREATE OR REPLACE PROCEDURE bulk_insert(p_data TEXT[][])
LANGUAGE plpgsql AS $$
DECLARE
    i       INT;
    p_name  TEXT;
    p_phone TEXT;
BEGIN
    -- Create temp table to collect invalid entries
    CREATE TEMP TABLE IF NOT EXISTS invalid_entries (
        first_name TEXT,
        phone      TEXT
    ) ON COMMIT DELETE ROWS;

    FOR i IN 1 .. array_length(p_data, 1) LOOP
        p_name  := p_data[i][1];
        p_phone := p_data[i][2];

        -- Validate: phone must start with + and be between 10 and 15 characters
        IF p_phone ~ '^\+[0-9]{9,14}$' THEN
            IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_name) THEN
                UPDATE phonebook SET phone = p_phone WHERE first_name = p_name;
            ELSE
                INSERT INTO phonebook (first_name, phone) VALUES (p_name, p_phone);
            END IF;
        ELSE
            INSERT INTO invalid_entries VALUES (p_name, p_phone);
        END IF;
    END LOOP;
END;
$$;


-- 3. Delete contact by first name or phone
CREATE OR REPLACE PROCEDURE delete_contact(p_value TEXT, p_type TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_type = 'name' THEN
        DELETE FROM phonebook WHERE first_name = p_value;
    ELSIF p_type = 'phone' THEN
        DELETE FROM phonebook WHERE phone = p_value;
    END IF;
END;
$$;