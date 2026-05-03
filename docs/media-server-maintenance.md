# Media Server Maintenance

This note covers the Docker-based maintenance pattern for the media stack on Cirrus:

- Mylar
- Kavita
- Komga

It also records whether the current library layout works for all three.

## Current Cirrus Layout

The library root used by the media apps is:

- `/mnt/phoenix/media/comics`

Current app config roots:

- Mylar: `/mnt/phoenix/services/mylar`
- Kavita: `/mnt/phoenix/services/kavita`
- Komga: recommended `/mnt/phoenix/services/komga`

Current compose files:

- `/srv/compose/mylar3/docker-compose.yml`
- `/srv/compose/kavita/docker-compose.yml`
- Komga is not yet deployed, but the expected compose location should follow the same pattern

## Compatibility With The Current Library Layout

Yes, the current layout is compatible with all three programs if the library remains organized as:

- publisher folders at the top level
- series folders beneath publisher folders
- `.cbz` as the normal file format
- rooted `ComicInfo.xml` for metadata

Observed fit:

- Mylar: compatible as an import/management pipeline
- Kavita: compatible as a read-only library reader
- Komga: compatible as a reader/library manager when pointed at the same root

Important caveats:

- Mylar is the strictest about import and metadata expectations.
- Kavita and Komga are happier once the tree is already organized.
- Keep config/state on local Phoenix storage, not on a remote mount.

## Mylar Update

Mylar runs from Docker Compose at:

- `/srv/compose/mylar3/docker-compose.yml`

Update procedure:

To update every service in the compose project:

```bash
cd /srv/compose/mylar3
docker compose pull
docker compose up -d
```

To update only Mylar:

```bash
cd /srv/compose/mylar3
docker compose pull mylar3
docker compose up -d mylar3
```

Notes:

- Mylar uses `/mnt/phoenix/media/incoming/mylar-import` as the import basket.
- Mylar uses `/mnt/phoenix/media/comics` as its library target.
- After an update, verify the container comes back on `http://192.168.1.113:8090`.

## Kavita Update

Kavita runs from Docker Compose at:

- `/srv/compose/kavita/docker-compose.yml`

Update procedure:

To update every service in the compose project:

```bash
cd /srv/compose/kavita
docker compose pull
docker compose up -d
```

To update only Kavita:

```bash
cd /srv/compose/kavita
docker compose pull kavita
docker compose up -d kavita
```

Notes:

- The current library mount is read-only at `/mnt/phoenix/media/comics:/comics:ro`.
- Verify the UI at `http://192.168.1.113:5000` after the update.
- Kavita’s Docker docs support the standard `docker compose pull` and `docker compose up -d` pattern.

## Komga Install

Komga is not yet deployed on Cirrus, but the expected Docker layout is straightforward.

Recommended compose pattern:

```yaml
services:
  komga:
    image: gotson/komga
    container_name: komga
    user: "1000:1000"
    restart: unless-stopped
    ports:
      - "192.168.1.113:25600:25600"
    volumes:
      - /mnt/phoenix/services/komga:/config
      - /mnt/phoenix/media/comics:/data
```

Komga install steps:

1. Create `/mnt/phoenix/services/komga`.
2. Add the compose file under `/srv/compose/komga/docker-compose.yml`.
3. Start the container with `docker compose up -d`.
4. Open `http://192.168.1.113:25600`.
5. Add `/data` as the library root inside Komga.

Notes:

- Komga’s Docker docs recommend local bind mounts for `/config` and `/data`.
- The current Phoenix layout is suitable for that.

## Komga Update

Komga updates with the same container recreation pattern as the other Docker apps:

To update every service in the compose project:

```bash
cd /srv/compose/komga
docker compose pull
docker compose up -d
```

To update only Komga:

```bash
cd /srv/compose/komga
docker compose pull komga
docker compose up -d komga
```

## Pull Scope Rule

Use `docker compose pull` when you want the whole compose stack refreshed.

Use `docker compose pull <service>` when you want only one image refreshed.

In both cases, `docker compose up -d` is what recreates the container if the image changed.

## Practical Rule

If the library is already normalized into publisher/series folders with `.cbz` and rooted metadata, all three apps can consume it cleanly.

If the file is still raw or ambiguous:

- Mylar is the first stop for import handling.
- Kavita and Komga should wait until the file is normalized.
