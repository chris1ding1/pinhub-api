# PinHub API

## Roadmap

- [ ] Send mail. Amazon SES
- [ ] Amazon Transcribe

## PostgreSQL

```sql
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    avatar_path VARCHAR(255),
    bio TEXT,
    links JSONB DEFAULT jsonb_build_array(),
    email VARCHAR(255) NOT NULL UNIQUE,
    email_verified_at BIGINT,
    locale VARCHAR(24) NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    preferences JSONB DEFAULT jsonb_build_object(),
    deleted_at BIGINT,
    created_at BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM now())::BIGINT),
    updated_at BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM now())::BIGINT)
);
```

```sql
CREATE TABLE pins (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    content TEXT,
    url VARCHAR(255),
    audio_path VARCHAR(255),
    image_path VARCHAR(255),
    tags JSONB DEFAULT jsonb_build_array(),
    visibility SMALLINT NOT NULL,
    extra JSONB DEFAULT jsonb_build_object(),
    deleted_at BIGINT,
    created_at BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM now())::BIGINT),
    updated_at BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM now())::BIGINT),

    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE NO ACTION
);

CREATE INDEX idx_pins_user_id ON pins(user_id);
```

`uv run uvicorn app.main:app --reload`

`uv run ruff check`

`uv run ruff check --fix && uv run ruff format`

```console
uv run ruff check app/
uv run ruff format app/
```
