CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN DEFAULT FALSE
);

-- Seed only if empty
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM tasks LIMIT 1) THEN
        INSERT INTO tasks (title, done) VALUES ('Learn SQL', FALSE);
        INSERT INTO tasks (title, done) VALUES ('Build CRUD API', TRUE);
        INSERT INTO tasks (title, done) VALUES ('Connect database', FALSE);
    END IF;
END $$;